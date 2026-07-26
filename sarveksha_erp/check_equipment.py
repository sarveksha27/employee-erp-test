import frappe
def check_equipment():
    try:
        fields = frappe.get_meta('Equipment').fields
        for f in fields:
            print(f.fieldname, f.fieldtype)
    except Exception as e:
        print("Error:", e)
