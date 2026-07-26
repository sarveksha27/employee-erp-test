import frappe
def check_home_content():
    doc = frappe.get_doc('Workspace', 'Home')
    print("Home Workspace Content:")
    print(doc.content)
