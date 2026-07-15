import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 150},
		{"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 150},
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Debit (Payment)", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
		{"label": "Credit (Invoice)", "fieldname": "credit", "fieldtype": "Currency", "width": 120},
		{"label": "Outstanding Amount", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 150}
	]

def get_data(filters):
	conditions = {}
	if filters and filters.get("company"):
		conditions["company"] = filters.get("company")
	if filters and filters.get("supplier"):
		conditions["supplier"] = filters.get("supplier")
		
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
			"posting_date": inv.posting_date,
			"voucher_type": "Purchase Invoice",
			"voucher_no": inv.name,
			"supplier": inv.supplier,
			"company": inv.company,
			"debit": 0.0,
			"credit": inv.grand_total,
			"outstanding_amount": inv.outstanding_amount
		})
		
	data = sorted(data, key=lambda x: x["posting_date"] if x["posting_date"] else "")
	return data
