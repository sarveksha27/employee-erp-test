frappe.ui.form.on("Vendor Contract", {
	refresh(frm) {
		if (frm.doc.status === "Active") {
			frm.set_intro(__("This contract is currently active."), "green");
		} else if (frm.doc.status === "Expired") {
			frm.set_intro(__("This contract has expired."), "red");
		}
	}
});
