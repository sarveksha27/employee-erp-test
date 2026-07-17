frappe.ui.form.on("Vendor Payment Request", {
	refresh(frm) {
		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Submit for Finance Review"), () => {
				frm.set_value("status", "Finance Review");
				frm.save_or_update();
			});
		} else if (frm.doc.status === "Finance Review") {
			frm.add_custom_button(__("Send for Approval"), () => {
				frm.set_value("status", "Under Approval");
				frm.save_or_update();
			});
		} else if (frm.doc.status === "Under Approval") {
			frm.add_custom_button(__("Approve"), () => {
				frappe.call({
					method: "frappe.client.insert",
					args: {
						doc: {
							doctype: "Payment Approval",
							payment_request: frm.doc.name,
							approver: frappe.session.user,
							approval_status: "Approved",
							approval_date: frappe.datetime.nowdate(),
							comments: "Approved via workflow."
						}
					},
					callback: function(r) {
						if (!r.exc) {
							frm.set_value("status", "Approved");
							frm.save_or_update();
							frappe.show_alert({message: __("Payment Approved"), indicator: "green"});
						}
					}
				});
			}, __("Actions"));

			frm.add_custom_button(__("Reject"), () => {
				frappe.prompt([
					{label: __("Comments"), fieldname: "comments", fieldtype: "Small Text", reqd: 1}
				], (values) => {
					frappe.call({
						method: "frappe.client.insert",
						args: {
							doc: {
								doctype: "Payment Approval",
								payment_request: frm.doc.name,
								approver: frappe.session.user,
								approval_status: "Rejected",
								approval_date: frappe.datetime.nowdate(),
								comments: values.comments
							}
						},
						callback: function(r) {
							if (!r.exc) {
								frm.set_value("status", "Rejected");
								frm.save_or_update();
								frappe.show_alert({message: __("Payment Rejected"), indicator: "red"});
							}
						}
					});
				}, __("Enter Rejection Reason"), __("Submit"));
			}, __("Actions"));
		}
	}
});
