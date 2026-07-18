import frappe

def execute():
    # Insert shortcuts directly into the Home workspace
    try:
        home = frappe.get_doc("Workspace", "Home")
        
        # Add Vendor Payment
        home.append("shortcuts", {
            "type": "DocType",
            "link_to": "Vendor Payment",
            "label": "Vendor Payments",
            "color": "green",
            "format": "{} Open",
            "stats_filter": "[]",
            "icon": "payment"
        })
        
        # Add Supplier
        home.append("shortcuts", {
            "type": "DocType",
            "link_to": "Supplier",
            "label": "Vendors",
            "color": "blue",
            "icon": "users"
        })
        
        home.save(ignore_permissions=True)
        frappe.db.commit()
        print("Successfully added shortcuts to Home workspace!")
    except Exception as e:
        print("Error:", e)
