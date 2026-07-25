import frappe

def execute():
    try:
        company = frappe.get_doc("Company", "Demo Student ERP")
        print("Company details:")
        print(f"Name: {company.name}")
        print(f"Creation: {company.creation}")
        print(f"Owner: {company.owner}")
        
        # Check global defaults
        default_company = frappe.db.get_single_value("Global Defaults", "default_company")
        print(f"Global Default Company: {default_company}")
        
    except Exception as e:
        print("Error:", e)
