import frappe

def execute():
	u = frappe.get_doc("User", "Administrator")
	print(u.home_settings)
