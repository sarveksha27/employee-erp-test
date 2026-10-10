// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Entry", {
	setup: function (frm) {
		// Set default print format
		frm.meta.default_print_format = "Payment Receipt Proof";

		// Auto-populate company if empty before any validation triggers
		if (!frm.doc.company) {
			const default_company =
				frappe.defaults.get_user_default("Company") ||
				frappe.defaults.get_default("company") ||
				"Sarveksha Realty and Inframine LLP";
			frm.doc.company = default_company;
		}

		// Override validate_company so it gracefully defaults rather than throwing an error popup
		frm.events.validate_company = function (frm) {
			if (!frm.doc.company) {
				const default_company =
					frappe.defaults.get_user_default("Company") ||
					frappe.defaults.get_default("company") ||
					"Sarveksha Realty and Inframine LLP";
				frm.set_value("company", default_company);
			}
		};

		// Filter Party Type strictly to Supplier (Vendors) and Company
		frm.set_query("party_type", function () {
			return {
				filters: {
					name: ["in", ["Supplier", "Company"]],
				},
			};
		});

		// Filter Party: if Supplier, only show Suppliers; if Company, only show Companies
		frm.set_query("party", function (doc) {
			if (doc.party_type === "Supplier") {
				return {
					filters: {
						is_transporter: 0,
					},
				};
			} else if (doc.party_type === "Company") {
				return {
					filters: {
						is_group: 0,
						name: ["!=", doc.company],
					},
				};
			}
		});
	},

	onload: function (frm) {
		// Ensure Company is set immediately on new form
		if (frm.is_new() || frm.doc.__islocal) {
			if (!frm.doc.company) {
				const default_company =
					frappe.defaults.get_user_default("Company") ||
					frappe.defaults.get_default("company") ||
					"Sarveksha Realty and Inframine LLP";
				frm.set_value("company", default_company);
			}

			if (!frm.doc.payment_type || frm.doc.payment_type === "Receive") {
				frm.set_value("payment_type", "Pay");
			}

			if (!frm.doc.party_type || frm.doc.party_type === "Customer") {
				frm.set_value("party_type", "Supplier");
			}
		}
	},

	refresh: function (frm) {
		frm.meta.default_print_format = "Payment Receipt Proof";

		if (frm.is_new() || frm.doc.__islocal) {
			if (!frm.doc.company) {
				const default_company =
					frappe.defaults.get_user_default("Company") ||
					frappe.defaults.get_default("company") ||
					"Sarveksha Realty and Inframine LLP";
				frm.set_value("company", default_company);
			}

			if (!frm.doc.payment_type || frm.doc.payment_type === "Receive") {
				frm.set_value("payment_type", "Pay");
			}

			if (!frm.doc.party_type || frm.doc.party_type === "Customer") {
				frm.set_value("party_type", "Supplier");
			}
		}
	},

	payment_type: function (frm) {
		// If switching to Pay, ensure party_type defaults to Supplier
		if (frm.doc.payment_type === "Pay" && frm.doc.party_type === "Customer") {
			frm.set_value("party_type", "Supplier");
		}
	},

	mode_of_payment: function (frm) {
		// Auto-fetch account for company if not set
		if (frm.doc.mode_of_payment && frm.doc.company && !frm.doc.paid_from) {
			frappe.call({
				method: "sarveksha_erp.payment_tracking.events.payment_entry_events.get_mode_of_payment_account",
				args: {
					mode_of_payment: frm.doc.mode_of_payment,
					company: frm.doc.company,
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value("paid_from", r.message);
					}
				},
			});
		}
	},
});
