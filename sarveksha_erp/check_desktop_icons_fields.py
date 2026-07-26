import frappe
def check_desktop_icons():
    try:
        icons = frappe.get_meta('Desktop Icon')
        print("Fields:", [f.fieldname for f in icons.fields])
        icons_docs = frappe.get_all('Desktop Icon', fields=['*'])
        for d in icons_docs:
            print(d.name, d.label, getattr(d, 'module_name', ''), getattr(d, '_user_tags', ''))
    except Exception as e:
        print("Error:", e)
