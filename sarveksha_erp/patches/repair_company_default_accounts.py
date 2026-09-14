import json

import frappe


ACCOUNT_FIELDS = (
    "default_bank_account",
    "default_cash_account",
    "default_receivable_account",
    "default_payable_account",
    "default_expense_account",
    "default_income_account",
    "default_discount_account",
    "default_operating_cost_account",
    "default_deferred_revenue_account",
    "default_deferred_expense_account",
    "default_advance_paid_account",
    "default_advance_received_account",
    "accumulated_depreciation_account",
    "depreciation_expense_account",
    "disposal_account",
    "capital_work_in_progress_account",
    "asset_received_but_not_billed",
    "expenses_added_to_stock_account",
    "expenses_added_to_stock_contra_account",
    "stock_received_but_not_billed",
    "stock_adjustment_account",
    "service_expense_account",
    "purchase_expense_account",
    "purchase_expense_contra_account",
    "write_off_account",
    "exchange_gain_loss_account",
    "unrealized_exchange_gain_loss_account",
    "unrealized_profit_loss_account",
    "round_off_account",
)


def _create_account(account_name, company):
    if frappe.db.exists("Account", {"name": account_name, "company": company}):
        return

    parent_account = frappe.db.get_value(
        "Account",
        {"company": company, "is_group": 1, "root_type": "Asset"},
        "name",
    ) or frappe.db.get_value(
        "Account", {"company": company, "is_group": 1}, "name"
    )
    if not parent_account:
        frappe.throw(f"Cannot repair {account_name}: no account group exists for {company}")

    account_title = account_name.rsplit(" - ", 1)[0]
    account = frappe.get_doc(
        {
            "doctype": "Account",
            "account_name": account_title,
            "company": company,
            "parent_account": parent_account,
            "account_currency": frappe.db.get_value(
                "Company", company, "default_currency"
            ),
            "is_group": 0,
        }
    )
    account.insert(ignore_permissions=True)


def execute():
    fixture_path = frappe.get_app_path("sarveksha_erp", "fixtures", "company.json")
    with open(fixture_path) as fixture_file:
        companies = json.load(fixture_file)

    for company_data in companies:
        company = company_data.get("name") or company_data.get("company_name")
        if not company or not frappe.db.exists("Company", company):
            continue

        for field in ACCOUNT_FIELDS:
            account_name = company_data.get(field)
            if account_name:
                _create_account(account_name, company)

    frappe.db.commit()