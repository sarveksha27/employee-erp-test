# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": _("PO Number"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Sarveksha Purchase Order",
			"width": 180
		},
		{
			"label": _("Date"),
			"fieldname": "creation",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Sarveksha Company",
			"width": 140
		},
		{
			"label": _("Vendor"),
			"fieldname": "vendor",
			"fieldtype": "Link",
			"options": "Sarveksha Vendor",
			"width": 160
		},
		{
			"label": _("Equipment"),
			"fieldname": "equipment",
			"fieldtype": "Link",
			"options": "Sarveksha Equipment",
			"width": 160
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 80
		},
		{
			"label": _("Qty"),
			"fieldname": "quantity",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100
		},
		{
			"label": _("Discount"),
			"fieldname": "discount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 90
		},
		{
			"label": _("Tax"),
			"fieldname": "tax",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 90
		},
		{
			"label": _("Freight"),
			"fieldname": "freight",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 90
		},
		{
			"label": _("Grand Total"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		}
	]

def get_data(filters):
	query_filters = {}
	if filters.get("company"):
		query_filters["company"] = filters.get("company")
	if filters.get("vendor"):
		query_filters["vendor"] = filters.get("vendor")
	if filters.get("status"):
		query_filters["status"] = filters.get("status")
	if filters.get("from_date") and filters.get("to_date"):
		query_filters["creation"] = ["between", [filters.get("from_date"), filters.get("to_date")]]

	fields = [
		"name", "creation", "company", "vendor", "equipment", "status",
		"currency", "quantity", "rate", "discount", "tax", "freight", "grand_total"
	]
	
	return frappe.get_all("Sarveksha Purchase Order", filters=query_filters, fields=fields, order_by="creation desc")
