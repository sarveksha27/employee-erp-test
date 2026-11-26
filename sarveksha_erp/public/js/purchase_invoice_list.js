frappe.listview_settings["Purchase Invoice"] = {
	onload: function (listview) {
		listview.page.clear_primary_action();
	},
	refresh: function (listview) {
		listview.page.clear_primary_action();
	},
};
