import frappe

def execute():
    try:
        # Check if the column exists in the database
        columns = frappe.db.sql("DESC `tabSupplier`", as_dict=True)
        col_names = [c.get('Field') for c in columns]
        
        if "custom_independent_company" in col_names:
            print("SUCCESS: `custom_independent_company` exists in the database table `tabSupplier`!")
        else:
            print("ERROR: `custom_independent_company` is MISSING from `tabSupplier`!")
            
        # Also check custom field doc
        if frappe.db.exists("Custom Field", "Supplier-custom_independent_company"):
            print("SUCCESS: `Supplier-custom_independent_company` Custom Field document exists!")
        else:
            print("ERROR: Custom Field document is missing!")
            
    except Exception as e:
        print("Error:", e)
