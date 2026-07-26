import frappe
def check_fiscal_years():
    try:
        fys = frappe.get_all('Fiscal Year', fields=['name'])
        print([f.name for f in fys])
    except Exception as e:
        print("Error:", e)
