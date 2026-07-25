import frappe
def check_modules():
    mods = frappe.get_all('Module Def', filters={'name': ('in', ['Organization', 'Vendor Management', 'Equipment Management', 'Framework', 'Accounting', 'Accounts'])})
    print("Module Defs:", [m.name for m in mods])
    
    # Let's also check if there is a 'Workspace' for 'Accounting' and 'Organization'
    ws = frappe.get_all('Workspace', filters={'name': ('in', ['Organization', 'Accounting', 'Accounts'])})
    print("Workspaces:", [w.name for w in ws])
