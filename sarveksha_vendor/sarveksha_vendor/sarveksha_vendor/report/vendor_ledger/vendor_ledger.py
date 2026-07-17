import frappe

def execute(filters=None):
	columns = [
		{"label": "Request ID", "fieldname": "name", "fieldtype": "Link", "options": "Vendor Payment Request", "width": 150},
		{"label": "Posting Date", "fieldname": "request_date", "fieldtype": "Date", "width": 120},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 150},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Invoice", "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 150},
		{"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120}
	]

	conditions = {}
	if filters:
		if filters.get("company"):
			conditions["company"] = filters.get("company")
		if filters.get("vendor"):
			conditions["vendor"] = filters.get("vendor")

	data = frappe.get_all(
		"Vendor Payment Request",
		filters=conditions,
		fields=["name", "request_date", "vendor", "company", "purchase_invoice", "amount", "status"],
		order_by="request_date desc"
	)

	return columns, data
