// Copyright (c) 2026, Your Team Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERP Attendance", {
	setup(frm) {
		frm.set_query("employee", function () {
			return {
				filters: {
					status: "Active",
				},
			};
		});
	},

	check_in_time(frm) {
		frm.events.calculate_working_hours(frm);
	},

	check_out_time(frm) {
		frm.events.calculate_working_hours(frm);
	},

	calculate_working_hours(frm) {
		if (frm.doc.check_in_time && frm.doc.check_out_time) {
			const checkin = frappe.datetime.moment(frm.doc.check_in_time, "HH:mm:ss");
			const checkout = frappe.datetime.moment(frm.doc.check_out_time, "HH:mm:ss");
			if (checkout.isAfter(checkin)) {
				const hours = checkout.diff(checkin, "hours", true);
				frm.set_value("working_hours", Math.round(hours * 10) / 10);
			}
		}
	},
});
