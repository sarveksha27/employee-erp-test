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
			(frm.doc.vendor_purchase_order || frm.doc.custom_vendor_purchase_order) &&
			frm.doc.docstatus === 1 &&
			Number(frm.doc.outstanding_amount) > 0 &&
			can_create_payment_entry &&
			frappe.model.can_create("Payment Entry")
		) {
			frm.add_custom_button(__("Create Payment Entry"), function () {
				frappe
					.call({
						method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry",
						args: {
							dt: frm.doc.doctype,
							dn: frm.doc.name,
						},
						freeze: true,
						freeze_message: __("Preparing Payment Entry..."),
					})
					.then((response) => {
						const doclist = frappe.model.sync(response.message);
						frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
					});
			});
			frm.change_custom_button_type(__("Create Payment Entry"), null, "primary");
		}

		const can_pay_milestones =
			roles.includes("Accounts Clerk") ||
			roles.includes("Accounts Manager") ||
			roles.includes("System Manager") ||
			roles.includes("Administrator");
		const schedule_grid = frm.fields_dict.payment_schedule?.grid;

		$(frm.wrapper).off("grid-row-render.sarveksha-milestone");
		if (!schedule_grid || !can_pay_milestones || frm.doc.docstatus !== 1) {
			return;
		}

		$(frm.wrapper).on("grid-row-render.sarveksha-milestone", (event, grid_row) => {
			if (grid_row.grid !== schedule_grid) {
				return;
			}

			const outstanding = Number(grid_row.doc.outstanding || 0);
			const $old_button = grid_row.row.find(".pay-milestone-action");
			if (outstanding <= 0 || !frappe.model.can_create("Payment Entry")) {
				$old_button.remove();
				return;
			}
			if ($old_button.length) {
				return;
			}

			$("<button>", {
				type: "button",
				class: "btn btn-xs btn-secondary pay-milestone-action",
				text: __("Pay Milestone"),
			})
				.appendTo($("<div>", { class: "col grid-static-col" }).appendTo(grid_row.row))
				.on("click", (click_event) => {
					click_event.preventDefault();
					click_event.stopPropagation();
					frappe
						.call({
							method: "sarveksha_erp.payment_tracking.milestone_payment_entry.make_milestone_payment_entry",
							args: {
								invoice_name: frm.doc.name,
								milestone_row_id: grid_row.doc.name,
							},
							freeze: true,
							freeze_message: __("Preparing milestone payment..."),
						})
						.then((response) => {
							if (response.message) {
								frappe.set_route("Form", "Payment Entry", response.message);
							}
						});
				});
		});

		schedule_grid.grid_rows?.forEach((grid_row) => {
			$(frm.wrapper).trigger("grid-row-render", [grid_row]);
		});
	},
});
