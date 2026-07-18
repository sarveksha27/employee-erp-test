import frappe

def execute():
    try:
        ws_sidebar = frappe.get_doc("Workspace Sidebar", "Vendor Management")
        ws_sidebar.header_icon = "accounting"
        ws_sidebar.standard = 1
        ws_sidebar.set("items", [])
        
        ws_sidebar.append("items", {
            "type": "Link",
            "label": "Vendor Payments",
            "link_type": "DocType",
            "link_to": "Vendor Payment",
            "icon": "accounting",
            "child": 0,
            "collapsible": 1
        })
        
        ws_sidebar.append("items", {
            "type": "Link",
            "label": "Vendors",
            "link_type": "DocType",
            "link_to": "Supplier",
            "icon": "users-round",
            "child": 0,
            "collapsible": 1
        })

        ws_sidebar.append("items", {
            "type": "Link",
            "label": "Company",
            "link_type": "DocType",
            "link_to": "Company",
            "icon": "home",
            "child": 0,
            "collapsible": 1
        })
        
        ws_sidebar.save(ignore_permissions=True)
        frappe.db.commit()
        print("Successfully updated Workspace Sidebar!")
        
    except Exception as e:
        print("Error:", e)
