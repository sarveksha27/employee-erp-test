import frappe

def execute():
    try:
        doc = frappe.get_doc("Workspace Sidebar", "Vendor Management")
        
        existing_items = [item.link_to for item in doc.items]
        
        updated = False
        if "Vendor Purchase Order" not in existing_items:
            doc.append("items", {
                "child": 0,
                "collapsible": 1,
                "icon": "file-text",
                "indent": 0,
                "keep_closed": 0,
                "label": "Purchase Orders",
                "link_to": "Vendor Purchase Order",
                "link_type": "DocType",
                "show_arrow": 0,
                "type": "Link"
            })
            updated = True
            
        if "Equipment" not in existing_items:
            doc.append("items", {
                "child": 0,
                "collapsible": 1,
                "icon": "tool",
                "indent": 0,
                "keep_closed": 0,
                "label": "Equipment",
                "link_to": "Equipment",
                "link_type": "DocType",
                "show_arrow": 0,
                "type": "Link"
            })
            updated = True
            
        if updated:
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            print("Successfully updated Workspace Sidebar items in the database!")
        else:
            print("Items already existed in the Workspace Sidebar.")
            
    except Exception as e:
        print(f"Error: {e}")

execute()
