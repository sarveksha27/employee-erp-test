import frappe
def check_all_modules():
    mods = frappe.get_all('Module Def', fields=['name', 'module_name'])
    for m in mods:
        print(m.name)
