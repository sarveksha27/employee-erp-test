// Copyright (c) 2026, Sarveksha Group and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sarveksha Purchase Order", {
	setup(frm) {
		// Set query filters
		frm.set_query("company", function() {
			return {
				filters: {
					status: "Active"
				}
			};
		});

		frm.set_query("vendor", function() {
			return {
				filters: {
					status: "Active"
				}
			};
		});

		frm.set_query("equipment", function() {
			return {
				filters: {
					status: "Active"
				}
			};
		});
	},

	refresh(frm) {
		// Calculate totals on load
		frm.trigger("calculate_totals");
	},

	process_pdf(frm) {
		if (!frm.doc.import_pdf) {
			frappe.msgprint(__("Please upload a PDF file first."));
			return;
		}
		
		frappe.show_alert({message: __("Extracting data from PDF..."), indicator: "blue"});
		
		frm.call({
			method: "sarveksha_erp.sarveksha_erp.doctype.sarveksha_purchase_order.sarveksha_purchase_order.parse_po_pdf",
			args: {
				file_url: frm.doc.import_pdf
			},
			callback: function(r) {
				if (r.message) {
					let data = r.message;
					let updated_fields = [];
					
					for (let key in data) {
						if (data[key] !== undefined && data[key] !== null) {
							frm.set_value(key, data[key]);
							updated_fields.push(frm.fields_dict[key].df.label);
						}
					}
					
					if (updated_fields.length > 0) {
						frappe.show_alert({
							message: __("Auto-filled: {0}", [updated_fields.join(", ")]),
							indicator: "green"
						});
					} else {
						frappe.show_alert({
							message: __("No matching patterns found in PDF."),
							indicator: "orange"
						});
					}
					
					frm.trigger("calculate_totals");
				}
			}
		});
	},

	company(frm) {
		if (frm.doc.company) {
			frappe.db.get_doc("Sarveksha Company", frm.doc.company)
				.then(company => {
					frm.set_value("warehouse", company.default_warehouse);
					frm.set_value("company_bank", company.default_bank || "");
					frm.set_value("currency", company.currency);
					if (!frm.doc.payment_terms) {
						frm.set_value("payment_terms", company.default_payment_terms);
					}
				});
		}
	},

	vendor(frm) {
		if (frm.doc.vendor) {
			frappe.db.get_doc("Sarveksha Vendor", frm.doc.vendor)
				.then(vendor => {
					let bank_info = [
						vendor.bank_name ? `Bank: ${vendor.bank_name}` : "",
						vendor.branch ? `Branch: ${vendor.branch}` : "",
						vendor.account_number ? `A/C: ${vendor.account_number}` : "",
						vendor.ifsc ? `IFSC: ${vendor.ifsc}` : "",
						vendor.swift ? `SWIFT: ${vendor.swift}` : "",
						vendor.iban ? `IBAN: ${vendor.iban}` : ""
					].filter(Boolean).join("\n");
					
					frm.set_value("vendor_bank", bank_info);
					frm.set_value("payment_terms", vendor.payment_terms || frm.doc.payment_terms);
					if (vendor.currency) {
						frm.set_value("currency", vendor.currency);
					}
				});
		}
	},

	equipment(frm) {
		if (frm.doc.equipment) {
			frappe.db.get_doc("Sarveksha Equipment", frm.doc.equipment)
				.then(eq => {
					frm.set_value("unit", eq.unit_of_measure);
					frm.set_value("rate", eq.approximate_cost || eq.latest_purchase_cost || 0.0);
					if (eq.preferred_vendor && !frm.doc.vendor) {
						frm.set_value("vendor", eq.preferred_vendor);
					}
					// Auto calculate tax if GST is applicable
					if (eq.gst_percentage) {
						let qty = frm.doc.quantity || 1.0;
						let rate = eq.approximate_cost || 0.0;
						let base_val = qty * rate;
						let tax_val = base_val * (eq.gst_percentage / 100.0);
						frm.set_value("tax", tax_val);
					}
				});
		}
	},

	quantity(frm) {
		frm.trigger("calculate_totals");
	},

	rate(frm) {
		frm.trigger("calculate_totals");
	},

	discount(frm) {
		frm.trigger("calculate_totals");
	},

	tax(frm) {
		frm.trigger("calculate_totals");
	},

	freight(frm) {
		frm.trigger("calculate_totals");
	},

	packing(frm) {
		frm.trigger("calculate_totals");
	},

	insurance(frm) {
		frm.trigger("calculate_totals");
	},

	other_charges(frm) {
		frm.trigger("calculate_totals");
	},

	calculate_totals(frm) {
		let qty = flt(frm.doc.quantity || 0.0);
		let rate = flt(frm.doc.rate || 0.0);
		let discount = flt(frm.doc.discount || 0.0);
		let tax = flt(frm.doc.tax || 0.0);
		let freight = flt(frm.doc.freight || 0.0);
		let packing = flt(frm.doc.packing || 0.0);
		let insurance = flt(frm.doc.insurance || 0.0);
		let other = flt(frm.doc.other_charges || 0.0);

		let grand_total = (qty * rate) - discount + tax + freight + packing + insurance + other;
		frm.set_value("grand_total", grand_total);
	}
});
