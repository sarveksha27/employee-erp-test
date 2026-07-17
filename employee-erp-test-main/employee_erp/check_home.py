import frappe

def execute():
	try:
		w = frappe.get_doc("Workspace", "Home")
		print(w.content)
	except Exception as e:
		print("Error:", e)
