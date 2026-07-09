// Copyright (c) 2026, Your Team Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERP Holiday List", {
	refresh(frm) {
		frm.set_value("total_holidays", (frm.doc.holidays || []).length);
	},
});
