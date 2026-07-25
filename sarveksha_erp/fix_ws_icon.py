import frappe
import json

def execute():
    try:
        w = frappe.get_doc("Workspace", "Vendor Management")
        w.icon = "users"
        w.sequence_id = 1.0 # high priority
        w.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated Vendor Management icon and sequence!")
    except Exception as e:
        print("Error:", e)
