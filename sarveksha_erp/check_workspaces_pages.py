import json, frappe.desk.desktop
def check_workspaces():
    pages = frappe.desk.desktop.get_workspaces()['pages']
    print(json.dumps([w['name'] for w in pages], indent=2))
