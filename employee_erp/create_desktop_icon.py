import frappe

def execute():
	frappe.set_user("Administrator")
	
	if not frappe.db.exists("Desktop Icon", "Employee ERP"):
		doc = frappe.new_doc("Desktop Icon")
		doc.name = "Employee ERP"
		doc.label = "Employee ERP"
		doc.icon_type = "Link"
		doc.link_type = "Workspace Sidebar"
		doc.link_to = "Employee ERP"
		doc.parent_icon = "ERPNext"
		doc.standard = 1
		doc.app = "employee_erp"
		doc.icon = "users"
		doc.hidden = 0
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print("Desktop Icon created.")
	else:
		print("Desktop Icon already exists.")
