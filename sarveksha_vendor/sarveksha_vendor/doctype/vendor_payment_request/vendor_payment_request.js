frappe.ui.form.on('Vendor Payment Request', {
	refresh: function(frm) {
		if (frm.doc.status === 'Approved' && frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Make Payment Entry'), function() {
				frappe.call({
					method: 'sarveksha_vendor.api.make_payment_entry',
					args: {
						source_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frappe.model.sync(r.message);
							frappe.set_route('Form', r.message.doctype, r.message.name);
						}
					}
				});
			});
		}
	}
});
