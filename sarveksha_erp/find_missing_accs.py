import frappe
import json
import os

def run():
    accounts = [
        "default_cash_account", "default_bank_account", "default_payable_account", "default_receivable_account",
        "default_expense_account", "default_income_account", "default_inventory_account", "stock_received_but_not_billed",
        "stock_adjustment_account", "unrealized_exchange_gain_loss_account", "unrealized_profit_loss_account",
        "exchange_gain_loss_account", "default_advance_received_account", "default_advance_paid_account",
        "round_off_account", "default_deferred_revenue_account", "default_deferred_expense_account",
        "accumulated_depreciation_account", "depreciation_expense_account", "disposal_account"
    ]
    app_path = frappe.get_app_path("sarveksha_erp")
    fixture_path = os.path.join(app_path, "fixtures", "company.json")
    with open(fixture_path, "r") as f:
        fixtures = json.load(f)

    for c in fixtures:
        company_name = c.get("name")
        for acc_field in accounts:
            acc_name = c.get(acc_field)
            if acc_name:
                if not frappe.db.exists("Account", acc_name):
                    print(f"MISSING: Company={company_name}, Field={acc_field}, Account={acc_name}")
    print("Done")
