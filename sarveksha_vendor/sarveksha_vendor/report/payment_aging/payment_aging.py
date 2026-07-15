import frappe
from frappe.utils import date_diff, today

def execute(filters=None):
	columns = [
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": "0-30 Days", "fieldname": "range1", "fieldtype": "Currency", "width": 120},
		{"label": "31-60 Days", "fieldname": "range2", "fieldtype": "Currency", "width": 120},
		{"label": "61-90 Days", "fieldname": "range3", "fieldtype": "Currency", "width": 120},
		{"label": "90+ Days", "fieldname": "range4", "fieldtype": "Currency", "width": 120},
		{"label": "Total Outstanding", "fieldname": "total_outstanding", "fieldtype": "Currency", "width": 150}
	]
	
	conditions = {"outstanding_amount": [">", 0]}
	if filters and filters.get("company"):
		conditions["company"] = filters.get("company")
		
	try:
		invoices = frappe.get_all(
			"Purchase Invoice",
			filters=conditions,
			fields=["posting_date", "supplier", "company", "outstanding_amount"]
		)
	except Exception:
		invoices = []
		
	data_map = {}
	current_date = today()
	
	for inv in invoices:
		key = (inv.supplier, inv.company)
		if key not in data_map:
			data_map[key] = {"supplier": inv.supplier, "company": inv.company, "range1": 0.0, "range2": 0.0, "range3": 0.0, "range4": 0.0, "total_outstanding": 0.0}
			
		days = date_diff(current_date, inv.posting_date)
		outstanding = float(inv.outstanding_amount or 0)
		
		if days <= 30:
			data_map[key]["range1"] += outstanding
		elif days <= 60:
			data_map[key]["range2"] += outstanding
		elif days <= 90:
			data_map[key]["range3"] += outstanding
		else:
			data_map[key]["range4"] += outstanding
			
		data_map[key]["total_outstanding"] += outstanding
		
	return columns, list(data_map.values())
