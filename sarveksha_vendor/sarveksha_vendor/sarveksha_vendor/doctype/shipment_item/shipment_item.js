frappe.ui.form.on("Shipment Item", {
	quantity(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.quantity && row.unit_value) {
			frappe.model.set_value(cdt, cdn, "total_value", row.quantity * row.unit_value);
		}
	},
	unit_value(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.quantity && row.unit_value) {
			frappe.model.set_value(cdt, cdn, "total_value", row.quantity * row.unit_value);
		}
	}
});
