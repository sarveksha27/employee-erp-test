import frappe
from frappe.utils import today

def execute(filters=None):
	columns = [
		{"label": "Payment Request", "fieldname": "payment_request", "fieldtype": "Link", "options": "Vendor Payment Request", "width": 180},
		{"label": "Request Date", "fieldname": "request_date", "fieldtype": "Date", "width": 120},
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": "Requested Amount", "fieldname": "requested_amount", "fieldtype": "Currency", "width": 150},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120}
	]
	
	conditions = {"status": ["in", ["Draft", "Pending Finance Review", "Pending Approval", "Approved"]]}
	if filters and filters.get("company"):
		conditions["company"] = filters.get("company")
		
	try:
		requests = frappe.get_all(
			"Vendor Payment Request",
			filters=conditions,
			fields=["name", "request_date", "vendor", "company", "requested_amount", "status"]
		)
	except Exception:
		requests = []
		
	data = []
	for req in requests:
		data.append({
			"payment_request": req.name,
			"request_date": req.request_date,
			"supplier": req.vendor,
			"company": req.company,
			"requested_amount": req.requested_amount,
			"status": req.status
		})
		
	return columns, data
