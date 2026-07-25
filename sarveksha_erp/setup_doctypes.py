import frappe

def execute():
    # 1. Add "Independent Company" to Supplier
    if not frappe.db.exists("Custom Field", "Supplier-custom_independent_company"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Supplier",
            "fieldname": "custom_independent_company",
            "label": "Independent Company",
            "fieldtype": "Check",
            "insert_after": "supplier_type",
            "module": "Vendor Management"
        }).insert(ignore_permissions=True)
        print("Created Custom Field: Independent Company in Supplier")
    
    # 2. Create Vendor Payment Doctype
    if not frappe.db.exists("DocType", "Vendor Payment"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Vendor Payment",
            "module": "Vendor Management",
            "custom": 0,
            "naming_rule": "Expression",
            "autoname": "VP-.YYYY.-.#####",
            "fields": [
                {"fieldname": "vendor", "label": "Vendor", "fieldtype": "Link", "options": "Supplier", "reqd": 1, "in_list_view": 1},
                {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1},
                {"fieldname": "payment_date", "label": "Payment Date", "fieldtype": "Date", "reqd": 1, "in_list_view": 1},
                {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Pending\nCompleted\nFailed", "default": "Pending", "in_list_view": 1},
                {"fieldname": "reference_number", "label": "Reference Number", "fieldtype": "Data"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1, "delete": 0},
                {"role": "Accounts User", "read": 1, "write": 1, "create": 1, "delete": 0}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created DocType: Vendor Payment")
    
    frappe.db.commit()
