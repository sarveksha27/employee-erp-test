import frappe

def execute():
    try:
        ws = frappe.get_doc("Workspace", "Vendor Management")
        
        # Remove all role restrictions - makes it visible to all users (like standard workspaces)
        ws.set("roles", [])
        
        ws.save(ignore_permissions=True)
        frappe.db.commit()
        print("Removed role restrictions from Vendor Management workspace.")
        print("Workspace is now fully public and visible to all logged-in users.")
        
        # Export the updated doc
        frappe.utils.commands.export_doc("Workspace", "Vendor Management")
        print("Exported updated workspace.")
    except Exception as e:
        print("Error:", e)
