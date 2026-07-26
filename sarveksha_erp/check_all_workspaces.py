import frappe
def check_workspaces():
    ws = frappe.get_all('Workspace', fields=['name', 'title', 'module'])
    for w in ws:
        print(f"Name: {w.name}, Title: {w.title}, Module: {w.module}")
