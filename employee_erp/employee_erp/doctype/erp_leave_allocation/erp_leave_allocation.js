// Copyright (c) 2026, Your Team Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERP Leave Allocation", {
	setup(frm) {
		frm.set_query("employee", function () {
			return {
				filters: {
					status: "Active",
				},
			};
		});
	},
});
