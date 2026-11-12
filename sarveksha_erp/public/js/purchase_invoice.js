frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
		const roles = frappe.user_roles || [];
		const can_create_payment_entry =
			roles.includes("Accounts Manager") ||
			roles.includes("Accounts Clerk") ||
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
			frm.add_custom_button(__("Create Payment Entry"), () => {
				frappe
					.call({
						method: "sarveksha_erp.payment_tracking.payment_entry_workflow.create_payment_entry_from_purchase_invoice",
						args: {
							purchase_invoice_name: frm.doc.name,
						},
						freeze: true,
						freeze_message: __("Initializing Payment Entry..."),
					})
					.then((response) => {
						if (response.message) {
							frappe.set_route("Form", "Payment Entry", response.message);
						}
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
		if (schedule_grid && can_pay_milestones && frm.doc.docstatus === 1) {
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
		}

		render_payment_schedule_summary_and_badges(frm);
	},

	payment_terms_template(frm) {
		setTimeout(() => render_payment_schedule_summary_and_badges(frm), 500);
	},
});

frappe.ui.form.on("Payment Schedule", {
	payment_amount(frm) {
		render_payment_schedule_summary_and_badges(frm);
	},
	paid_amount(frm) {
		render_payment_schedule_summary_and_badges(frm);
	},
	due_date(frm) {
		render_payment_schedule_summary_and_badges(frm);
	},
});

function render_payment_schedule_summary_and_badges(frm) {
	if (!frm.fields_dict["payment_schedule"]) return;

	const schedule = frm.doc.payment_schedule || [];
	if (!schedule.length) {
		$("#milestone-schedule-summary-banner").remove();
		return;
	}

	let total_amount = 0.0;
	let total_paid = 0.0;
	let total_outstanding = 0.0;
	const today = frappe.datetime.get_today();

	schedule.forEach((row) => {
		const amt = flt(row.payment_amount);
		const paid = flt(row.paid_amount);
		const out = flt(row.outstanding || amt - paid);
		total_amount += amt;
		total_paid += paid;
		total_outstanding += out;
	});

	// 1. Render Financial Summary Banner
	let $wrapper = $(frm.fields_dict["payment_schedule"].wrapper);
	$("#milestone-schedule-summary-banner").remove();

	const banner_html = `
		<div id="milestone-schedule-summary-banner" style="display:flex; gap:16px; align-items:center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 16px; margin-bottom:12px;">
			<div style="flex:1;">
				<span style="font-size:11px; text-transform:uppercase; color:#64748b; font-weight:600;">Total Milestone Amount</span>
				<div style="font-size:16px; font-weight:700; color:#0f172a;">${format_currency(total_amount, frm.doc.currency)}</div>
			</div>
			<div style="width:1px; height:28px; background:#cbd5e1;"></div>
			<div style="flex:1;">
				<span style="font-size:11px; text-transform:uppercase; color:#16a34a; font-weight:600;">Total Paid</span>
				<div style="font-size:16px; font-weight:700; color:#15803d;">${format_currency(total_paid, frm.doc.currency)}</div>
			</div>
			<div style="width:1px; height:28px; background:#cbd5e1;"></div>
			<div style="flex:1;">
				<span style="font-size:11px; text-transform:uppercase; color:#dc2626; font-weight:600;">Remaining Outstanding</span>
				<div style="font-size:16px; font-weight:700; color:#b91c1c;">${format_currency(total_outstanding, frm.doc.currency)}</div>
			</div>
		</div>
	`;
	$wrapper.find(".grid-heading-row, .form-grid").first().before(banner_html);

	// 2. Render Row Status Badges
	const grid = frm.fields_dict["payment_schedule"].grid;
	if (grid && grid.grid_rows) {
		grid.grid_rows.forEach((grid_row) => {
			const doc = grid_row.doc;
			if (!doc) return;

			const amt = flt(doc.payment_amount);
			const paid = flt(doc.paid_amount);
			const outstanding = flt(doc.outstanding || amt - paid);
			const due_date = doc.due_date;

			let badge_color = "#3b82f6"; // blue
			let badge_bg = "#eff6ff";
			let badge_text = __("Upcoming");

			if (outstanding <= 0.0) {
				badge_color = "#16a34a"; // green
				badge_bg = "#f0fdf4";
				badge_text = __("Paid");
			} else if (due_date) {
				if (due_date === today) {
					badge_color = "#d97706"; // amber
					badge_bg = "#fffbeb";
					badge_text = __("Due Today");
				} else if (due_date < today) {
					badge_color = "#dc2626"; // red
					badge_bg = "#fef2f2";
					badge_text = __("Overdue");
				}
			}

			const $desc_col = grid_row.row.find("[data-fieldname='description']");
			$desc_col.find(".milestone-status-badge").remove();
			$desc_col.append(`
				<span class="milestone-status-badge" style="display:inline-block; margin-left:6px; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:600; color:${badge_color}; background:${badge_bg}; border:1px solid ${badge_color}33;">
					${badge_text}
				</span>
			`);
		});
	}
}
