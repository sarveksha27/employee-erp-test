import frappe
import json

def execute():
    w = frappe.get_doc("Workspace", "Vendor Management")
    print(json.dumps(w.as_dict(), indent=2, default=str))
