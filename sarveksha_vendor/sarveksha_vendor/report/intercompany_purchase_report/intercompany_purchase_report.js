frappe.query_reports["Intercompany Purchase Report"] = {
	"filters": [
		{
			"fieldname": "source_company",
			"label": __("Source Company"),
			"fieldtype": "Link",
			"options": "Company"
		},
		{
			"fieldname": "target_company",
			"label": __("Target Company"),
			"fieldtype": "Link",
			"options": "Company"
		}
	]
};
