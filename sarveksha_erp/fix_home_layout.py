import frappe
import json

def execute():
    try:
        home = frappe.get_doc("Workspace", "Home")
        content = json.loads(home.content)
        
        # Add the shortcuts to the content array right after the header
        content.append({
            "id": "custom_vp",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Vendor Payments",
                "col": 3
            }
        })
        content.append({
            "id": "custom_v",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Vendors",
                "col": 3
            }
        })
        
        home.content = json.dumps(content)
        home.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated Home workspace layout!")
    except Exception as e:
        print("Error:", e)
