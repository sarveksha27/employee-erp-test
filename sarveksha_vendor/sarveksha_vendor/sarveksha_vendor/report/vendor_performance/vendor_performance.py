import frappe

def execute(filters=None):
	columns = [
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 150},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Contracts Count", "fieldname": "contracts_count", "fieldtype": "Int", "width": 120},
		{"label": "Total Contract Value", "fieldname": "total_contract_value", "fieldtype": "Currency", "width": 150},
		{"label": "Total Payments Paid", "fieldname": "total_payments_paid", "fieldtype": "Currency", "width": 150},
		{"label": "Pending Requests Count", "fieldname": "pending_requests_count", "fieldtype": "Int", "width": 150},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120}
	]

	# Fetch contract totals
	contracts = frappe.db.sql("""
		select vendor, company, count(name) as cnt, sum(contract_amount) as val
		from `tabVendor Contract`
		group by vendor, company
	""", as_dict=True)

	# Fetch paid totals
	paid_pmts = frappe.db.sql("""
		select vendor, company, sum(amount) as val
		from `tabVendor Payment Request`
		where status = 'Paid'
		group by vendor, company
	""", as_dict=True)

	# Fetch pending requests
	pending_pmts = frappe.db.sql("""
		select vendor, company, count(name) as cnt
		from `tabVendor Payment Request`
		where status in ('Draft', 'Finance Review', 'Under Approval', 'Approved', 'Batch Pending')
		group by vendor, company
	""", as_dict=True)

	# Assemble data map
	data_map = {}
	for c in contracts:
		key = (c.vendor, c.company)
		data_map[key] = {
			"vendor": c.vendor,
			"company": c.company,
			"contracts_count": c.cnt,
			"total_contract_value": float(c.val or 0.0),
			"total_payments_paid": 0.0,
			"pending_requests_count": 0,
			"status": "Good"
		}

	for p in paid_pmts:
		key = (p.vendor, p.company)
		if key in data_map:
			data_map[key]["total_payments_paid"] = float(p.val or 0.0)

	for r in pending_pmts:
		key = (r.vendor, r.company)
		if key in data_map:
			data_map[key]["pending_requests_count"] = r.cnt
			if r.cnt > 3:
				data_map[key]["status"] = "Action Required"

	data = list(data_map.values())
	return columns, data
