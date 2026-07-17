// Copyright (c) 2026, Your Team Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERP Salary Slip", {
	setup(frm) {
		frm.set_query("employee", function () {
			return {
				filters: {
					status: "Active",
				},
			};
		});

		frm.set_query("salary_structure", function () {
			return {
				filters: {
					is_active: 1,
				},
			};
		});
	},

	refresh(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.salary_structure) {
			frm.add_custom_button(__("Get Components"), function () {
				frm.call({
					doc: frm.doc,
					method: "pull_salary_components",
					freeze: true,
					freeze_message: __("Fetching Salary Components..."),
					callback(r) {
						frm.refresh_fields();
						frm.dirty();
					},
				});
			});
		}
	},

	salary_structure(frm) {
		if (frm.doc.salary_structure && frm.doc.docstatus === 0) {
			frm.call({
				doc: frm.doc,
				method: "pull_salary_components",
				freeze: true,
				freeze_message: __("Fetching Salary Components..."),
				callback(r) {
					frm.refresh_fields();
					frm.dirty();
				},
			});
		}
	},
});
