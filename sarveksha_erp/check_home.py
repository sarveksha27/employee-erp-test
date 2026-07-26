import frappe, json
def check_home():
    doc = frappe.get_doc('Workspace', 'Home')
    print(json.dumps(doc.as_dict(), indent=2, default=str))
