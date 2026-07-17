// Copyright (c) 2026, Your Team Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERP Department", {
	setup(frm) {
		frm.set_query("department_head", function () {
			return {
				filters: {
					status: "Active",
				},
			};
		});

		frm.set_query("parent_department", function () {
			return {
				filters: {
					name: ["!=", frm.doc.name || ""],
					is_active: 1,
				},
			};
		});
	},
});
