import frappe

def execute():
	from frappe.boot import get_bootinfo
	frappe.set_user("Administrator")
	bootinfo = get_bootinfo()
	allowed_modules = bootinfo.get("allowed_modules", [])
	print(f"Is Employee ERP in allowed_modules? {'Employee ERP' in allowed_modules}")
	print(f"allowed_modules: {allowed_modules}")
