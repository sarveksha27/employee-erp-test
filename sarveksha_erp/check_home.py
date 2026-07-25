import frappe
import json

def execute():
    w = frappe.get_doc("Workspace", "Home")
    print("SHORTCUTS TABLE:")
    print(json.dumps([s.as_dict() for s in w.shortcuts], indent=2, default=str))
    print("\nCONTENT FIELD:")
    print(w.content)
