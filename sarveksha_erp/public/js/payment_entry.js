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

		// Filter Party Type dynamically based on payment type (allows Customer, Supplier, Employee, Shareholder)
		frm.set_query("party_type", function (doc) {
			if (doc && doc.payment_type === "Pay") {
				return {
					filters: {
						name: ["in", ["Supplier", "Customer", "Employee"]],
					},
				};
			}
			return {
				filters: {
					name: ["in", ["Customer", "Supplier", "Shareholder", "Employee"]],
				},
			};
		});

		// Filter Party: if Supplier, only show non-transporter Suppliers
		frm.set_query("party", function (doc) {
			if (doc.party_type === "Supplier") {
				return {
					filters: {
						is_transporter: 0,
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

			if (!frm.doc.payment_type) {
				frm.set_value("payment_type", "Pay");
			}

			if (frm.doc.payment_type === "Pay" && !frm.doc.party_type) {
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

			if (frm.doc.payment_type === "Pay" && !frm.doc.party_type) {
				frm.set_value("party_type", "Supplier");
			}

			frm.add_custom_button(__("Fetch from Vendor PO"), function () {
				show_po_picker_for_payment_entry(frm);
			});
		}
	},

	payment_type: function (frm) {
		// Auto-align party_type based on payment_type switch
		if (frm.doc.payment_type === "Pay" && frm.doc.party_type === "Customer") {
			frm.set_value("party_type", "Supplier");
		} else if (frm.doc.payment_type === "Receive" && frm.doc.party_type === "Supplier") {
			frm.set_value("party_type", "Customer");
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

function show_po_picker_for_payment_entry(frm) {
	frappe.call({
		method: "sarveksha_erp.payment_tracking.payment_generator.get_pending_pos_for_vendor",
		args: {
			vendor: frm.doc.party_type === "Supplier" ? frm.doc.party : "",
			company: frm.doc.company || "",
		},
		freeze: true,
		freeze_message: __("Loading Vendor Purchase Orders..."),
		callback: function (r) {
			const pos = r.message || [];
			if (pos.length === 0) {
				frappe.msgprint(__("No pending approved Purchase Orders found for this Supplier/Company."));
				return;
			}

			const po_options = pos.map(function (p) {
				return p.display_name;
			});
			const po_map = {};
			pos.forEach(function (p) {
				po_map[p.display_name] = p;
			});

			const d = new frappe.ui.Dialog({
				title: __("Select Vendor Purchase Order"),
				fields: [
					{
						fieldname: "selected_po",
						label: __("Purchase Order"),
						fieldtype: "Select",
						options: po_options.join("\n"),
						default: po_options[0],
						reqd: 1,
					},
					{
						fieldname: "payment_target",
						label: __("Payment Target"),
						fieldtype: "Select",
						options: "Advance Payment\nRemaining Balance\nCustom Amount",
						default: "Advance Payment",
						reqd: 1,
					},
					{
						fieldname: "custom_amount",
						label: __("Amount"),
						fieldtype: "Currency",
						reqd: 1,
					},
				],
				primary_action_label: __("Apply to Payment Entry"),
				primary_action: function (values) {
					const chosen = po_map[values.selected_po];
					if (!chosen) return;

					frm.set_value("payment_type", "Pay");
					frm.set_value("party_type", "Supplier");
					frm.set_value("party", chosen.vendor);
					frm.set_value("company", chosen.company);
					frm.set_value("paid_amount", values.custom_amount);
					frm.set_value("received_amount", values.custom_amount);

					const po_label = chosen.ref_number || chosen.name;
					const remarks = `Payment of ${chosen.currency} ${values.custom_amount} against Vendor Purchase Order ${po_label} (${values.payment_target}) to ${chosen.vendor}`;
					if (frm.fields_dict.custom_remarks) {
						frm.set_value("custom_remarks", 1);
					}
					frm.set_value("remarks", remarks);
					if (frm.fields_dict.custom_vendor_purchase_order) {
						frm.set_value("custom_vendor_purchase_order", chosen.name);
					}
					if (frm.fields_dict.reference_no && !frm.doc.reference_no) {
						frm.set_value("reference_no", `TXN-${chosen.name}-${frappe.datetime.nowdate().replace(/-/g, "")}`);
						frm.set_value("reference_date", frappe.datetime.get_today());
					}

					d.hide();
					frappe.show_alert({
						message: __("Applied details from PO {0}", [po_label]),
						indicator: "green",
					});
				},
			});

			function update_dialog_amount() {
				const chosen = po_map[d.get_value("selected_po")];
				const target = d.get_value("payment_target");
				if (!chosen) return;

				if (target === "Advance Payment") {
					d.set_value("custom_amount", chosen.advance_amount || flt(chosen.grand_total * 0.3, 2));
				} else if (target === "Remaining Balance") {
					d.set_value("custom_amount", chosen.balance_due);
				}
			}

			d.fields_dict.selected_po.$input.on("change", update_dialog_amount);
			d.fields_dict.payment_target.$input.on("change", update_dialog_amount);

			d.show();
			update_dialog_amount();
		},
	});
}
