import frappe

def execute(filters=None):
	columns = [
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": "Total Purchase Orders", "fieldname": "total_pos", "fieldtype": "Int", "width": 150},
		{"label": "Total Invoiced Amount", "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 180},
		{"label": "Outstanding Amount", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 180},
		{"label": "Performance Score", "fieldname": "performance_score", "fieldtype": "Percent", "width": 150}
	]
	
	conditions = {}
	if filters and filters.get("supplier"):
		conditions["name"] = filters.get("supplier")
		
	try:
		suppliers = frappe.get_all("Supplier", filters=conditions, fields=["name"])
	except Exception:
		suppliers = []
		
	data = []
	for s in suppliers:
		try:
			pos_count = frappe.db.count("Purchase Order", filters={"supplier": s.name})
			invs = frappe.get_all(
				"Purchase Invoice",
				filters={"supplier": s.name},
				fields=["grand_total", "outstanding_amount"]
			)
			total_invoiced = sum([float(i.grand_total or 0) for i in invs])
			outstanding = sum([float(i.outstanding_amount or 0) for i in invs])
			
			paid_ratio = 1.0
			if total_invoiced > 0:
				paid_ratio = (total_invoiced - outstanding) / total_invoiced
			score = round(paid_ratio * 100, 2)
		except Exception:
			pos_count = 0
			total_invoiced = 0.0
			outstanding = 0.0
			score = 100.0

		data.append({
			"supplier": s.name,
			"total_pos": pos_count,
			"total_invoiced": total_invoiced,
			"outstanding_amount": outstanding,
			"performance_score": score
		})
		
	return columns, data
