import frappe
from frappe.utils import date_diff, today, getdate

def execute(filters=None):
	columns = [
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 150},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Outstanding Amount", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 150},
		{"label": "0 - 30 Days", "fieldname": "range_1", "fieldtype": "Currency", "width": 120},
		{"label": "31 - 60 Days", "fieldname": "range_2", "fieldtype": "Currency", "width": 120},
		{"label": "61 - 90 Days", "fieldname": "range_3", "fieldtype": "Currency", "width": 120},
		{"label": "90+ Days", "fieldname": "range_4", "fieldtype": "Currency", "width": 120}
	]

	conditions = {"outstanding_amount": [">", 0]}
	if filters:
		if filters.get("company"):
			conditions["company"] = filters.get("company")
		if filters.get("vendor"):
			conditions["vendor"] = filters.get("vendor")

	schedules = frappe.get_all(
		"Vendor Payment Schedule",
		filters=conditions,
		fields=["vendor", "company", "due_date", "outstanding_amount"]
	)

	data_map = {}
	current_date = getdate(today())

	for s in schedules:
		key = (s.vendor, s.company)
		if key not in data_map:
			data_map[key] = {
				"vendor": s.vendor,
				"company": s.company,
				"outstanding_amount": 0.0,
				"range_1": 0.0,
				"range_2": 0.0,
				"range_3": 0.0,
				"range_4": 0.0
			}

		diff = date_diff(current_date, s.due_date)
		out_amt = float(s.outstanding_amount)
		data_map[key]["outstanding_amount"] += out_amt

		if diff <= 30:
			data_map[key]["range_1"] += out_amt
		elif diff <= 60:
			data_map[key]["range_2"] += out_amt
		elif diff <= 90:
			data_map[key]["range_3"] += out_amt
		else:
			data_map[key]["range_4"] += out_amt

	data = list(data_map.values())
	return columns, data
