import frappe

def execute():
	if frappe.db.exists("Workspace", "Employee ERP"):
		ws = frappe.get_doc("Workspace", "Employee ERP")
		ws.set("roles", [])
		ws.append("roles", {"role": "System Manager"})
		ws.append("roles", {"role": "HR Manager"})
		ws.type = "Workspace"
		ws.flags.ignore_permissions = True
		ws.save()
		frappe.db.commit()
		print("Roles updated.")
