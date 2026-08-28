import os
import json
import frappe

def execute():
    # Path to company.json fixture
    fixture_path = frappe.get_app_path("sarveksha_erp", "fixtures", "company.json")
    if not os.path.exists(fixture_path):
        return
        
    with open(fixture_path, "r") as f:
        try:
            companies = json.load(f)
        except Exception:
            return
        
    for company in companies:
        name = company.get("name") or company.get("company_name")
        if not name:
            continue
            
        if not frappe.db.exists("Company", name):
            # Create a minimal company first to trigger Chart of Accounts generation
            # without default accounts validation failing
            doc = frappe.get_doc({
                "doctype": "Company",
                "company_name": name,
                "abbr": company.get("abbr"),
                "default_currency": company.get("default_currency") or "USD",
                "country": company.get("country") or "India",
                "create_chart_of_accounts_based_on": "Standard Template"
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
