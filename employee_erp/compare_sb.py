import frappe
def execute():
	print("--- Workspace Sidebar DB Comparison ---")
	p = frappe.db.get_value("Workspace Sidebar", "Projects", "*", as_dict=1)
	e = frappe.db.get_value("Workspace Sidebar", "Employee ERP", "*", as_dict=1)
	
	if p and e:
		for key in p.keys():
			if key not in ['creation', 'modified', 'owner', 'modified_by', 'idx']:
				if p.get(key) != e.get(key):
					print(f"DIFFERENCE on {key}: Projects='{p.get(key)}' vs Employee='{e.get(key)}'")
	else:
		print("Missing sidebar?", "Projects:", bool(p), "Employee ERP:", bool(e))
