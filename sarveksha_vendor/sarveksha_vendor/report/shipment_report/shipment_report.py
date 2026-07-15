import frappe

def execute(filters=None):
	columns = [
		{"label": "Shipment ID", "fieldname": "shipment_id", "fieldtype": "Link", "options": "Shipment", "width": 180},
		{"label": "Shipment Date", "fieldname": "shipment_date", "fieldtype": "Date", "width": 120},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": "Origin", "fieldname": "origin_country", "fieldtype": "Link", "options": "Country", "width": 120},
		{"label": "Destination", "fieldname": "destination_country", "fieldtype": "Link", "options": "Country", "width": 120},
		{"label": "Carrier", "fieldname": "carrier_name", "fieldtype": "Data", "width": 120},
		{"label": "Tracking Number", "fieldname": "tracking_number", "fieldtype": "Data", "width": 150}
	]
	
	conditions = {}
	if filters and filters.get("company"):
		conditions["company"] = filters.get("company")
	if filters and filters.get("status"):
		conditions["status"] = filters.get("status")
		
	try:
		shipments = frappe.get_all(
			"Shipment",
			filters=conditions,
			fields=["name", "shipment_date", "status", "company", "origin_country", "destination_country", "carrier_name", "tracking_number"]
		)
	except Exception:
		shipments = []
		
	data = []
	for s in shipments:
		data.append({
			"shipment_id": s.name,
			"shipment_date": s.shipment_date,
			"status": s.status,
			"company": s.company,
			"origin_country": s.origin_country,
			"destination_country": s.destination_country,
			"carrier_name": s.carrier_name,
			"tracking_number": s.tracking_number
		})
		
	return columns, data
