import frappe
def check_company_fields():
    try:
        fields = frappe.get_all('Custom Field', filters={'dt': 'Company'}, fields=['fieldname'])
        print([f.fieldname for f in fields])
    except Exception as e:
        print("Error:", e)
