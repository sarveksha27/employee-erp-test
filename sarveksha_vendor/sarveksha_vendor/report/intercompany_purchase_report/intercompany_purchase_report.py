import frappe

def execute(filters=None):
	columns = [
		{"label": "Transfer ID", "fieldname": "transfer_id", "fieldtype": "Link", "options": "Intercompany Transfer", "width": 180},
		{"label": "Transfer Date", "fieldname": "transfer_date", "fieldtype": "Date", "width": 120},
		{"label": "Source Company", "fieldname": "source_company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": "Target Company", "fieldname": "target_company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": "Purchase Order", "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 150},
		{"label": "Intercompany Invoice", "fieldname": "intercompany_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 150},
		{"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
		{"label": "Transfer Status", "fieldname": "transfer_status", "fieldtype": "Data", "width": 120}
	]
	
	conditions = {}
	if filters and filters.get("source_company"):
		conditions["source_company"] = filters.get("source_company")
	if filters and filters.get("target_company"):
		conditions["target_company"] = filters.get("target_company")
		
	try:
		transfers = frappe.get_all(
			"Intercompany Transfer",
			filters=conditions,
			fields=["name", "transfer_date", "source_company", "target_company", "purchase_order", "intercompany_invoice", "amount", "transfer_status"]
		)
	except Exception:
		transfers = []
		
	data = []
	for t in transfers:
		data.append({
			"transfer_id": t.name,
			"transfer_date": t.transfer_date,
			"source_company": t.source_company,
			"target_company": t.target_company,
			"purchase_order": t.purchase_order,
			"intercompany_invoice": t.intercompany_invoice,
			"amount": t.amount,
			"transfer_status": t.transfer_status
		})
		
	return columns, data
