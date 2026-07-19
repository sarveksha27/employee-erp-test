// Copyright (c) 2026, Sarveksha Group and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sarveksha PI Container", {
	pi_number(frm) {
		if (frm.doc.pi_number) {
			frappe.db.get_doc("Sarveksha Purchase Order", frm.doc.pi_number)
				.then(po => {
					frm.set_value("company", po.company);
					frm.set_value("vendor", po.vendor);
					frm.set_value("equipment", po.equipment);
					if (po.container_number && !frm.doc.container_number) {
						frm.set_value("container_number", po.container_number);
					}
					if (po.port && !frm.doc.loading_port) {
						frm.set_value("loading_port", po.port);
					}
				});
		}
	}
});
