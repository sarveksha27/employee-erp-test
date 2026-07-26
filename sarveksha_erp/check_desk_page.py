import frappe
def check_desk_page():
    try:
        pages = frappe.get_all('Desk Page')
        print("Desk Pages:", pages)
    except Exception as e:
        print("Error:", e)
