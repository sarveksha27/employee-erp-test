import frappe, json
def check_desktop_icons():
    try:
        icons = frappe.get_all('Desktop Icon', fields=['module_name'])
        print([d.module_name for d in icons])
    except Exception as e:
        print("Error:", e)
