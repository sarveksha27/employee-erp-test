import frappe

def execute(filters=None):
	columns = [
		{"label": "Schedule ID", "fieldname": "name", "fieldtype": "Link", "options": "Vendor Payment Schedule", "width": 150},
		{"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 120},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 150},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Purchase Order", "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 150},
		{"label": "Scheduled Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
		{"label": "Paid Amount", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Outstanding Amount", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120}
	]

	conditions = {"outstanding_amount": [">", 0]}
	if filters:
		if filters.get("company"):
			conditions["company"] = filters.get("company")
		if filters.get("vendor"):
			conditions["vendor"] = filters.get("vendor")

	data = frappe.get_all(
		"Vendor Payment Schedule",
		filters=conditions,
		fields=["name", "due_date", "vendor", "company", "purchase_order", "amount", "paid_amount", "outstanding_amount", "status"],
		order_by="due_date asc"
	)

	return columns, data
