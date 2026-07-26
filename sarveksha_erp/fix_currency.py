import frappe
import json

def run():
    with open("apps/sarveksha_erp/sarveksha_erp/fixtures/company.json", "r") as f:
        fixtures = json.load(f)
    
    for c in fixtures:
        company_name = c.get("name")
        comp_currency = c.get("default_currency")
        cash_acc = c.get("default_cash_account")
        
        if cash_acc:
            if frappe.db.exists("Account", cash_acc):
                acc_currency = frappe.db.get_value("Account", cash_acc, "account_currency")
                if acc_currency != comp_currency:
                    print(f"Mismatch for {company_name}: fixture comp_currency={comp_currency}, db acc_currency={acc_currency}")
                    frappe.db.set_value("Account", cash_acc, "account_currency", comp_currency)
                    print(f"Fixed Account {cash_acc} to {comp_currency}")
            else:
                print(f"Account {cash_acc} does not exist in DB yet.")
    frappe.db.commit()
