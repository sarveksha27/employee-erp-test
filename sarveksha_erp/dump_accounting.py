import frappe
import json

def execute():
    w = frappe.get_doc("Workspace", "Accounting")
    print(json.dumps(w.as_dict(), indent=2, default=str))
