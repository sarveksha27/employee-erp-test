frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
		const roles = frappe.user_roles || [];
		const can_create_payment_entry =
			roles.includes("Accounts Clerk") ||
			roles.includes("Accounts Manager") ||
			roles.includes("Accounts User") ||
			roles.includes("System Manager") ||
			roles.includes("Administrator");

		if (
			frm.doc.vendor_purchase_order &&
			frm.doc.docstatus === 1 &&
			Number(frm.doc.outstanding_amount) > 0 &&
			can_create_payment_entry &&
			frappe.model.can_create("Payment Entry")
		) {
			frm.add_custom_button(__("Create Payment Entry"), function () {
				frappe.call({
					method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry",
					args: {
						dt: frm.doc.doctype,
						dn: frm.doc.name,
					},
					freeze: true,
					freeze_message: __("Preparing Payment Entry..."),
				}).then((response) => {
					const doclist = frappe.model.sync(response.message);
					frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
				});
			});
			frm.change_custom_button_type(__("Create Payment Entry"), null, "primary");
		}
	},
});