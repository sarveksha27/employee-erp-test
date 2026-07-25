import frappe

def execute():
    m = frappe.get_doc("Module Def", "Vendor Management")
    print(m.as_dict())
