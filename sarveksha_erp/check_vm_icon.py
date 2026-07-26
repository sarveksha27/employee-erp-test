import frappe
def check_vm_icon():
    d = frappe.get_doc('Desktop Icon', 'Vendor Management')
    print(d.as_dict())
