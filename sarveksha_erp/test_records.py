import frappe

def execute():
    try:
        # Create a test supplier
        if not frappe.db.exists("Supplier", "Test Supplier"):
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": "Test Supplier",
                "supplier_group": "All Supplier Groups",
                "custom_independent_company": 1
            })
            supplier.insert(ignore_permissions=True)
            print("Created Test Supplier with Independent Company checked!")
        
        # Create a test Vendor Payment
        payment = frappe.get_doc({
            "doctype": "Vendor Payment",
            "vendor": "Test Supplier",
            "amount": 500.0,
            "payment_date": "2026-07-18",
            "status": "Draft",
            "reference_number": "REF-12345"
        })
        payment.insert(ignore_permissions=True)
        print("Created Vendor Payment record:", payment.name)
        
    except Exception as e:
        print("Error:", e)
