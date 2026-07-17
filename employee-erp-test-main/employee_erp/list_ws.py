import frappe

def execute():
	print("--- WORKSPACES ---")
	workspaces = frappe.get_all("Workspace", filters={"type": "Workspace"}, fields=["name", "icon", "module", "is_hidden", "public", "parent_page", "for_user"])
	for w in workspaces:
		print(w)
