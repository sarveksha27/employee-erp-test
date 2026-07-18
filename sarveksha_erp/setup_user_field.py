import frappe

def execute():
    try:
        # Create Custom Field on User Doctype
        field_name = "User-custom_independent_company_flow"
        if not frappe.db.exists("Custom Field", field_name):
            doc = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "User",
                "fieldname": "custom_independent_company_flow",
                "label": "Enable Independent Company Flow",
                "fieldtype": "Check",
                "insert_after": "role_profile_name", # Usually under roles
                "module": "Vendor Management"
            })
            doc.insert(ignore_permissions=True)
            print("Successfully added Custom Field 'Enable Independent Company Flow' to User.")
        else:
            print("Custom Field already exists.")
            
        frappe.db.commit()
    except Exception as e:
        print("Error:", e)
