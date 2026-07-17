frappe.ui.form.on("Payment Batch", {
	refresh(frm) {
		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Process Payment Batch"), () => {
				frm.set_value("status", "Processing");
				frm.save_or_update();
			});
		} else if (frm.doc.status === "Processing") {
			frm.add_custom_button(__("Mark as Paid"), () => {
				frm.set_value("status", "Paid");
				frm.save_or_update();
				frappe.show_alert({message: __("Payment Batch marked as Paid"), indicator: "green"});
			});
		}
	}
});
