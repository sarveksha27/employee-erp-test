import frappe

def execute():
    ws = frappe.get_all("Workspace", filters={"for_user": "Administrator"}, pluck="name")
    print("Custom workspaces for Administrator:")
    for w in ws:
        print(w)
