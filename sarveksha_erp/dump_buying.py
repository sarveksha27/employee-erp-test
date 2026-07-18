import frappe
import json

def execute():
    w = frappe.get_doc("Workspace", "Buying")
    print(json.dumps(w.as_dict(), indent=2, default=str))
