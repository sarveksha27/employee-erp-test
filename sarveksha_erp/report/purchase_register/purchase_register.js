// Copyright (c) 2026, Sarveksha Group and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Register"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Sarveksha Company"
		},
		{
			"fieldname": "vendor",
			"label": __("Vendor"),
			"fieldtype": "Link",
			"options": "Sarveksha Vendor"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nEquipment Enquiry\nVendor Selection\nQuotation\nPurchase Order\nProforma Invoice\nAdvance Payment\nManufacturing\nDispatch\nShipment\nContainer Tracking\nExport Documentation\nDestination Warehouse\nFinal Payment\nCompleted"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		}
	]
};
