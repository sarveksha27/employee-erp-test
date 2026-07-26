import frappe, json
def check_companies():
    try:
        companies = frappe.get_all('Company', fields=['name'])
        print([c.name for c in companies])
    except Exception as e:
        print("Error:", e)
