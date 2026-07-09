// Copyright (c) 2026, Your Team Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERP Employee", {
	setup(frm) {
		frm.set_query("department", function () {
			return {
				filters: {
					is_active: 1,
				},
			};
		});

		frm.set_query("reports_to", function () {
			return {
				filters: {
					status: "Active",
					name: ["!=", frm.doc.name || ""],
				},
			};
		});
	},

	refresh(frm) {
		if (frm.doc.date_of_birth) {
			frm.fields_dict.date_of_birth.datepicker?.update({
				maxDate: new Date(),
			});
		}

		// Show/hide exit tab fields based on status
		frm.toggle_display(
			["resignation_letter_date", "relieving_date", "reason_for_leaving", "exit_comment"],
			frm.doc.status === "Left"
		);
	},

	first_name(frm) {
		frm.events.update_employee_name(frm);
	},

	middle_name(frm) {
		frm.events.update_employee_name(frm);
	},

	last_name(frm) {
		frm.events.update_employee_name(frm);
	},

	update_employee_name(frm) {
		const parts = [frm.doc.first_name, frm.doc.middle_name, frm.doc.last_name].filter(
			Boolean
		);
		frm.set_value("employee_name", parts.join(" "));
	},

	status(frm) {
		frm.toggle_display(
			["resignation_letter_date", "relieving_date", "reason_for_leaving", "exit_comment"],
			frm.doc.status === "Left"
		);
	},
});
