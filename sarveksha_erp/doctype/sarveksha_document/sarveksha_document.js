// Copyright (c) 2026, Sarveksha Group and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sarveksha Document", {
	purchase_order(frm) {
		if (frm.doc.purchase_order) {
			frappe.db.get_doc("Sarveksha Purchase Order", frm.doc.purchase_order)
				.then(po => {
					frm.set_value("vendor", po.vendor);
					frm.set_value("equipment", po.equipment);
					if (po.container_number && !frm.doc.container) {
						frm.set_value("container", po.container_number);
					}
				});
		}
	}
});
