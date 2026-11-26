frappe.listview_settings["Payment Entry"] = {
	onload: function (listview) {
		listview.page.clear_primary_action();
	},
	refresh: function (listview) {
		listview.page.clear_primary_action();
	},
};
