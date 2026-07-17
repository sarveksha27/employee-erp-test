frappe.ui.form.on("Payment Batch Entry", {
	payment_request(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.payment_request) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Vendor Payment Request",
					name: row.payment_request
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "vendor", r.message.vendor);
						frappe.model.set_value(cdt, cdn, "amount", r.message.amount);
					}
				}
			});
		}
	}
});
