// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vendor Purchase Order", {
	// ─── ON FORM LOAD ─────────────────────────────────────────
	refresh: function (frm) {
		const colors = {
			Draft: "gray",
			"Generated (Yet to be Verified)": "orange",
			"Verified (Yet to be approved)": "blue",
			Approved: "green",
			Cancelled: "red",
		};
		if (frm.doc.workflow_state && colors[frm.doc.workflow_state]) {
			frm.set_indicator_formatter("workflow_state", function (doc) {
				return colors[doc.workflow_state] || "gray";
			});
		}

		// Hide standard workflow actions menu
		if (frm.states) {
			frm.states.show_actions = function () {};
			frm.page.clear_actions_menu();
		}

		// Hide manual status and workflow_state selection fields from the form
		frm.toggle_display("status", false);
		frm.toggle_display("workflow_state", false);

		// Always lock PO Type so selection cannot be changed during drafting or editing
		frm.set_df_property("po_type", "read_only", 1);

		// Render custom buttons based on workflow state & user roles
		const state = frm.doc.workflow_state || "Draft";
		set_quotation_governance_access(frm, state);
		render_quotation_attachments(frm);
		set_entity_policy_filters(frm);
		const user_roles = frappe.user_roles;
		const is_admin =
			user_roles.includes("System Manager") || user_roles.includes("Administrator");

		// Helper function to apply workflow action
		const apply_action = function (action_name) {
			const is_dirty = Boolean(
				(frm.is_dirty && frm.is_dirty()) ||
				frm.doc.__unsaved ||
				frm.doc.__islocal
			);
			if (is_dirty) {
				frappe.msgprint(__("Please save changes before sending forward."));
				update_save_before_forward_guard(frm);
				return;
			}

			const execute_action = () => {
				frappe.dom.freeze();
				frappe
					.xcall("frappe.model.workflow.apply_workflow", {
						doc: frm.doc,
						action: action_name,
					})
					.then((doc) => {
						frappe.model.sync(doc);
						return frm.reload_doc();
					})
					.then(() => {
						frappe.show_alert({
							message: __("Action '{0}' applied successfully!", [action_name]),
							indicator: "green",
						});
					})
					.catch((err) => {
						frappe.msgprint(__("Error applying action: ") + (err.message || err));
					})
					.finally(() => {
						frappe.dom.unfreeze();
					});
			};

			execute_action();
		};

		// Clear existing custom buttons first
		frm.clear_custom_buttons();

		if (frm.doc.docstatus === 0) {
			if (state === "Draft" && (user_roles.includes("PO Generator") || is_admin)) {
				frm.add_custom_button(__("Send Forward"), function () {
					apply_action("Generate PO");
				});
				frm.change_custom_button_type(__("Send Forward"), null, "primary");
			} else if (
				state === "Generated (Yet to be Verified)" &&
				(user_roles.includes("PO Verifier") || is_admin)
			) {
				frm.add_custom_button(__("Send Forward"), function () {
					apply_action("Verify");
				});
				frm.change_custom_button_type(__("Send Forward"), null, "primary");

				frm.add_custom_button(__("Send Back"), function () {
					frappe.prompt(
						[
							{
								label: __("Reason / Corrective Action Required"),
								fieldname: "remarks",
								fieldtype: "Small Text",
								reqd: 1,
							},
						],
						function (values) {
							frm.set_value("verifier_comments", values.remarks);
							frm.save().then(() => {
								apply_action("Send Back");
							});
						},
						__("Send Back to Generator"),
						__("Submit"),
					);
				});
				frm.change_custom_button_type(__("Send Back"), null, "danger");
			} else if (
				state === "Verified (Yet to be approved)" &&
				(user_roles.includes("PO Approver") || is_admin)
			) {
				frm.add_custom_button(__("Send Forward"), function () {
					apply_action("Approve");
				});
				frm.change_custom_button_type(__("Send Forward"), null, "primary");

				frm.add_custom_button(__("Send Back"), function () {
					frappe.prompt(
						[
							{
								label: __("Reason / Corrective Action Required"),
								fieldname: "remarks",
								fieldtype: "Small Text",
								reqd: 1,
							},
						],
						function (values) {
							frm.set_value("approver_comments", values.remarks);
							frm.save().then(() => {
								apply_action("Send Back");
							});
						},
						__("Send Back to Verifier"),
						__("Submit"),
					);
				});
				frm.change_custom_button_type(__("Send Back"), null, "danger");
			}
		}

		// Allow Administrator/System Manager to permanently delete the PO
		if (is_admin && frm.doc.name && !frm.doc.__islocal) {
			frm.add_custom_button(__("Delete PO"), function () {
				frappe.confirm(
					__(
						"This will permanently delete Purchase Order {0}. This action cannot be undone. Continue?",
						[frm.doc.name],
					),
					function () {
						frappe.call({
							method: "frappe.client.delete",
							args: {
								doctype: "Vendor Purchase Order",
								name: frm.doc.name,
							},
							callback: function (r) {
								if (!r.exc) {
									frappe.show_alert({
										message: __("Purchase Order deleted successfully."),
										indicator: "green",
									});
									frappe.set_route("List", "Vendor Purchase Order");
								}
							},
						});
					},
				);
			});
			frm.change_custom_button_type(__("Delete PO"), null, "danger");
		}

		// Configure Print Button & Menu Visibility based on Workflow Stage and User Roles
		const is_approved = frm.doc.workflow_state === "Approved" || frm.doc.docstatus === 1;
		const can_print = is_approved && (user_roles.includes("PO Generator") || is_admin);

		// PI Generation Button for Internal POs (Only available on Internal PO, never on External/Vendor PO)
		if (
			is_approved &&
			frm.doc.po_type === "Internal PO" &&
			!frm.doc.__islocal &&
			frm.doc.name &&
			(user_roles.includes("PO Generator") || is_admin)
		) {
			frappe.db
				.get_value(
					"Proforma Invoice",
					{ internal_po: frm.doc.name, docstatus: ["!=", 2] },
					"name",
				)
				.then((r) => {
					const existing_pi = r && r.message && r.message.name;
					if (existing_pi) {
						frm.add_custom_button(__("View PI"), function () {
							frappe.set_route("Form", "Proforma Invoice", existing_pi);
						});
						frm.change_custom_button_type(__("View PI"), null, "info");

						frm.add_custom_button(__("Generate PI"), function () {
							frappe.show_alert({
								message: __(
									"Proforma Invoice {0} is already generated for this PO. Passing on to it.",
									[existing_pi],
								),
								indicator: "blue",
							});
							frappe.set_route("Form", "Proforma Invoice", existing_pi);
						});
					} else {
						frm.add_custom_button(__("Generate PI"), function () {
							frappe.db
								.get_value(
									"Proforma Invoice",
									{ internal_po: frm.doc.name, docstatus: ["!=", 2] },
									"name",
								)
								.then((res) => {
									const curr_pi = res && res.message && res.message.name;
									if (curr_pi) {
										frappe.show_alert({
											message: __(
												"Proforma Invoice {0} is already generated for this PO. Passing on to it.",
												[curr_pi],
											),
											indicator: "blue",
										});
										frappe.set_route("Form", "Proforma Invoice", curr_pi);
									} else {
										frappe.model.with_doctype("Proforma Invoice", function () {
											const new_pi =
												frappe.model.get_new_doc("Proforma Invoice");
											new_pi.internal_po = frm.doc.name;
											frappe.set_route(
												"Form",
												"Proforma Invoice",
												new_pi.name,
											);
										});
									}
								});
						});
						frm.change_custom_button_type(__("Generate PI"), null, "info");
					}
				});
		}

		const open_compiled_pdf = function () {
			const pdf_url = frappe.urllib.get_full_url(
				`/api/method/frappe.utils.print_format.download_pdf?doctype=Vendor%20Purchase%20Order&name=${encodeURIComponent(frm.doc.name)}`,
			);
			window.open(pdf_url, "_blank");
		};

		if (can_print) {
			frm.add_custom_button(__("Print PO"), open_compiled_pdf);
			frm.change_custom_button_type(__("Print PO"), null, "primary");

			// Intercept standard Frappe print actions
			frm.print_doc = open_compiled_pdf;
		}

		if (!can_print) {
			frm.page.hide_menu_item(__("Print"));
			frm.page.hide_menu_item(__("PDF"));
			if (frm.page.btn_print) frm.page.btn_print.hide();
			if (frm.page.set_print_btn_display) frm.page.set_print_btn_display(false);
		} else {
			frm.page.show_menu_item(__("Print"));
			frm.page.show_menu_item(__("PDF"));
			if (frm.page.btn_print) frm.page.btn_print.show();
			if (frm.page.set_print_btn_display) frm.page.set_print_btn_display(true);

			setTimeout(() => {
				if (frm.page) {
					frm.page.menu
						.find('[data-label="Print"]')
						.off("click")
						.on("click", function (e) {
							e.preventDefault();
							e.stopPropagation();
							open_compiled_pdf();
						});
					frm.page.menu
						.find('[data-label="PDF"]')
						.off("click")
						.on("click", function (e) {
							e.preventDefault();
							e.stopPropagation();
							open_compiled_pdf();
						});
				}
			}, 300);
		}

		// Hide "+ New" button for Verifiers/Approvers in Form View
		if (!is_admin && frappe.session.user !== "Administrator") {
			const is_verifier_or_approver =
				user_roles.includes("PO Verifier") || user_roles.includes("PO Approver");
			const is_generator = user_roles.includes("PO Generator");

			if (is_verifier_or_approver && !is_generator) {
				frm.page.hide_menu_item(__("New"));
				frm.page.clear_secondary_action();
			}
		}

		// Configure Verification & Approval Panel Dynamic Controls
		setup_verification_approval_panel(frm);
		apply_dynamic_field_locks(frm);

		// Lock Currency and Exchange Rate: evaluate whether user has System Manager or Administrator
		const has_currency_admin_access =
			user_roles.includes("System Manager") ||
			user_roles.includes("Administrator") ||
			frappe.session.user === "Administrator";
		if (!has_currency_admin_access) {
			frm.set_df_property("currency", "read_only", 1);
			frm.set_df_property("exchange_rate", "read_only", 1);
		} else {
			frm.set_df_property("currency", "read_only", 0);
			frm.set_df_property("exchange_rate", "read_only", 0);
		}

		// Lock Price Inputs for Verifiers and Approvers
		lock_price_inputs_for_reviewers(frm);

		// Payment Section Locking
		toggle_payment_section(frm);

		// Save-Before-Forward Guard
		bind_workflow_action_guard(frm);
		update_save_before_forward_guard(frm);

		// Render custom remarks and revision number in the sidebar
		render_sidebar_custom_info(frm);

		// Recalculate on every refresh to keep values consistent
		calculate_gst_and_totals(frm);
		set_port_filter(frm);

		// Auto-detect letterhead if not set
		if (!frm.doc.letter_head && frm.doc.company) {
			frm.trigger("company");
		}

		// Display standard terms preview on load
		if (frm.doc.standard_terms) {
			frm.trigger("standard_terms");
		} else {
			frm.set_df_property("terms_preview", "options", "");
		}

		// Set up Shipment Subtype visibility and options
		handle_shipment_type_change(frm);

		// Render Workflow Activity History
		render_workflow_activity_history(frm);
	},

	// ─── COMPANY TRIGGER ──────────────────────────────────────
	company: function (frm) {
		if (!frm.doc.company) return;

		frappe.call({
			method: "sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order.get_company_details",
			args: { company: frm.doc.company },
			callback: function (r) {
				if (r.message) {
					const data = r.message;
					if (data.default_port) {
						frm.set_value("default_port", data.default_port);
						set_port_filter(frm);
						const first_port = data.default_port.split(",")[0].trim();
						frappe.db.exists("Port", first_port).then((exists) => {
							if (exists) {
								frm.set_value("port", first_port);
							}
						});
					}
					if (data.currency) {
						frm.set_value("currency", data.currency);
					}
					frm.set_value("company_gstin", data.company_gstin);
					frm.set_value("company_pan", data.company_pan);
					frm.set_value("company_address", data.company_address);
					frm.set_value("letter_head", data.letter_head);

					// Auto-select standard terms if not already set
					if (!frm.doc.standard_terms || frm.doc.standard_terms.length === 0) {
						const company_name = (frm.doc.company || "").toLowerCase();
						let terms_to_add = [];
						if (frm.doc.is_lut_applicable) {
							terms_to_add.push("LUT Certificate Terms");
						}

						if (company_name.includes("bstp"))
							terms_to_add.push("Guinea BSTP SAS Procurement Terms");
						else if (company_name.includes("mining") || company_name.includes("baani"))
							terms_to_add.push("Cameroon Mining & Minerals Terms");
						else if (company_name.includes("sl limited"))
							terms_to_add.push("Sierra Leone Procurement Terms");
						else if (company_name.includes("botswana"))
							terms_to_add.push("Botswana Mining & Equipment Terms");

						if (!terms_to_add.includes("Standard Export PO Terms")) {
							terms_to_add.push("Standard Export PO Terms");
						}

						frm.set_value(
							"standard_terms",
							terms_to_add.map((t) => ({ standard_term: t })),
						);
						frm.trigger("standard_terms");
					}
				}
				calculate_gst_and_totals(frm);
			},
		});
	},

	// ─── ON FORM LOAD / INITIALIZATION ───────────────────────
	onload: function (frm) {
		if (frm.is_new()) {
			let po_category =
				frappe.route_options &&
				(frappe.route_options.po_category || frappe.route_options.po_type);
			if (!po_category && window.location.search) {
				let params = new URLSearchParams(window.location.search);
				po_category = params.get("po_category") || params.get("po_type");
			}
			if (po_category) {
				if (po_category.includes("Internal")) {
					frm.set_value("po_type", "Internal PO");
					frm.set_value("vendor", "Sarveksha Realty and Inframine LLP");
				} else if (po_category.includes("External") || po_category.includes("Vendor")) {
					frm.set_value("po_type", "Vendor PO");
				}
			}
		}
	},

	onload_post_render: function (frm) {
		render_workflow_activity_history(frm);
	},

	// ─── VENDOR TRIGGER ───────────────────────────────────────
	vendor: function (frm) {
		if (!frm.doc.vendor) {
			frm.set_value("vendor_address", "");
			return;
		}

		frappe.call({
			method: "sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order.get_supplier_payment_details",
			args: { supplier: frm.doc.vendor },
			callback: function (r) {
				if (r.message) {
					const data = r.message;
					if (data.tax_id) frm.set_value("vendor_gstin", data.tax_id);
					if (data.custom_pan) frm.set_value("vendor_pan", data.custom_pan);
					if (data.custom_bank_name)
						frm.set_value("vendor_bank_name", data.custom_bank_name);
					if (data.custom_account_number)
						frm.set_value("vendor_account_number", data.custom_account_number);
					if (data.custom_ifsc) frm.set_value("vendor_ifsc", data.custom_ifsc);
					if (data.vendor_address !== undefined)
						frm.set_value("vendor_address", data.vendor_address);

					frm._vendor_gstin = data.tax_id || "";

					// Populate Payment Terms & Advance Percentage
					if (data.payment_terms_description) {
						frm.set_value("payment_terms", data.payment_terms_description);
					}
					if (data.advance_percentage !== undefined) {
						frm.set_value("advance_percentage", data.advance_percentage);
					}

					calculate_gst_and_totals(frm);
				}
			},
		});
	},

	shipment_type: function (frm) {
		handle_shipment_type_change(frm);
	},

	// ─── PRICING TRIGGERS ─────────────────────────────────────
	freight: function (frm) {
		calculate_gst_and_totals(frm);
	},
	insurance: function (frm) {
		calculate_gst_and_totals(frm);
	},
	packing_charges: function (frm) {
		calculate_gst_and_totals(frm);
	},
	other_charges: function (frm) {
		calculate_gst_and_totals(frm);
	},
	advance_percentage: function (frm) {
		calculate_gst_and_totals(frm);
	},
	payment_status: function (frm) {
		sync_payment_status_display(frm);
	},
	vendor_gstin: function (frm) {
		calculate_gst_and_totals(frm);
	},
	is_lut_applicable: function (frm) {
		if (frm.doc.is_lut_applicable) {
			frm.set_value("standard_terms", [{ standard_term: "LUT Certificate Terms" }]);
			frm.trigger("standard_terms");
		}
		calculate_gst_and_totals(frm);
	},

	po_type: function (frm) {
		set_entity_policy_filters(frm);
		// Recalculate whenever PO Type changes (External vs Internal)
		// This shows/hides margin fields and updates grand total
		calculate_gst_and_totals(frm);
		frm.refresh_fields([
			"sec_internal_margin",
			"internal_margin_percentage",
			"internal_margin_amount",
			"logistics_cost",
		]);
	},

	internal_margin_percentage: function (frm) {
		calculate_gst_and_totals(frm);
	},
	// ─── INDIVIDUAL EQUIPMENT ENTRY TRIGGERS ──────────────────
	equipment: function (frm) {
		if (!frm.doc.equipment) return;

		frappe.db.get_value(
			"Equipment",
			frm.doc.equipment,
			[
				"equipment_name",
				"hsn_code",
				"brand",
				"manufacturer",
				"unit",
				"specification",
				"approx_cost_inr",
				"last_purchase_cost_inr",
				"gst_percentage",
			],
			function (r) {
				if (r) {
					frm.set_value("equipment_name", r.equipment_name || "");
					frm.set_value("hsn_code", r.hsn_code || "");
					frm.set_value("brand", r.brand || "");
					frm.set_value("manufacturer", r.manufacturer || "");
					frm.set_value("unit", r.unit || "Nos");
					frm.set_value("specification", r.specification || "");

					const cost = flt(r.approx_cost_inr) || flt(r.last_purchase_cost_inr) || 10000;
					const gst_pct = flt(r.gst_percentage) || 18;

					frm.set_value("rate", cost);
					frm.set_value("gst_percentage", gst_pct);
				}
			},
		);
	},

	add_equipment_btn: function (frm) {
		if (!frm.doc.equipment && !frm.doc.equipment_name) {
			frappe.msgprint(
				__(
					"Please select an Equipment Code or enter Equipment Name before adding to table.",
				),
			);
			return;
		}

		let item = frm.add_child("items");
		item.equipment = frm.doc.equipment || "";
		item.equipment_name = frm.doc.equipment_name || "";
		item.hsn_code = frm.doc.hsn_code || "";
		item.brand = frm.doc.brand || "";
		item.manufacturer = frm.doc.manufacturer || "";
		item.quantity = flt(frm.doc.quantity) || 1;
		item.unit = frm.doc.unit || "Nos";
		item.rate = flt(frm.doc.rate) || 0;
		item.discount_percent = flt(frm.doc.discount_percent) || 0;
		item.gst_percentage = flt(frm.doc.gst_percentage) || 18;
		item.specification = frm.doc.specification || "";

		frm.refresh_field("items");
		calculate_gst_and_totals(frm);

		// Reset individual input fields for next entry
		frm.set_value("equipment", "");
		frm.set_value("equipment_name", "");
		frm.set_value("hsn_code", "");
		frm.set_value("brand", "");
		frm.set_value("manufacturer", "");
		frm.set_value("quantity", 1);
		frm.set_value("rate", 0);
		frm.set_value("specification", "");

		frappe.show_alert({
			message: __("Equipment item added to order table!"),
			indicator: "green",
		});
	},

	standard_terms: function (frm) {
		if (frm.doc.standard_terms && frm.doc.standard_terms.length > 0) {
			const terms_list = frm.doc.standard_terms
				.map((row) => row.standard_term)
				.filter(Boolean);
			if (terms_list.length > 0) {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Terms and Conditions",
						filters: { name: ["in", terms_list] },
						fields: ["name", "terms"],
						limit: 50,
					},
					callback: function (r) {
						if (r.message && r.message.length > 0) {
							const terms_map = {};
							r.message.forEach((item) => {
								terms_map[item.name] = item.terms;
							});
							let concatenated_terms = "";
							terms_list.forEach((t_name, idx) => {
								if (terms_map[t_name]) {
									concatenated_terms += `<h3>${idx + 1}. ${t_name}</h3>${terms_map[t_name]}<br><hr>`;
								}
							});
							frm.set_df_property("terms_preview", "options", concatenated_terms);
						} else {
							frm.set_df_property("terms_preview", "options", "");
						}
					},
				});
			} else {
				frm.set_df_property("terms_preview", "options", "");
			}
		} else {
			frm.set_df_property("terms_preview", "options", "");
		}
	},

	after_save: function (frm) {
		update_save_before_forward_guard(frm);
		render_workflow_activity_history(frm);
	},

	on_change: function (frm) {
		update_save_before_forward_guard(frm);
	},
});

// ─── CHILD TABLE GRID TRIGGERS (Vendor Purchase Order Item) ───
frappe.ui.form.on("Vendor Purchase Order Item", {
	equipment: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.equipment) return;

		frappe.db.get_value(
			"Equipment",
			row.equipment,
			[
				"equipment_name",
				"hsn_code",
				"brand",
				"manufacturer",
				"unit",
				"specification",
				"approx_cost_inr",
				"last_purchase_cost_inr",
				"gst_percentage",
			],
			function (r) {
				if (r) {
					frappe.model.set_value(cdt, cdn, "equipment_name", r.equipment_name || "");
					frappe.model.set_value(cdt, cdn, "hsn_code", r.hsn_code || "");
					frappe.model.set_value(cdt, cdn, "brand", r.brand || "");
					frappe.model.set_value(cdt, cdn, "manufacturer", r.manufacturer || "");
					frappe.model.set_value(cdt, cdn, "unit", r.unit || "Nos");
					frappe.model.set_value(cdt, cdn, "specification", r.specification || "");

					const cost = flt(r.approx_cost_inr) || flt(r.last_purchase_cost_inr) || 10000;
					const gst_pct = flt(r.gst_percentage) || 18;

					frappe.model.set_value(cdt, cdn, "rate", cost);
					frappe.model.set_value(cdt, cdn, "gst_percentage", gst_pct);

					calculate_gst_and_totals(frm);
					update_save_before_forward_guard(frm);
				}
			},
		);
	},

	quantity: function (frm, cdt, cdn) {
		calculate_gst_and_totals(frm);
		update_save_before_forward_guard(frm);
	},
	rate: function (frm, cdt, cdn) {
		calculate_gst_and_totals(frm);
		update_save_before_forward_guard(frm);
	},
	discount_percent: function (frm, cdt, cdn) {
		calculate_gst_and_totals(frm);
		update_save_before_forward_guard(frm);
	},
	gst_percentage: function (frm, cdt, cdn) {
		calculate_gst_and_totals(frm);
		update_save_before_forward_guard(frm);
	},
	items_remove: function (frm) {
		calculate_gst_and_totals(frm);
		update_save_before_forward_guard(frm);
	},
});

// ─── MASTER CALCULATION ENGINE ────────────────────────────────
// ─── MASTER CALCULATION ENGINE ────────────────────────────────
function calculate_gst_and_totals(frm) {
	const is_lut = frm.doc.is_lut_applicable;
	const is_internal = (frm.doc.po_type || "") === "Internal PO";

	let total_taxable_value = 0;
	let total_item_tax = 0;

	// We need to handle LUT reversion asynchronously for items with Equipment master
	// To keep it synchronous-safe, we collect items needing reversion and use a queue
	const reversion_promises = [];

	if (frm.doc.items && frm.doc.items.length > 0) {
		frm.doc.items.forEach((row) => {
			if (is_lut) {
				row.gst_percentage = 0.1;
			} else {
				// ── LUT REVERSION ─────────────────────────────────────────────
				// If the item's GST% is exactly 0.1, it was set by LUT.
				// Restore from Equipment master (async but we handle it after)
				if (flt(row.gst_percentage) === 0.1 && row.equipment) {
					reversion_promises.push(
						frappe.db
							.get_value("Equipment", row.equipment, "gst_percentage")
							.then((r) => {
								const master_gst =
									r && r.message && flt(r.message.gst_percentage) > 0
										? flt(r.message.gst_percentage)
										: 18.0;
								row.gst_percentage = master_gst;
							}),
					);
				}
			}
		});
	}

	const _do_calculate = () => {
		let tv = 0;
		let tt = 0;

		if (frm.doc.items && frm.doc.items.length > 0) {
			frm.doc.items.forEach((row) => {
				const rate = flt(row.rate) || 0;
				const qty = flt(row.quantity) || 1;
				const discount_pct = flt(row.discount_percent) || 0;
				const gst_pct = flt(row.gst_percentage) || 0;

				const base_amount = rate * qty;
				const discount_amount = base_amount * (discount_pct / 100);
				const taxable_amount = base_amount - discount_amount;
				const tax_amount = taxable_amount * (gst_pct / 100);
				const total_amount = taxable_amount + tax_amount;

				row.taxable_amount = flt(taxable_amount, 2);
				row.tax_amount = flt(tax_amount, 2);
				row.total_amount = flt(total_amount, 2);

				tv += row.taxable_amount;
				tt += row.tax_amount;
			});
			frm.refresh_field("items");
		}

		total_taxable_value = tv;
		total_item_tax = tt;

		const freight = flt(frm.doc.freight) || 0;
		const insurance = flt(frm.doc.insurance) || 0;
		const packing = flt(frm.doc.packing_charges) || 0;
		const other = flt(frm.doc.other_charges) || 0;
		const advance_pct = flt(frm.doc.advance_percentage) || 0;

		// Logistics cost aggregation
		const logistics_cost = flt(freight + insurance + packing + other, 2);

		// Check if Child Company is selected (Remove GST components)
		const is_child_co =
			frm.doc.company && frm.doc.company !== "Sarveksha Realty and Inframine LLP";

		let gst_type = "IGST";
		let cgst = 0,
			sgst = 0,
			igst = 0;

		if (is_child_co) {
			gst_type = "";
			total_item_tax = 0;
			if (frm.doc.items && frm.doc.items.length > 0) {
				frm.doc.items.forEach((row) => {
					row.gst_percentage = 0;
					row.tax_amount = 0;
					row.total_amount = row.taxable_amount;
				});
				frm.refresh_field("items");
			}
			frm.toggle_display(
				["gst_type", "cgst_amount", "sgst_amount", "igst_amount", "tax_amount", "sec_tax"],
				false,
			);
		} else {
			frm.toggle_display(
				["gst_type", "cgst_amount", "sgst_amount", "igst_amount", "tax_amount", "sec_tax"],
				true,
			);
			if (is_lut) {
				gst_type = "IGST";
				igst = total_item_tax;
			} else if (
				vendor_gstin.length >= 2 &&
				company_gstin.length >= 2 &&
				vendor_gstin.substring(0, 2) === company_gstin.substring(0, 2)
			) {
				gst_type = "CGST + SGST";
				cgst = total_item_tax / 2;
				sgst = total_item_tax / 2;
			} else {
				gst_type = "IGST";
				igst = total_item_tax;
			}
		}

		// Internal Margin (Internal PO only: 5% - 30%)
		let internal_margin_amount = 0;
		let internal_margin_pct = 0;
		if (is_internal) {
			internal_margin_pct = flt(frm.doc.internal_margin_percentage) || 5.0;
			internal_margin_amount = flt(
				(total_taxable_value + logistics_cost) * (internal_margin_pct / 100),
				2,
			);
		}

		const grand_total = flt(
			total_taxable_value + total_item_tax + logistics_cost + internal_margin_amount,
			2,
		);
		const advance_amount = flt(grand_total * (advance_pct / 100), 2);
		const balance_due = flt(grand_total - advance_amount, 2);

		frm.set_value("taxable_value", flt(total_taxable_value, 2));
		frm.set_value("logistics_cost", logistics_cost);
		frm.set_value("gst_type", gst_type);
		frm.set_value("cgst_amount", flt(cgst, 2));
		frm.set_value("sgst_amount", flt(sgst, 2));
		frm.set_value("igst_amount", flt(igst, 2));
		frm.set_value("tax_amount", flt(total_item_tax, 2));

		// ── RUNNING TOTALS ────────────────────────────────────────────────────
		const cumulative_items_total = flt(total_taxable_value, 2);
		const cumulative_after_tax = flt(total_taxable_value + total_item_tax, 2);
		const cumulative_after_logistics = flt(cumulative_after_tax + logistics_cost, 2);
		frm.set_value("cumulative_items_total", cumulative_items_total);
		frm.set_value("cumulative_after_tax", cumulative_after_tax);
		frm.set_value("cumulative_after_logistics", cumulative_after_logistics);

		// ── INTERNAL PO: Hide tax section entirely ───────────────────────────
		const is_tax_exempt = is_internal || is_child_co;
		frm.toggle_display(
			[
				"sec_pricing",
				"is_lut_applicable",
				"gst_percentage",
				"gst_type",
				"cgst_amount",
				"sgst_amount",
				"igst_amount",
				"tax_amount",
				"cumulative_after_tax",
			],
			!is_tax_exempt,
		);
		if (is_tax_exempt) {
			// Clear LUT and tax inputs to avoid confusion
			frm.set_value("is_lut_applicable", 0);
			frm.set_value("gst_type", "");
			frm.set_value("cgst_amount", 0);
			frm.set_value("sgst_amount", 0);
			frm.set_value("igst_amount", 0);
			frm.set_value("tax_amount", 0);
		}

		if (is_internal) {
			frm.set_value("internal_margin_percentage", internal_margin_pct);
			frm.set_value("internal_margin_amount", internal_margin_amount);
		} else {
			frm.set_value("internal_margin_percentage", 0);
			frm.set_value("internal_margin_amount", 0);
		}
		frm.set_value("grand_total", grand_total);
		frm.set_value("advance_amount", advance_amount);
		frm.set_value("balance_due", balance_due);
	};

	// If there are LUT reversion fetches pending, wait for them then calculate
	if (reversion_promises.length > 0) {
		Promise.all(reversion_promises).then(_do_calculate);
	} else {
		_do_calculate();
	}
}

function set_port_filter(frm) {
	frm.set_query("port", function () {
		if (frm.doc.default_port) {
			const ports = frm.doc.default_port
				.split(",")
				.map((p) => p.trim())
				.filter(Boolean);
			if (ports.length > 0) {
				return { filters: [["Port", "name", "in", ports]] };
			}
		}
		return { filters: { is_active: 1 } };
	});
}

function setup_verification_approval_panel(frm) {
	const user_roles = frappe.user_roles;
	const has_verifier_role =
		user_roles.includes("PO Verifier") ||
		user_roles.includes("System Manager") ||
		user_roles.includes("Administrator");
	const has_approver_role =
		user_roles.includes("PO Approver") ||
		user_roles.includes("System Manager") ||
		user_roles.includes("Administrator");
	const is_admin = user_roles.includes("System Manager") || user_roles.includes("Administrator");

	const state = frm.doc.workflow_state || "Draft";

	// 1. Enable/Disable entire form based on active role allowed to edit in current state
	let can_edit = false;
	if (is_admin) {
		can_edit = true;
	} else if (state === "Draft" && user_roles.includes("PO Generator")) {
		can_edit = true;
	} else if (state === "Generated (Yet to be Verified)" && user_roles.includes("PO Verifier")) {
		can_edit = true;
	} else if (state === "Verified (Yet to be approved)" && user_roles.includes("PO Approver")) {
		can_edit = true;
	}

	if (can_edit) {
		frm.enable_form();
	} else {
		frm.disable_form();
		frm.dashboard.clear_comment_input();
	}

	// 2. Verifier comments: ONLY editable during 'Generated (Yet to be Verified)' stage by authorized verifiers
	if (state === "Generated (Yet to be Verified)" && has_verifier_role && can_edit) {
		frm.set_df_property("verifier_comments", "read_only", 0);
	} else {
		frm.set_df_property("verifier_comments", "read_only", 1);
	}

	// 3. Approver comments: ONLY editable during 'Verified (Yet to be approved)' stage by authorized approvers
	if (state === "Verified (Yet to be approved)" && has_approver_role && can_edit) {
		frm.set_df_property("approver_comments", "read_only", 0);
	} else {
		frm.set_df_property("approver_comments", "read_only", 1);
	}

	// 4. Ensure audit metadata fields are permanently read-only
	[
		"verified_by",
		"verified_on",
		"verifier_status",
		"approved_by",
		"approved_on",
		"approver_status",
		"prepared_by",
		"signatory",
	].forEach((field) => {
		frm.set_df_property(field, "read_only", 1);
	});
}

function apply_dynamic_field_locks(frm) {
	const user_roles = frappe.user_roles || [];
	const is_admin =
		user_roles.includes("System Manager") ||
		user_roles.includes("Administrator") ||
		frappe.session.user === "Administrator";
	const state = frm.doc.workflow_state || "Draft";
	const is_reviewer = user_roles.includes("PO Verifier") || user_roles.includes("PO Approver");

	// 1. Payment section locking
	toggle_payment_section(frm);

	// 2. Currency and exchange rate locking
	["currency", "exchange_rate"].forEach((fieldname) => {
		frm.set_df_property(fieldname, "read_only", is_admin ? 0 : 1);
	});

	// 3. Price inputs locking for verifiers and approvers
	lock_price_inputs_for_reviewers(frm);

	const lock_reviewer_inputs = !is_admin && is_reviewer && state !== "Draft";
	const reviewer_fields = [
		"rate",
		"discount_percent",
		"freight",
		"insurance",
		"packing_charges",
		"other_charges",
		"internal_margin_percentage",
		"expected_delivery",
		"expected_delivery_time",
		"delivery_location",
		"warehouse",
		"port",
		"cha",
		"shipment_type",
		"shipment_subtype",
		"container_number",
		"invoice_doc",
		"shipping_bill",
		"bill_of_lading",
		"packing_list",
		"commercial_invoice",
		"certificate_of_origin",
		"inspection_report",
		"insurance_doc",
		"cfa_doc",
	];
	reviewer_fields.forEach((fieldname) => {
		if (frm.get_field(fieldname)) {
			frm.set_df_property(fieldname, "read_only", lock_reviewer_inputs ? 1 : 0);
		}
	});

	const items_grid = frm.get_field("items") && frm.get_field("items").grid;
	if (items_grid) {
		frm.set_df_property("items", "read_only", lock_reviewer_inputs ? 1 : 0);
		items_grid.cannot_add_rows = lock_reviewer_inputs;
		items_grid.cannot_delete_rows = lock_reviewer_inputs;
		["rate", "discount_percent"].forEach((fieldname) => {
			items_grid.update_docfield_property(
				fieldname,
				"read_only",
				lock_reviewer_inputs ? 1 : 0,
			);
		});
		items_grid.refresh();
	}

	// 4. Re-apply reviewers price locking on items_grid if needed
	lock_price_inputs_for_reviewers(frm);

	bind_workflow_action_guard(frm);
	update_save_before_forward_guard(frm);
}

function toggle_payment_section(frm) {
	const user_roles = frappe.user_roles || [];
	const has_accounts_or_admin =
		user_roles.includes("Accounts User") ||
		user_roles.includes("Accounts Manager") ||
		user_roles.includes("System Manager") ||
		user_roles.includes("Administrator") ||
		frappe.session.user === "Administrator";

	const is_allowed =
		frm.doc.workflow_state === "Approved" && has_accounts_or_admin;

	const target_fields = [
		"payment_status",
		"advance_paid",
		"balance_due",
		"payment_pending",
		"payment_partially_paid",
		"payment_fully_paid",
		"advance_percentage",
		"payment_terms",
	];

	target_fields.forEach((field) => {
		if (frm.get_field(field)) {
			frm.set_df_property(field, "read_only", is_allowed ? 0 : 1);
		}
	});

	["advance_amount", "company_bank"].forEach((field) => {
		if (frm.get_field(field)) {
			frm.set_df_property(field, "read_only", is_allowed ? 0 : 1);
		}
	});
}

function lock_price_inputs_for_reviewers(frm) {
	const user_roles = frappe.user_roles || [];
	const has_verifier_or_approver =
		user_roles.includes("PO Verifier") || user_roles.includes("PO Approver");
	const has_generator_or_sys_mgr =
		user_roles.includes("PO Generator") ||
		user_roles.includes("System Manager") ||
		user_roles.includes("Administrator") ||
		frappe.session.user === "Administrator";

	if (has_verifier_or_approver && !has_generator_or_sys_mgr) {
		const items_grid = frm.get_field("items") && frm.get_field("items").grid;
		if (items_grid) {
			["rate", "base_rate"].forEach((col) => {
				items_grid.update_docfield_property(col, "read_only", 1);
			});
			items_grid.refresh();
		}

		const logistics_fields = [
			"ocean_air_freight_charges",
			"customs_clearance_charges",
			"inland_transportation_charges",
			"insurance_charges",
			"packaging_forwarding_charges",
			"other_incidental_charges",
			"discount_amount",
			"freight",
			"insurance",
			"packing_charges",
			"other_charges",
			"discount_percent",
		];
		logistics_fields.forEach((field) => {
			if (frm.get_field(field)) {
				frm.set_df_property(field, "read_only", 1);
			}
		});
	}
}

function sync_payment_status_display(frm) {
	const status = frm.doc.payment_status || "Pending";
	const status_values = {
		payment_pending: status === "Pending" ? 1 : 0,
		payment_partially_paid: ["Advance Paid", "Partially Paid"].includes(status) ? 1 : 0,
		payment_fully_paid: status === "Fully Paid" ? 1 : 0,
	};

	Object.entries(status_values).forEach(([fieldname, value]) => {
		if (frm.doc[fieldname] !== value) {
			frm.set_value(fieldname, value);
		}
	});
}

function bind_workflow_action_guard(frm) {
	if (!frm.wrapper) return;

	frm.wrapper.off("input.vpo-workflow-guard change.vpo-workflow-guard");
	frm.wrapper.on("input.vpo-workflow-guard change.vpo-workflow-guard", function () {
		update_save_before_forward_guard(frm);
	});
}

function update_save_before_forward_guard(frm) {
	if (!frm.page || !frm.page.wrapper) return;

	const is_dirty = Boolean(
		(frm.is_dirty && frm.is_dirty()) ||
		frm.doc.__unsaved ||
		frm.doc.__islocal
	);

	const forward_btn = frm.page.wrapper
		.find('[data-label="Send%20Forward"], [data-label="Send Forward"], button:contains("Send Forward")')
		.filter(function () {
			const label = $(this).attr("data-label");
			const text = $(this).text().trim();
			return (
				text === __("Send Forward") ||
				label === "Send Forward" ||
				label === "Send%20Forward"
			);
		});

	if (forward_btn.length) {
		if (is_dirty) {
			forward_btn
				.prop("disabled", true)
				.addClass("disabled")
				.attr("aria-disabled", "true")
				.attr("title", __("Please save changes before sending forward."));
		} else {
			forward_btn
				.prop("disabled", false)
				.removeClass("disabled")
				.attr("aria-disabled", "false")
				.removeAttr("title");
		}
	}
}

const update_workflow_action_buttons = update_save_before_forward_guard;

function render_sidebar_custom_info(frm) {
	if (!frm.sidebar || !frm.sidebar.sidebar) return;

	const sidebar_menu = frm.sidebar.sidebar.find(".sidebar-menu");
	if (!sidebar_menu.length) return;

	// Clear any previously appended custom info
	sidebar_menu.find(".custom-sidebar-info").remove();

	// 1. Revision Number
	const revision = frm.doc.revision;
	if (revision !== undefined && revision !== null) {
		sidebar_menu.append(`
            <li class="custom-sidebar-info" style="border-top: 1px dashed var(--border-color); margin-top: 8px; padding-top: 8px;">
                <strong>${__("Revision No")}:</strong> ${revision}
            </li>
        `);
	}

	// 2. Remarks (if any)
	if (frm.doc.remarks) {
		sidebar_menu.append(`
            <li class="custom-sidebar-info" style="margin-top: 4px;">
                <strong>${__("Remarks")}:</strong> <br><span class="text-muted">${frappe.utils.escape_html(frm.doc.remarks)}</span>
            </li>
        `);
	}

	// 3. Verifier Comments (if any)
	if (frm.doc.verifier_comments) {
		sidebar_menu.append(`
            <li class="custom-sidebar-info" style="margin-top: 4px;">
                <strong>${__("Verifier Comments")}:</strong> <br><span class="text-muted">${frappe.utils.escape_html(frm.doc.verifier_comments)}</span>
            </li>
        `);
	}

	// 4. Approver Comments (if any)
	if (frm.doc.approver_comments) {
		sidebar_menu.append(`
            <li class="custom-sidebar-info" style="margin-top: 4px;">
                <strong>${__("Approver Comments")}:</strong> <br><span class="text-muted">${frappe.utils.escape_html(frm.doc.approver_comments)}</span>
            </li>
        `);
	}
}

function handle_shipment_type_change(frm) {
	let shipment_type = frm.doc.shipment_type;
	let subtype_options = [];

	if (shipment_type === "Containerized") {
		subtype_options = [
			"",
			"20 gp container",
			"40 gp container",
			"20 hq container",
			"40 hq container",
			"20 SOC container",
			"40 SOC container",
		];
	} else if (shipment_type === "Flat Rack") {
		subtype_options = ["", "20 Flat track", "40 Flat track"];
	} else if (shipment_type === "Oversized") {
		subtype_options = ["", "20 ODC", "40 ODC"];
	}

	if (subtype_options.length > 0) {
		frm.set_df_property("shipment_subtype", "options", subtype_options.join("\n"));
		frm.set_df_property("shipment_subtype", "hidden", 0);
		frm.set_df_property("shipment_subtype", "reqd", 1);
	} else {
		frm.set_value("shipment_subtype", "");
		frm.set_df_property("shipment_subtype", "hidden", 1);
		frm.set_df_property("shipment_subtype", "reqd", 0);
	}
}

function render_workflow_activity_history(frm) {
	if (!frm || !frm.doc || frm.doc.__islocal || !frm.doc.name) {
		$(frm.wrapper).find('[data-fieldname="sec_workflow_history"]').hide();
		return;
	}

	const $sec = $(frm.wrapper).find('[data-fieldname="sec_workflow_history"]');
	$sec.removeClass("hide-control hide").show();
	$sec.find(".section-body").removeClass("hide").show();

	frappe.call({
		method: "sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order.get_workflow_activity_history",
		args: { docname: frm.doc.name },
		callback: function (r) {
			let html = "";
			if (r.message && r.message.length > 0) {
				html = `
                    <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;">
                        <span style="font-weight: 600; font-size: 12px; color: #1e293b;">
                            <i class="fa fa-history" style="margin-right: 5px; color: #2563eb;"></i> PO Approval &amp; Activity Audit Trail (${r.message.length} events)
                        </span>
                        <button type="button" class="btn btn-xs btn-default btn-export-excel" style="font-weight: 600; font-size: 11px; padding: 4px 10px; background: #ffffff; color: #15803d; border: 1px solid #86efac; border-radius: 4px;">
                            <i class="fa fa-file-excel-o" style="margin-right: 4px; color: #16a34a;"></i> Export to Excel (CSV)
                        </button>
                    </div>
                    <div class="table-responsive" style="border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                        <table class="table table-bordered table-condensed table-hover" style="margin: 0; background: #fff; font-size: 12px; color: #1e293b; width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #1e3a5f; color: #ffffff; font-weight: 600;">
                                    <th style="width: 40px; text-align: center; padding: 8px 6px; border: 1px solid #334e68;">#</th>
                                    <th style="width: 135px; padding: 8px 8px; border: 1px solid #334e68;">Date &amp; Time</th>
                                    <th style="width: 175px; padding: 8px 8px; border: 1px solid #334e68;">User</th>
                                    <th style="width: 190px; padding: 8px 8px; border: 1px solid #334e68;">Stage &amp; Action</th>
                                    <th style="padding: 8px 10px; border: 1px solid #334e68;">Changes Made</th>
                                    <th style="width: 170px; padding: 8px 8px; border: 1px solid #334e68;">Remarks / Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
				r.message.forEach((row, idx) => {
					let rowBg = idx % 2 === 0 ? "#ffffff" : "#f8fafc";
					let changesHtml = "";
					if (row.changes && row.changes.length > 0) {
						changesHtml = '<div style="max-height: 140px; overflow-y: auto;"><ul style="margin: 0; padding-left: 16px; font-size: 11px; line-height: 1.6; color: #334155;">';
						row.changes.forEach((chg) => {
							let fieldName = frappe.utils.escape_html(chg.field || "");
							let oldVal = frappe.utils.escape_html(chg.old || "");
							let newVal = frappe.utils.escape_html(chg.new || "");
							if (oldVal !== "—" && newVal !== "—") {
								changesHtml += `<li><strong>${fieldName}:</strong> <del style="color: #b91c1c; text-decoration: line-through;">${oldVal}</del> → <span style="color: #15803d; font-weight: 600;">${newVal}</span></li>`;
							} else if (newVal !== "—") {
								changesHtml += `<li><strong>${fieldName}:</strong> <span style="color: #15803d; font-weight: 600;">${newVal}</span></li>`;
							} else if (chg.text) {
								changesHtml += `<li>${frappe.utils.escape_html(chg.text)}</li>`;
							} else {
								changesHtml += `<li><strong>${fieldName}</strong></li>`;
							}
						});
						changesHtml += "</ul></div>";
					} else {
						changesHtml = '<span style="color: #94a3b8; font-style: italic;">No field modifications</span>';
					}

					html += `
                        <tr style="background: ${rowBg};">
                            <td style="padding: 8px 6px; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; vertical-align: top; font-weight: 500;">${row.no}</td>
                            <td style="padding: 8px 8px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #475569; vertical-align: top; white-space: nowrap;">${row.datetime}</td>
                            <td style="padding: 8px 8px; border-top: 1px solid #e2e8f0; vertical-align: top;">
                                <div style="font-weight: 600; color: #0f172a;">${frappe.utils.escape_html(row.user)}</div>
                                <div style="font-size: 10px; color: #64748b;">${frappe.utils.escape_html(row.email)}</div>
                            </td>
                            <td style="padding: 8px 8px; border-top: 1px solid #e2e8f0; vertical-align: top;">
                                <span style="display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; background: #e0e7ff; color: #3730a3;">${frappe.utils.escape_html(row.state || "Draft")}</span>
                                <div style="font-size: 11px; font-weight: 600; color: #1e293b; margin-top: 4px;">${frappe.utils.escape_html(row.action || "")}</div>
                            </td>
                            <td style="padding: 8px 10px; border-top: 1px solid #e2e8f0; vertical-align: top;">${changesHtml}</td>
                            <td style="padding: 8px 8px; border-top: 1px solid #e2e8f0; white-space: pre-wrap; word-wrap: break-word; color: #334155; vertical-align: top;">${row.remarks ? frappe.utils.escape_html(row.remarks) : '<span style="color:#cbd5e1;">—</span>'}</td>
                        </tr>
                    `;
				});
				html += `
                            </tbody>
                        </table>
                    </div>
                `;
			} else {
				html = `
					<div style="padding: 18px; text-align: center; color: #64748b; font-style: italic; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 6px;">
						<i class="fa fa-info-circle" style="margin-right: 5px; color: #3b82f6;"></i> No audit trail records found for this Purchase Order yet.
					</div>
				`;
			}

			// Render directly into DOM
			let rendered = false;
			const $field = $(frm.wrapper).find('[data-fieldname="workflow_history_html"]');
			if ($field.length) {
				$field.empty().html(html);
				rendered = true;
			}

			if (frm.fields_dict && frm.fields_dict.workflow_history_html && frm.fields_dict.workflow_history_html.$wrapper) {
				frm.fields_dict.workflow_history_html.$wrapper.empty().html(html);
				rendered = true;
			}

			const $secBody = $(frm.wrapper).find('[data-fieldname="sec_workflow_history"] .section-body');
			if ($secBody.length && (!rendered || !$secBody.find(".table-responsive").length)) {
				$secBody.empty().html(html);
			}

			// Bind click event to export button
			setTimeout(() => {
				$(frm.wrapper)
					.find(".btn-export-excel")
					.off("click")
					.on("click", function () {
						export_history_to_excel(frm.doc.name, r.message || []);
					});
			}, 100);
		},
	});
}

function export_history_to_excel(po_name, data) {
	let csv = "No,Date & Time,User Name,User Email,Stage,Action,Changes Made,Remarks / Comments\n";
	data.forEach((row) => {
		let remarks = (row.remarks || "").replace(/"/g, '""');
		let user = (row.user || "").replace(/"/g, '""');
		let action = (row.action || "").replace(/"/g, '""');
		let state = (row.state || "").replace(/"/g, '""');
		let changesText = (row.changes || [])
			.map((c) => c.text || `${c.field}: ${c.old} -> ${c.new}`)
			.join(" | ")
			.replace(/"/g, '""');
		csv += `${row.no},"${row.datetime}","${user}","${row.email}","${state}","${action}","${changesText}","${remarks}"\n`;
	});

	const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
	const link = document.createElement("a");
	if (link.download !== undefined) {
		const url = URL.createObjectURL(blob);
		link.setAttribute("href", url);
		link.setAttribute("download", `${po_name}_audit_trail.csv`);
		link.style.visibility = "hidden";
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}
}


function set_quotation_governance_access(frm, state) {
	const is_locked = !frm.is_new() && state !== "Draft";
	["quotations", "quotation_comparison_sheet"].forEach((fieldname) => {
		frm.set_df_property(fieldname, "read_only", is_locked ? 1 : 0);
	});

	const quotation_grid = frm.get_field("quotations") && frm.get_field("quotations").grid;
	if (quotation_grid) {
		quotation_grid.cannot_add_rows = is_locked;
		quotation_grid.cannot_delete_rows = is_locked;
		quotation_grid.refresh();
	}
}

function render_quotation_attachments(frm) {
	const quotation_field = frm.get_field("quotations");
	if (!quotation_field || !quotation_field.$wrapper) return;

	quotation_field.$wrapper.find(".quotation-attachments-panel").remove();

	const attachments = (frm.doc.quotations || []).filter((row) => row.quotation_pdf);
	if (!attachments.length) return;

	const rows = attachments
		.map((row) => {
			const supplier = frappe.utils.escape_html(row.supplier || __("Vendor"));
			const file_url = frappe.utils.escape_html(row.quotation_pdf);
			const file_name = frappe.utils.escape_html(
				row.quotation_pdf.split("/").pop() || __("Quotation file"),
			);

			return `
            <li>
                <strong>${supplier}</strong>
                <a href="${file_url}" target="_blank" rel="noopener noreferrer">${file_name}</a>
            </li>
        `;
		})
		.join("");

	quotation_field.$wrapper.append(`
        <div class="quotation-attachments-panel form-grid-container" style="margin-top: 12px;">
            <div class="form-section-heading">${__("Quotation Attachments")}</div>
            <ul class="list-unstyled" style="margin-bottom: 0;">
                ${rows}
            </ul>
        </div>
    `);
}

function set_entity_policy_filters(frm) {
	const sri_entity = "Sarveksha Realty and Inframine LLP";
	if (frm.doc.po_type === "Internal PO") {
		frm.set_query("vendor", () => ({ filters: { supplier_name: sri_entity, disabled: 0 } }));
		frm.set_query("company", () => ({ filters: [["name", "!=", sri_entity]] }));
		return;
	}

	frm.set_query("vendor", () => ({ filters: { disabled: 0 } }));
	frm.set_query("company", () => ({}));
}
