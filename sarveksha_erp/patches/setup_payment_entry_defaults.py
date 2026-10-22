# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def execute():
    """
    Setup default bank accounts, mode of payment accounts, and default print formats
    for Payment Entry across all active companies to ensure zero missing account errors.
    """
    setup_company_bank_accounts_and_modes()
    setup_payment_entry_properties()


def setup_company_bank_accounts_and_modes():
    """Ensure every company has default Bank and Cash accounts, and Mode of Payment Account mappings."""
    companies = frappe.get_all("Company", fields=["name", "abbr", "default_currency", "default_bank_account", "default_cash_account"])

    # Cache resolved accounts per company to avoid repeated DB loads
    company_accounts = {}  # {company_name: {"bank": ..., "cash": ...}}

    for c in companies:
        cash_acc = c.default_cash_account
        bank_acc = c.default_bank_account
        curr = c.default_currency or "INR"
        updates = {}

        # 1. Ensure Default Cash Account
        if not cash_acc or not frappe.db.exists("Account", cash_acc):
            cash_acc = frappe.db.get_value("Account", {"company": c.name, "account_type": "Cash", "is_group": 0}, "name")
            if cash_acc:
                updates["default_cash_account"] = cash_acc

        # 2. Ensure Default Bank Account
        if bank_acc and frappe.db.exists("Account", bank_acc):
            acc_curr = frappe.db.get_value("Account", bank_acc, "account_currency")
            if acc_curr and acc_curr != curr:
                bank_acc = None  # currency mismatch — look for a better one

        if not bank_acc:
            bank_acc = frappe.db.get_value(
                "Account",
                {"company": c.name, "account_type": "Bank", "is_group": 0, "account_currency": curr},
                "name"
            )
            if not bank_acc:
                bank_acc = frappe.db.get_value(
                    "Account",
                    {"company": c.name, "account_type": "Bank", "is_group": 0},
                    "name"
                )
                if bank_acc:
                    frappe.db.set_value("Account", bank_acc, "account_currency", curr)

            if not bank_acc:
                parent_bank = f"Bank Accounts - {c.abbr}"
                if not frappe.db.exists("Account", parent_bank):
                    parent_bank = f"Current Assets - {c.abbr}"
                if not frappe.db.exists("Account", parent_bank):
                    parent_bank = frappe.db.get_value(
                        "Account", {"company": c.name, "is_group": 1, "root_type": "Asset"}, "name"
                    )

                if parent_bank:
                    new_acc = frappe.new_doc("Account")
                    new_acc.account_name = "Primary Bank Account"
                    new_acc.company = c.name
                    new_acc.parent_account = parent_bank
                    new_acc.account_type = "Bank"
                    new_acc.is_group = 0
                    new_acc.account_currency = curr
                    new_acc.flags.ignore_permissions = True
                    new_acc.insert()
                    bank_acc = new_acc.name

            if bank_acc:
                updates["default_bank_account"] = bank_acc

        # Use frappe.db.set_value to bypass link validation (safe during pre_model_sync).
        # company_doc.save() would validate ALL link fields (cost centers, etc.) which
        # may not exist yet at this point in the migration, causing LinkValidationError.
        if updates:
            frappe.db.set_value("Company", c.name, updates, update_modified=False)

        company_accounts[c.name] = {
            "bank": updates.get("default_bank_account", c.default_bank_account),
            "cash": updates.get("default_cash_account", c.default_cash_account),
        }

    # 3. Populate Mode of Payment Account for all modes
    modes = frappe.get_all("Mode of Payment", fields=["name", "type"])
    for m in modes:
        mode_doc = frappe.get_doc("Mode of Payment", m.name)
        mode_modified = False

        for c in companies:
            accs = company_accounts.get(c.name, {})
            target_account = accs.get("cash") if m.type == "Cash" else accs.get("bank")
            if not target_account:
                continue

            existing_row = next((row for row in mode_doc.accounts if row.company == c.name), None)
            if existing_row:
                if not existing_row.default_account:
                    existing_row.default_account = target_account
                    mode_modified = True
            else:
                mode_doc.append("accounts", {
                    "company": c.name,
                    "default_account": target_account,
                })
                mode_modified = True

        if mode_modified:
            mode_doc.flags.ignore_permissions = True
            mode_doc.flags.ignore_validate_links = True
            mode_doc.save()

    frappe.db.commit()


def setup_payment_entry_properties():
    """Set default print format on Payment Entry to Payment Receipt Proof."""
    try:
        make_property_setter(
            "Payment Entry",
            "",
            "default_print_format",
            "Payment Receipt Proof",
            "Data",
            for_doctype=True,
            validate_fields_for_doctype=False,
        )
    except Exception:
        pass
    frappe.db.commit()
