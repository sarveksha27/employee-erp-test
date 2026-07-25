import frappe

def execute():
    try:
        # Create Workspace Sidebar for Vendor Management
        if not frappe.db.exists("Workspace Sidebar", "Vendor Management"):
            ws_sidebar = frappe.get_doc({
                "doctype": "Workspace Sidebar",
                "title": "Vendor Management",
                "name": "Vendor Management",
                "module": "Vendor Management",
                "header_icon": "users", # Standard Frappe v16 icon
                "items": [
                    {
                        "type": "Link",
                        "label": "Vendor Management Dashboard",
                        "link_type": "Dashboard",
                        "link_to": "Vendor Management",
                        "icon": "chart",
                        "child": 0,
                        "collapsible": 1
                    },
                    {
                        "type": "Link",
                        "label": "Vendor Payments",
                        "link_type": "DocType",
                        "link_to": "Vendor Payment",
                        "icon": "accounting",
                        "child": 0,
                        "collapsible": 1
                    },
                    {
                        "type": "Link",
                        "label": "Vendors",
                        "link_type": "DocType",
                        "link_to": "Supplier",
                        "icon": "users",
                        "child": 0,
                        "collapsible": 1
                    },
                    {
                        "type": "Link",
                        "label": "Companies",
                        "link_type": "DocType",
                        "link_to": "Company",
                        "icon": "company",
                        "child": 0,
                        "collapsible": 1
                    }
                ]
            })
            ws_sidebar.insert(ignore_permissions=True)
            print("Successfully created Workspace Sidebar for Vendor Management!")
            frappe.utils.commands.export_doc("Workspace Sidebar", "Vendor Management")
        else:
            print("Workspace Sidebar already exists!")
            
        frappe.db.commit()
    except Exception as e:
        print("Error:", e)
