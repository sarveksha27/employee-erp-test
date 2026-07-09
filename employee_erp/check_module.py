import frappe
from frappe.boot import get_bootinfo

def execute():
	bootinfo = get_bootinfo()
	print("module_app keys:", bootinfo.get('module_app', {}).keys())
	print("employee_erp in module_app?", "employee_erp" in bootinfo.get('module_app', {}).values())
	print("module_app:", bootinfo.get('module_app'))
