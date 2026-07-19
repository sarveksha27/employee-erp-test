// Copyright (c) 2026, Sarveksha Group and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sarveksha Payment", {
	purchase_order(frm) {
		if (frm.doc.purchase_order) {
			frappe.db.get_doc("Sarveksha Purchase Order", frm.doc.purchase_order)
				.then(po => {
					frm.set_value("company", po.company);
					frm.set_value("vendor", po.vendor);
					frm.set_value("currency", po.currency);
					frm.set_value("exchange_rate", po.exchange_rate);
					
					// Prepopulate invoice details or stages if available
					if (po.proforma_invoice_number) {
						frm.set_value("invoice", po.proforma_invoice_number);
					}
					
					// Suggest payment amount based on stage if empty
					if (!frm.doc.amount) {
						if (frm.doc.payment_stage === "Advance") {
							frm.set_value("amount", po.advance_payment || 0.0);
						} else if (frm.doc.payment_stage === "Final") {
							frm.set_value("amount", po.final_payment || po.grand_total || 0.0);
						} else if (frm.doc.payment_stage === "Milestone") {
							frm.set_value("amount", po.second_payment || 0.0);
						}
					}
				});
		}
	},
	
	payment_stage(frm) {
		// Update suggestion if PO is selected
		if (frm.doc.purchase_order) {
			frm.trigger("purchase_order");
		}
	}
});
