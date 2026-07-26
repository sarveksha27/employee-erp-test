import frappe
def check_allowed_modules():
    import frappe.boot
    import json
    bootinfo = frappe.boot.get_bootinfo()
    allowed = bootinfo.get('allowed_modules', [])
    print("Allowed modules count:", len(allowed))
    for m in allowed:
        print(f"  - {m.get('module_name')}")
