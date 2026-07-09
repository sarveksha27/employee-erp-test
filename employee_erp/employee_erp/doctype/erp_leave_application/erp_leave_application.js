// Copyright (c) 2026, Your Team Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERP Leave Application", {
	setup(frm) {
		frm.set_query("employee", function () {
			return {
				filters: {
					status: "Active",
				},
			};
		});
	},

	employee(frm) {
		if (frm.doc.employee && frm.doc.leave_type) {
			frm.events.show_leave_balance(frm);
		}
	},

	leave_type(frm) {
		if (frm.doc.employee && frm.doc.leave_type) {
			frm.events.show_leave_balance(frm);
		}
	},

	from_date(frm) {
		frm.events.calculate_total_days(frm);
	},

	to_date(frm) {
		frm.events.calculate_total_days(frm);
	},

	calculate_total_days(frm) {
		if (frm.doc.from_date && frm.doc.to_date) {
			if (frm.doc.to_date < frm.doc.from_date) {
				frappe.msgprint(__("To Date cannot be before From Date."));
				frm.set_value("to_date", frm.doc.from_date);
				return;
			}
			const days = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1;
			frm.set_value("total_leave_days", days);
		}
	},

	show_leave_balance(frm) {
		const fiscal_year = String(
			frappe.datetime.str_to_obj(frm.doc.from_date || frappe.datetime.get_today()).getFullYear()
		);

		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "ERP Leave Allocation",
				filters: {
					employee: frm.doc.employee,
					leave_type: frm.doc.leave_type,
					fiscal_year: fiscal_year,
				},
				fieldname: ["total_leaves_allocated", "leaves_taken", "balance_leaves"],
			},
			callback(r) {
				if (r.message) {
					frm.dashboard.set_headline(
						__("Leave Balance: {0} (Allocated: {1}, Taken: {2})", [
							r.message.balance_leaves || 0,
							r.message.total_leaves_allocated || 0,
							r.message.leaves_taken || 0,
						])
					);
				} else {
					frm.dashboard.set_headline(
						__("No leave allocation found for this employee and leave type.")
					);
				}
			},
		});
	},
});
