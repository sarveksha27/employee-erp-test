import frappe
import json

def execute():
    try:
        # We need to remove the custom workspace if it exists, or clear shortcuts from standard
        home_ws = frappe.get_doc("Workspace", "Home")
        
        # Remove custom shortcuts
        shortcuts = home_ws.get("shortcuts")
        clean_shortcuts = [s for s in shortcuts if s.label not in ["Vendor Payments", "Vendors"]]
        home_ws.set("shortcuts", clean_shortcuts)
        
        # Remove from content json
        if home_ws.content:
            try:
                content = json.loads(home_ws.content)
                clean_content = [c for c in content if c.get("id") not in ["custom_vp", "custom_v"]]
                home_ws.content = json.dumps(clean_content)
            except Exception as e:
                pass
                
        home_ws.save(ignore_permissions=True)
        frappe.db.commit()
        print("Successfully cleaned up Home workspace.")
    except Exception as e:
        print("Error:", e)
