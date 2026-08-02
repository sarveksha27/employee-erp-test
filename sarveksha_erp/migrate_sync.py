"""Bulletproof currency/company sync for sarveksha_erp fixture import.

Two layers of defence so `bench migrate` works on ANY database state
(fresh DB, existing DB with native-currency accounts, partially set-up DB, etc.):

1. `before_migrate` hook — runs BEFORE fixture import (pre_schema_updates).
   - Creates missing companies (triggers chart-of-accounts setup in USD).
   - Triggers chart-of-accounts setup for companies that exist but have no accounts.
   - Creates missing referenced accounts with the correct currency.
   - Syncs company + account currencies to match the fixture.

2. `company_before_validate` doc_event on Company — runs right before
   `Company.validate` → `validate_default_accounts` during fixture import
   (guarded by `frappe.flags.in_import`). This is the safety net: during
   fixture import the old Company row is deleted then re-created, but Account
   rows survive (they are separate doctypes). So this hook can always fix
   account currencies at the last second before validation runs.

Why this is needed: the fixture sets default_currency=USD for non-India
companies, but the "Standard" chart-of-accounts template creates accounts in
the company's country-native currency (XOF/GNF/BWP/SLL/etc.). ERPNext throws
"Default Cash Account currency must be same as company's default currency"
when any linked account's currency differs. Both hooks are idempotent.
"""
import json
import os

import frappe

# ---------------------------------------------------------------------------
# All account fields that ERPNext validates against the company's
# default_currency (Company.validate_default_accounts +
# validate_advance_account_currency) plus other *_account fields present in
# the company.json fixture. Keeping this broad ensures nothing is missed.
# ---------------------------------------------------------------------------
ACCOUNT_FIELDS = [
	"default_bank_account",
	"default_cash_account",
	"default_receivable_account",
	"default_payable_account",
	"default_expense_account",
	"default_income_account",
	"default_inventory_account",
	"stock_received_but_not_billed",
	"stock_adjustment_account",
	"write_off_account",
	"default_discount_account",
	"unrealized_profit_loss_account",
	"exchange_gain_loss_account",
	"unrealized_exchange_gain_loss_account",
	"round_off_account",
	"default_deferred_revenue_account",
	"default_deferred_expense_account",
	"accumulated_depreciation_account",
	"depreciation_expense_account",
	"disposal_account",
	"default_advance_received_account",
	"default_advance_paid_account",
	"default_operating_cost_account",
	"default_provisional_account",
	"asset_received_but_not_billed",
	"capital_work_in_progress_account",
]

# Maps fixture account-field names → ERPNext Account.account_type values,
# used when we need to create a missing account from scratch.
FIELD_TO_ACCOUNT_TYPE = {
	"default_cash_account": "Cash",
	"default_bank_account": "Bank",
	"default_receivable_account": "Receivable",
	"default_payable_account": "Payable",
	"default_expense_account": "Cost of Goods Sold",
	"default_income_account": "Income Account",
	"default_inventory_account": "Stock",
	"stock_received_but_not_billed": "Stock Received But Not Billed",
	"stock_adjustment_account": "Stock Adjustment",
	"round_off_account": "Round Off",
	"accumulated_depreciation_account": "Accumulated Depreciation",
	"depreciation_expense_account": "Depreciation",
	"asset_received_but_not_billed": "Asset Received But Not Billed",
	"capital_work_in_progress_account": "Capital Work in Progress",
	"write_off_account": "Expense Account",
	"exchange_gain_loss_account": "Expense Account",
	"unrealized_profit_loss_account": "Expense Account",
	"unrealized_exchange_gain_loss_account": "Expense Account",
	"disposal_account": "Expense Account",
	"default_deferred_revenue_account": "Income Account",
	"default_deferred_expense_account": "Expense Account",
	"default_advance_received_account": "Liability",
	"default_advance_paid_account": "Current Asset",
	"default_operating_cost_account": "Expense Account",
	"default_provisional_account": "Stock Received But Not Billed",
	"default_discount_account": "Expense Account",
}

# Maps account_type → root_type, used to find a parent account when creating
# a missing account from scratch.
ACCOUNT_TYPE_TO_ROOT_TYPE = {
	"Cash": "Asset",
	"Bank": "Asset",
	"Receivable": "Asset",
	"Current Asset": "Asset",
	"Stock": "Asset",
	"Stock Received But Not Billed": "Liability",
	"Stock Adjustment": "Expense",
	"Asset Received But Not Billed": "Asset",
	"Capital Work in Progress": "Asset",
	"Accumulated Depreciation": "Asset",
	"Fixed Asset": "Asset",
	"Payable": "Liability",
	"Liability": "Liability",
	"Current Liability": "Liability",
	"Cost of Goods Sold": "Expense",
	"Expense Account": "Expense",
	"Depreciation": "Expense",
	"Income Account": "Income",
	"Round Off": "Expense",
	"Equity": "Equity",
}


# ---------------------------------------------------------------------------
# Layer 1: before_migrate hook
# ---------------------------------------------------------------------------

def before_migrate():
	"""Ensure the DB is in a state where Company fixture import will succeed,
	regardless of the starting DB state."""
	fixture_path = os.path.join(
		frappe.get_app_path("sarveksha_erp"), "fixtures", "company.json"
	)
	if not os.path.exists(fixture_path):
		return

	with open(fixture_path) as f:
		companies = json.load(f)

	stats = {"companies_created": 0, "charts_setup": 0, "currencies_synced": 0,
	         "accounts_created": 0, "account_currencies_synced": 0, "warnings": []}

	for c in companies:
		name = c.get("name")
		currency = c.get("default_currency")
		if not name or not currency:
			continue

		# 1. Create the company if it doesn't exist yet. Creating with the
		#    correct default_currency makes ERPNext create the chart of
		#    accounts in that currency — no mismatch from the start.
		if not frappe.db.exists("Company", name):
			try:
				_create_company(c, stats)
			except Exception as e:
				stats["warnings"].append(f"Could not create company {name}: {e}")
				continue

		# 2. Sync company default_currency (bypasses validate_currency guard).
		if frappe.db.get_value("Company", name, "default_currency") != currency:
			frappe.db.set_value("Company", name, "default_currency", currency)
			frappe.clear_document_cache("Company", name)
			stats["currencies_synced"] += 1

		# 3. If the company exists but has no accounts, set up chart of accounts.
		if not frappe.db.exists("Account", {"company": name}):
			try:
				_setup_chart_of_accounts(name, c, stats)
			except Exception as e:
				stats["warnings"].append(f"Could not set up chart for {name}: {e}")

		# 4. For every referenced account: create if missing, sync currency if wrong.
		for field in ACCOUNT_FIELDS:
			acc = c.get(field)
			if not acc:
				continue
			if not frappe.db.exists("Account", acc):
				try:
					_create_missing_account(acc, name, currency, field, stats)
				except Exception as e:
					stats["warnings"].append(f"Could not create account {acc}: {e}")
			elif frappe.db.get_value("Account", acc, "account_currency") != currency:
				frappe.db.set_value("Account", acc, "account_currency", currency)
				frappe.clear_document_cache("Account", acc)
				stats["account_currencies_synced"] += 1

		# 5. Sync ALL accounts for this company to the company's currency.
		#    The fixture only references a subset of accounts (default_cash_account,
		#    default_expense_account, etc.), but the chart of accounts creates ~95
		#    accounts per company. If the company was originally created with a
		#    native currency (XOF/GNF/BWP/...), ALL of them have the wrong currency.
		#    Syncing every account ensures complete consistency so that any future
		#    operation (UI save, setting default_payable_account, etc.) won't fail.
		_sync_all_account_currencies(name, currency, stats)

	_summary = (
		f"companies_created={stats['companies_created']}, "
		f"charts_setup={stats['charts_setup']}, "
		f"currencies_synced={stats['currencies_synced']}, "
		f"accounts_created={stats['accounts_created']}, "
		f"account_currencies_synced={stats['account_currencies_synced']}"
	)
	print(f"[migrate_sync] {_summary}")
	if stats["warnings"]:
		print(f"[migrate_sync] {len(stats['warnings'])} warning(s):")
		for w in stats["warnings"]:
			print(f"  - {w}")

	# No explicit commit: pre_schema_updates runs inside an @atomic block
	# which commits before post_schema_updates (fixture import) starts.


def _create_company(c, stats):
	"""Create a company with essential fields from the fixture, letting
	ERPNext set up the chart of accounts, warehouses, cost centers, etc."""
	doc = frappe.new_doc("Company")
	doc.company_name = c.get("company_name") or c.get("name")
	doc.abbr = c.get("abbr")
	doc.country = c.get("country")
	doc.default_currency = c.get("default_currency")
	doc.chart_of_accounts = c.get("chart_of_accounts") or "Standard"
	doc.create_chart_of_accounts_based_on = (
		c.get("create_chart_of_accounts_based_on") or "Standard Template"
	)
	if c.get("domain"):
		doc.domain = c.get("domain")
	doc.insert(ignore_permissions=True)
	stats["companies_created"] += 1
	print(f"[migrate_sync] created company: {doc.name} ({doc.default_currency})")


def _setup_chart_of_accounts(name, c, stats):
	"""Trigger chart-of-accounts setup for an existing company that has no
	accounts yet (e.g. created without a chart)."""
	company_doc = frappe.get_doc("Company", name)
	# Ensure chart_of_accounts is set from the fixture.
	if not company_doc.chart_of_accounts:
		company_doc.chart_of_accounts = c.get("chart_of_accounts") or "Standard"
		company_doc.db_set("chart_of_accounts", company_doc.chart_of_accounts)
	frappe.local.flags.ignore_root_company_validation = True
	company_doc.create_default_accounts()
	company_doc.create_default_cost_center()
	stats["charts_setup"] += 1
	print(f"[migrate_sync] set up chart of accounts for: {name}")


def _create_missing_account(acc, company, currency, field, stats):
	"""Create a single missing account with the correct currency and a
	best-effort parent account."""
	# Account names in ERPNext are "Account Name - ABBR"; strip the abbr suffix.
	parts = acc.rsplit(" - ", 1)
	account_name = parts[0] if len(parts) > 1 else acc

	account_type = FIELD_TO_ACCOUNT_TYPE.get(field)
	root_type = ACCOUNT_TYPE_TO_ROOT_TYPE.get(account_type)

	# Try to find a suitable parent (a group account of the same root_type).
	parent = None
	if root_type:
		parent = frappe.db.get_value(
			"Account",
			{"company": company, "root_type": root_type, "is_group": 1},
			"name",
		)

	doc = frappe.new_doc("Account")
	doc.account_name = account_name
	doc.company = company
	doc.account_currency = currency
	doc.is_group = 0
	if account_type:
		doc.account_type = account_type
	if parent:
		doc.parent_account = parent
	doc.flags.ignore_mandatory = True
	doc.insert(ignore_permissions=True)
	stats["accounts_created"] += 1
	print(f"[migrate_sync] created account: {doc.name} ({currency})")


def _sync_all_account_currencies(company, currency, stats):
	"""Sync every Account belonging to *company* to *currency*.

	The fixture only references a handful of accounts (default_cash_account,
	default_expense_account, …), but the Standard chart-of-accounts template
	creates ~95 accounts per company.  If the company was originally created
	with a native currency (XOF/GNF/BWP/SLL/…), **all** of them have the wrong
	currency.  Syncing every account up-front means:
	  • validate_default_accounts never fails — even for fields that
	    on_update → set_default_accounts auto-populates (default_payable_account,
	    default_receivable_account) after the fixture import.
	  • Any later UI save of the Company won't hit a surprise currency error.
	"""
	wrong = frappe.get_all(
		"Account",
		filters={"company": company, "account_currency": ["!=", currency]},
		pluck="name",
	)
	for acc_name in wrong:
		frappe.db.set_value("Account", acc_name, "account_currency", currency)
		frappe.clear_document_cache("Account", acc_name)
	stats["account_currencies_synced"] += len(wrong)
	if wrong:
		print(f"[migrate_sync] synced {len(wrong)} account(s) for {company} → {currency}")


# ---------------------------------------------------------------------------
# Layer 2: before_validate doc_event on Company (safety net during import)
# ---------------------------------------------------------------------------

def company_before_validate(doc, method=None):
	"""Fix account currencies at the last second before Company.validate runs.

	During fixture import, the old Company row is deleted then re-created, but
	Account rows survive (they are separate doctypes). So this hook can always
	sync account currencies right before validate_default_accounts checks them.

	This syncs ALL accounts for the company (not just fixture-referenced ones)
	because on_update → set_default_accounts may auto-populate
	default_payable_account / default_receivable_account from the chart of
	accounts, and those accounts must also have the correct currency.

	Only active during fixture import (frappe.flags.in_import) to avoid
	interfering with normal manual Company edits.
	"""
	if not getattr(frappe.local, "flags", None) or not frappe.flags.in_import:
		return
	if not doc.default_currency:
		return

	# Sync ALL accounts for this company to the company's currency.
	wrong = frappe.get_all(
		"Account",
		filters={"company": doc.name, "account_currency": ["!=", doc.default_currency]},
		pluck="name",
	)
	for acc_name in wrong:
		frappe.db.set_value("Account", acc_name, "account_currency", doc.default_currency)
		frappe.clear_document_cache("Account", acc_name)

	if wrong:
		print(
			f"[migrate_sync] before_validate fixed {len(wrong)} account currency(ies) "
			f"for {doc.name}"
		)
