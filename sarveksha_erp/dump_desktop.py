import frappe
from frappe.desk.desktop import get_workspaces
import json

def execute():
    frappe.set_user("Administrator")
    ws = get_workspaces()
    print(json.dumps(ws, indent=2, default=str))
