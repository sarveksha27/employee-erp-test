import frappe

def execute(filters=None):
	columns = [
		{"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Link", "options": "Purchase Invoice", "width": 180},
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
		{"label": "Outstanding Amount", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 150}
	]
	
	conditions = {"outstanding_amount": [">", 0]}
	if filters and filters.get("company"):
		conditions["company"] = filters.get("company")
		
	try:
		invoices = frappe.get_all(
			"Purchase Invoice",
			filters=conditions,
			fields=["name", "posting_date", "supplier", "company", "grand_total", "outstanding_amount"]
		)
	except Exception:
		invoices = []
		
	data = []
	for inv in invoices:
		data.append({
			"voucher_no": inv.name,
			"posting_date": inv.posting_date,
			"supplier": inv.supplier,
			"company": inv.company,
			"grand_total": inv.grand_total,
			"outstanding_amount": inv.outstanding_amount
		})
		
	return columns, data
