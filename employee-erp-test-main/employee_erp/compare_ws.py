import frappe

def execute():
	print("--- Workspace DB Comparison ---")
	p = frappe.db.get_value("Workspace", "Projects", "*", as_dict=1)
	e = frappe.db.get_value("Workspace", "Employee ERP", "*", as_dict=1)
	
	for key in p.keys():
		if key not in ['creation', 'modified', 'owner', 'modified_by', 'idx']:
			if p.get(key) != e.get(key):
				print(f"DIFFERENCE on {key}: Projects='{p.get(key)}' vs Employee='{e.get(key)}'")
