import frappe

def execute():
    ws = frappe.get_all("Workspace", pluck="name")
    for w in ws:
        print(w)
