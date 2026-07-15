import frappe

def execute(filters=None):
	columns = [
		{"label": "Equipment ID", "fieldname": "equipment_id", "fieldtype": "Link", "options": "Equipment", "width": 180},
		{"label": "Equipment Name", "fieldname": "equipment_name", "fieldtype": "Data", "width": 180},
		{"label": "Asset Code", "fieldname": "asset_code", "fieldtype": "Data", "width": 120},
		{"label": "Serial No", "fieldname": "serial_no", "fieldtype": "Data", "width": 120},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": "Purchase Order", "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 150},
		{"label": "Purchase Invoice", "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 150},
		{"label": "Installation Date", "fieldname": "installation_date", "fieldtype": "Date", "width": 120},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120}
	]
	
	conditions = {}
	if filters and filters.get("company"):
		conditions["company"] = filters.get("company")
		
	try:
		equipment = frappe.get_all(
			"Equipment",
			filters=conditions,
			fields=["name", "equipment_name", "asset_code", "serial_no", "company", "purchase_order", "purchase_invoice", "installation_date", "status"]
		)
	except Exception:
		equipment = []
		
	data = []
	for eq in equipment:
		data.append({
			"equipment_id": eq.name,
			"equipment_name": eq.equipment_name,
			"asset_code": eq.asset_code,
			"serial_no": eq.serial_no,
			"company": eq.company,
			"purchase_order": eq.purchase_order,
			"purchase_invoice": eq.purchase_invoice,
			"installation_date": eq.installation_date,
			"status": eq.status
		})
		
	return columns, data
