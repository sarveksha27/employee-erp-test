import frappe

def execute(filters=None):
	columns = [
		{"label": "Equipment ID", "fieldname": "name", "fieldtype": "Link", "options": "Equipment", "width": 150},
		{"label": "Equipment Name", "fieldname": "equipment_name", "fieldtype": "Data", "width": 150},
		{"label": "Type", "fieldname": "equipment_type", "fieldtype": "Data", "width": 120},
		{"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 120},
		{"label": "Serial Number", "fieldname": "serial_number", "fieldtype": "Data", "width": 120},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Purchase Date", "fieldname": "purchase_date", "fieldtype": "Date", "width": 120},
		{"label": "Cost", "fieldname": "purchase_cost", "fieldtype": "Currency", "width": 120},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 150},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120}
	]

	conditions = {}
	if filters:
		if filters.get("company"):
			conditions["company"] = filters.get("company")
		if filters.get("status"):
			conditions["status"] = filters.get("status")

	data = frappe.get_all(
		"Equipment",
		filters=conditions,
		fields=["name", "equipment_name", "equipment_type", "model", "serial_number", "company", "purchase_date", "purchase_cost", "vendor", "status"],
		order_by="purchase_date desc"
	)

	return columns, data
