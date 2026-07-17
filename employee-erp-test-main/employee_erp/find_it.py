import frappe

def execute():
	print("--- RESULTS ---")
	for doctype in frappe.get_all('DocType', pluck='name'):
		try:
			if frappe.db.exists(doctype, 'Accounting'):
				print(f'Found in {doctype}: Accounting')
			if frappe.db.exists(doctype, 'Framework'):
				print(f'Found in {doctype}: Framework')
		except Exception:
			pass
