import frappe

def execute(filters=None):
	columns = [
		{"label": "Shipment ID", "fieldname": "name", "fieldtype": "Link", "options": "Shipment", "width": 150},
		{"label": "Origin", "fieldname": "origin_country", "fieldtype": "Link", "options": "Country", "width": 120},
		{"label": "Destination", "fieldname": "destination_country", "fieldtype": "Link", "options": "Country", "width": 120},
		{"label": "Carrier", "fieldname": "carrier", "fieldtype": "Data", "width": 120},
		{"label": "Tracking Number", "fieldname": "tracking_number", "fieldtype": "Data", "width": 150},
		{"label": "Shipment Date", "fieldname": "shipment_date", "fieldtype": "Date", "width": 120},
		{"label": "Est. Delivery", "fieldname": "estimated_delivery_date", "fieldtype": "Date", "width": 120},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150}
	]

	conditions = {}
	if filters:
		if filters.get("company"):
			conditions["company"] = filters.get("company")
		if filters.get("status"):
			conditions["status"] = filters.get("status")

	data = frappe.get_all(
		"Shipment",
		filters=conditions,
		fields=["name", "origin_country", "destination_country", "carrier", "tracking_number", "shipment_date", "estimated_delivery_date", "status", "company"],
		order_by="shipment_date desc"
	)

	return columns, data
