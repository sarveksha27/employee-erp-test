import frappe

def execute():
    try:
        if frappe.db.exists("Workspace", "Vendor Management"):
            ws = frappe.get_doc("Workspace", "Vendor Management")
            
            # 1. Clear existing shortcuts and links to ensure a fresh state
            ws.set("shortcuts", [])
            ws.set("links", [])
            
            # 2. Re-populate Shortcuts (These correspond to the ones in `content`)
            ws.append("shortcuts", {
                "type": "DocType",
                "link_to": "Vendor Payment",
                "label": "Vendor Payment",
                "icon": "payment",
                "color": "green",
                "format": "{} Open",
                "stats_filter": "[]"
            })
            
            ws.append("shortcuts", {
                "type": "DocType",
                "link_to": "Supplier",
                "label": "Supplier",
                "icon": "users",
                "color": "blue"
            })
            
            ws.append("shortcuts", {
                "type": "DocType",
                "link_to": "Company",
                "label": "Company",
                "icon": "company"
            })
            
            # 3. Add to standard Links array (Sidebar inner links)
            ws.append("links", {
                "type": "Card Break",
                "label": "Vendor Portal"
            })
            ws.append("links", {
                "type": "Link",
                "link_type": "DocType",
                "link_to": "Vendor Payment",
                "label": "Vendor Payments"
            })
            ws.append("links", {
                "type": "Link",
                "link_type": "DocType",
                "link_to": "Supplier",
                "label": "Vendors"
            })
            
            # 4. Set Workspace properties to Top-Level Sidebar standard
            ws.parent_page = "" # Top-Level
            ws.public = 1
            ws.is_hidden = 0
            ws.icon = "users"
            ws.sequence_id = 2.0
            
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            print("Successfully restructured Vendor Management workspace!")
            
            # 5. Export Document
            frappe.utils.commands.export_doc("Workspace", "Vendor Management")
            print("Exported Vendor Management Workspace successfully!")
        else:
            print("Workspace Vendor Management not found!")
    except Exception as e:
        print("Error:", e)
