import frappe
def create_desktop_icon():
    try:
        if not frappe.db.exists('Desktop Icon', 'Equipment Management'):
            doc = frappe.get_doc({
                'doctype': 'Desktop Icon',
                'name': 'Equipment Management',
                'label': 'Equipment Management',
                'icon_type': 'Link',
                'icon': 'setting',
                'link_to': 'Equipment Management',
                'link_type': 'Workspace Sidebar',
                'parent_icon': 'ERPNext',
                'standard': 1,
                'app': 'sarveksha_erp',
                'hidden': 0,
                'bg_color': 'gray'
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print("Desktop Icon created!")
        else:
            print("Desktop Icon already exists.")
    except Exception as e:
        print("Error:", e)
