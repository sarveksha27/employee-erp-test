import frappe, json
def check_workspace():
    try:
        doc = frappe.get_doc('Workspace', 'Workspace')
        print(json.dumps(doc.as_dict(), indent=2, default=str))
    except Exception as e:
        print("Error:", str(e))
