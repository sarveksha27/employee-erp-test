import frappe
def check_fy_mapping():
    try:
        fyc = frappe.get_all('Fiscal Year Company', fields=['parent', 'company'])
        if not fyc:
            print("No Fiscal Year Company mappings found!")
        else:
            for m in fyc:
                print(m)
    except Exception as e:
        print("Error:", e)
