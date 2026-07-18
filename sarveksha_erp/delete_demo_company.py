import frappe

def execute():
    try:
        company_to_delete = "Demo Student ERP"
        new_default_company = "Sarveksha Realty and Inframine LLP"
        
        # 1. Update Global Defaults if the demo company is the default
        global_defaults = frappe.get_doc("Global Defaults")
        if global_defaults.default_company == company_to_delete:
            global_defaults.default_company = new_default_company
            global_defaults.save(ignore_permissions=True)
            print(f"Updated Global Default Company to: {new_default_company}")
            
        # 2. Update System Settings if necessary (sometimes default company is cached or set elsewhere, but Global Defaults is the main one)
        
        # 3. Check and delete User defaults linking to this company
        user_defaults = frappe.get_all("DefaultValue", filters={"defvalue": company_to_delete})
        for d in user_defaults:
            frappe.delete_doc("DefaultValue", d.name, ignore_permissions=True)
            print(f"Removed user default linking to {company_to_delete}")
            
        # 4. Attempt to delete the company
        if frappe.db.exists("Company", company_to_delete):
            # We use force=True to bypass some standard checks if it's a dummy company, but it will still fail if there are real transactions.
            # Assuming no transactions were made for this demo company.
            frappe.delete_doc("Company", company_to_delete, ignore_permissions=True, force=True)
            print(f"Successfully deleted company: {company_to_delete}")
        else:
            print(f"Company {company_to_delete} does not exist.")
            
        frappe.db.commit()
        
    except Exception as e:
        print("Error:", e)
        frappe.db.rollback()
