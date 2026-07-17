import frappe

def execute():
	print(frappe.get_all('DocType', filters={'name': ('like', '%Workspace%')}, pluck='name'))
