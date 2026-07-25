import frappe

def execute():
    try:
        ws = frappe.get_doc("Workspace", "Vendor Management")
        
        # Update shortcuts to use safe, verified Frappe SVG icons to prevent Vue rendering crashes
        for shortcut in ws.shortcuts:
            shortcut.icon = "accounting" # Verified safe icon
            
        ws.icon = "accounting" # Safe workspace icon
        
        ws.save(ignore_permissions=True)
        frappe.db.commit()
        print("Successfully updated icons to standard 'accounting'.")
        
        frappe.utils.commands.export_doc("Workspace", "Vendor Management")
        print("Exported Vendor Management Workspace successfully!")
    except Exception as e:
        print("Error:", e)
