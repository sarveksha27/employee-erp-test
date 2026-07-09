frappe.listview_settings["ERP Employee"] = {
	add_fields: ["status", "department", "designation", "image"],
	filters: [["status", "=", "Active"]],

	get_indicator(doc) {
		const status_map = {
			Active: [__("Active"), "green", "status,=,Active"],
			Inactive: [__("Inactive"), "orange", "status,=,Inactive"],
			Suspended: [__("Suspended"), "yellow", "status,=,Suspended"],
			Left: [__("Left"), "red", "status,=,Left"],
		};

		return status_map[doc.status] || [__("Active"), "green", "status,=,Active"];
	},
};
