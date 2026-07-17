frappe.ui.form.on("Intercompany Transfer", {
	refresh(frm) {
		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Process Transfer"), () => {
				frm.set_value("status", "Pending");
				frm.save_or_update();
			});
		} else if (frm.doc.status === "Pending") {
			frm.add_custom_button(__("Mark Completed"), () => {
				frm.set_value("status", "Completed");
				frm.save_or_update();
				frappe.show_alert({message: __("Transfer Completed"), indicator: "green"});
			});
			frm.add_custom_button(__("Mark Failed"), () => {
				frm.set_value("status", "Failed");
				frm.save_or_update();
				frappe.show_alert({message: __("Transfer Failed"), indicator: "red"});
			});
		}
	}
});
