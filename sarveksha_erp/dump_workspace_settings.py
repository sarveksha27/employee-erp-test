import frappe

def execute():
    try:
        w = frappe.get_single("Workspace Settings")
        print(w.as_dict())
    except Exception as e:
        print("Error:", e)
