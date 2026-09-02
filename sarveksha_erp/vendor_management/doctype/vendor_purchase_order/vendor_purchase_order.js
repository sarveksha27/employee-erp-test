// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vendor Purchase Order', {

    // ─── ON FORM LOAD ─────────────────────────────────────────
    refresh: function(frm) {
        const colors = {
            'Draft': 'gray',
            'Generated (Yet to be Verified)': 'orange',
            'Verified (Yet to be approved)': 'blue',
            'Approved': 'green',
            'Cancelled': 'red',
        };
        if (frm.doc.workflow_state && colors[frm.doc.workflow_state]) {
            frm.set_indicator_formatter('workflow_state', function(doc) {
                return colors[doc.workflow_state] || 'gray';
            });
        }

        // Hide standard workflow actions menu
        if (frm.states) {
            frm.states.show_actions = function() {};
            frm.page.clear_actions_menu();
        }

        // Hide manual status and workflow_state selection fields from the form
        frm.toggle_display('status', false);
        frm.toggle_display('workflow_state', false);

        // Always lock PO Type so selection cannot be changed during drafting or editing
        frm.set_df_property('po_type', 'read_only', 1);

        // Render custom buttons based on workflow state & user roles
        const state = frm.doc.workflow_state || 'Draft';
        set_quotation_governance_access(frm, state);
        set_entity_policy_filters(frm);
        const user_roles = frappe.user_roles;
        const is_manager = user_roles.includes('Procurement Manager') || user_roles.includes('System Manager') || user_roles.includes('Administrator');

        // Helper function to apply workflow action
        const apply_action = function(action_name) {
            const execute_action = () => {
                frappe.dom.freeze();
                frappe.xcall("frappe.model.workflow.apply_workflow", {
                    doc: frm.doc,
                    action: action_name
                }).then(doc => {
                    frappe.model.sync(doc);
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __("Action '{0}' applied successfully!", [action_name]),
                        indicator: 'green'
                    });
                }).catch(err => {
                    frappe.msgprint(__("Error applying action: ") + err.message);
                }).finally(() => {
                    frappe.dom.unfreeze();
                });
            };

            if (frm.doc.__unsaved || frm.doc.__islocal) {
                frm.save().then(execute_action);
            } else {
                execute_action();
            }
        };

        // Clear existing custom buttons first
        frm.clear_custom_buttons();

        if (frm.doc.docstatus === 0) {
            if (state === 'Draft' && (user_roles.includes('PO Generator') || is_manager)) {
                frm.add_custom_button(__('Send Forward'), function() {
                    apply_action('Generate PO');
                });
                frm.change_custom_button_type(__('Send Forward'), null, 'primary');
            }

            else if (state === 'Generated (Yet to be Verified)' && (user_roles.includes('PO Verifier') || is_manager)) {
                frm.add_custom_button(__('Send Forward'), function() {
                    apply_action('Verify');
                });
                frm.change_custom_button_type(__('Send Forward'), null, 'primary');

                frm.add_custom_button(__('Send Back'), function() {
                    frappe.prompt([
                        {
                            label: __('Reason / Corrective Action Required'),
                            fieldname: 'remarks',
                            fieldtype: 'Small Text',
                            reqd: 1
                        }
                    ], function(values) {
                        frm.set_value('verifier_comments', values.remarks);
                        frm.save().then(() => {
                            apply_action('Send Back');
                        });
                    }, __('Send Back to Generator'), __('Submit'));
                });
                frm.change_custom_button_type(__('Send Back'), null, 'danger');
            }

            else if (state === 'Verified (Yet to be approved)' && (user_roles.includes('PO Approver') || is_manager)) {
                frm.add_custom_button(__('Send Forward'), function() {
                    apply_action('Approve');
                });
                frm.change_custom_button_type(__('Send Forward'), null, 'primary');

                frm.add_custom_button(__('Send Back'), function() {
                    frappe.prompt([
                        {
                            label: __('Reason / Corrective Action Required'),
                            fieldname: 'remarks',
                            fieldtype: 'Small Text',
                            reqd: 1
                        }
                    ], function(values) {
                        frm.set_value('approver_comments', values.remarks);
                        frm.save().then(() => {
                            apply_action('Send Back');
                        });
                    }, __('Send Back to Verifier'), __('Submit'));
                });
                frm.change_custom_button_type(__('Send Back'), null, 'danger');
            }
        }

        // Configure Print Button & Menu Visibility based on Workflow Stage and User Roles
        const is_approved = (frm.doc.workflow_state === 'Approved' || frm.doc.docstatus === 1);
        const can_print = is_approved && (user_roles.includes('PO Generator') || is_manager);

        const open_compiled_pdf = function() {
            const pdf_url = frappe.urllib.get_full_url(
                `/api/method/frappe.utils.print_format.download_pdf?doctype=Vendor%20Purchase%20Order&name=${encodeURIComponent(frm.doc.name)}`
            );
            window.open(pdf_url, '_blank');
        };

        if (can_print) {
            frm.add_custom_button(__('Print PO'), open_compiled_pdf);
            frm.change_custom_button_type(__('Print PO'), null, 'primary');

            // Intercept standard Frappe print actions
            frm.print_doc = open_compiled_pdf;
        }

        if (!can_print) {
            frm.page.hide_menu_item(__('Print'));
            frm.page.hide_menu_item(__('PDF'));
            if (frm.page.btn_print) frm.page.btn_print.hide();
            if (frm.page.set_print_btn_display) frm.page.set_print_btn_display(false);
        } else {
            frm.page.show_menu_item(__('Print'));
            frm.page.show_menu_item(__('PDF'));
            if (frm.page.btn_print) frm.page.btn_print.show();
            if (frm.page.set_print_btn_display) frm.page.set_print_btn_display(true);

            setTimeout(() => {
                if (frm.page) {
                    frm.page.menu.find('[data-label="Print"]').off('click').on('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        open_compiled_pdf();
                    });
                    frm.page.menu.find('[data-label="PDF"]').off('click').on('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        open_compiled_pdf();
                    });
                }
            }, 300);
        }

        // Hide "+ New" button for Verifiers/Approvers in Form View
        if (frappe.session.user !== 'Administrator') {
            const is_verifier_or_approver = (user_roles.includes('PO Verifier') || user_roles.includes('PO Approver'));
            const is_generator = user_roles.includes('PO Generator');

            if (is_verifier_or_approver && !is_generator) {
                frm.page.hide_menu_item(__('New'));
                frm.page.clear_secondary_action();
            }
        }

        // Configure Verification & Approval Panel Dynamic Controls
        setup_verification_approval_panel(frm);

        // Render custom remarks and revision number in the sidebar
        render_sidebar_custom_info(frm);

        // Recalculate on every refresh to keep values consistent
        calculate_gst_and_totals(frm);
        set_port_filter(frm);

        // Auto-detect letterhead if not set
        if (!frm.doc.letter_head && frm.doc.company) {
            frm.trigger('company');
        }

        // Display standard terms preview on load
        if (frm.doc.standard_terms) {
            frm.trigger('standard_terms');
        } else {
            frm.set_df_property('terms_preview', 'options', '');
        }

        // Set up Shipment Subtype visibility and options
        handle_shipment_type_change(frm);

        // Render Workflow Activity History
        render_workflow_activity_history(frm);
    },

    // ─── COMPANY TRIGGER ──────────────────────────────────────
    company: function(frm) {
        if (!frm.doc.company) return;

        frappe.call({
            method: 'sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order.get_company_details',
            args: { company: frm.doc.company },
            callback: function(r) {
                if (r.message) {
                    const data = r.message;
                    if (data.default_port) {
                        frm.set_value('default_port', data.default_port);
                        set_port_filter(frm);
                        const first_port = data.default_port.split(',')[0].trim();
                        frappe.db.exists('Port', first_port).then(exists => {
                            if (exists) {
                                frm.set_value('port', first_port);
                            }
                        });
                    }
                    if (data.currency) {
                        frm.set_value('currency', data.currency);
                    }
                    frm.set_value('company_gstin', data.company_gstin);
                    frm.set_value('company_pan', data.company_pan);
                    frm.set_value('company_address', data.company_address);
                    frm.set_value('letter_head', data.letter_head);

                    // Auto-select standard terms if not already set
                    if (!frm.doc.standard_terms || frm.doc.standard_terms.length === 0) {
                        const company_name = (frm.doc.company || '').toLowerCase();
                        let terms_to_add = [];
                        if (frm.doc.is_lut_applicable) {
                            terms_to_add.push('LUT Certificate Terms');
                        }
                        
                        if (company_name.includes('bstp')) terms_to_add.push('Guinea BSTP SAS Procurement Terms');
                        else if (company_name.includes('mining') || company_name.includes('baani')) terms_to_add.push('Cameroon Mining & Minerals Terms');
                        else if (company_name.includes('sl limited')) terms_to_add.push('Sierra Leone Procurement Terms');
                        else if (company_name.includes('botswana')) terms_to_add.push('Botswana Mining & Equipment Terms');

                        if (!terms_to_add.includes('Standard Export PO Terms')) {
                            terms_to_add.push('Standard Export PO Terms');
                        }

                        frm.set_value('standard_terms', terms_to_add.map(t => ({ standard_term: t })));
                        frm.trigger('standard_terms');
                    }
                }
                calculate_gst_and_totals(frm);
            }
        });
    },

    // ─── ON FORM LOAD / INITIALIZATION ───────────────────────
    onload: function(frm) {
        if (frm.is_new()) {
            let po_category = frappe.route_options && (frappe.route_options.po_category || frappe.route_options.po_type);
            if (!po_category && window.location.search) {
                let params = new URLSearchParams(window.location.search);
                po_category = params.get('po_category') || params.get('po_type');
            }
            if (po_category) {
                if (po_category.includes('Internal')) {
                    frm.set_value('po_type', 'Internal PO');
                    frm.set_value('vendor', 'Sarveksha Realty and Inframine LLP');
                } else if (po_category.includes('External') || po_category.includes('Vendor')) {
                    frm.set_value('po_type', 'Vendor PO');
                }
            }
        }
    },

    // ─── VENDOR TRIGGER ───────────────────────────────────────
    vendor: function(frm) {
        if (!frm.doc.vendor) {
            frm.set_value('vendor_address', '');
            return;
        }

        frappe.call({
            method: 'sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order.get_supplier_payment_details',
            args: { supplier: frm.doc.vendor },
            callback: function(r) {
                if (r.message) {
                    const data = r.message;
                    if (data.tax_id) frm.set_value('vendor_gstin', data.tax_id);
                    if (data.custom_pan) frm.set_value('vendor_pan', data.custom_pan);
                    if (data.custom_bank_name) frm.set_value('vendor_bank_name', data.custom_bank_name);
                    if (data.custom_account_number) frm.set_value('vendor_account_number', data.custom_account_number);
                    if (data.custom_ifsc) frm.set_value('vendor_ifsc', data.custom_ifsc);
                    if (data.vendor_address !== undefined) frm.set_value('vendor_address', data.vendor_address);

                    frm._vendor_gstin = data.tax_id || '';

                    // Populate Payment Terms & Advance Percentage
                    if (data.payment_terms_description) {
                        frm.set_value('payment_terms', data.payment_terms_description);
                    }
                    if (data.advance_percentage !== undefined) {
                        frm.set_value('advance_percentage', data.advance_percentage);
                    }

                    calculate_gst_and_totals(frm);
                }
            }
        });
    },

    shipment_type: function(frm) {
        handle_shipment_type_change(frm);
    },

    // ─── PRICING TRIGGERS ─────────────────────────────────────
    freight: function(frm) { calculate_gst_and_totals(frm); },
    insurance: function(frm) { calculate_gst_and_totals(frm); },
    packing_charges: function(frm) { calculate_gst_and_totals(frm); },
    other_charges: function(frm) { calculate_gst_and_totals(frm); },
    advance_percentage: function(frm) { calculate_gst_and_totals(frm); },
    vendor_gstin: function(frm) { calculate_gst_and_totals(frm); },
    is_lut_applicable: function(frm) {
        if (frm.doc.is_lut_applicable) {
            frm.set_value('standard_terms', [{ standard_term: 'LUT Certificate Terms' }]);
            frm.trigger('standard_terms');
        }
        calculate_gst_and_totals(frm);
    },

    po_type: function(frm) {
        set_entity_policy_filters(frm);
        // Recalculate whenever PO Type changes (External vs Internal)
        // This shows/hides margin fields and updates grand total
        calculate_gst_and_totals(frm);
        frm.refresh_fields(['sec_internal_margin', 'internal_margin_percentage', 'internal_margin_amount', 'logistics_cost']);
    },

    internal_margin_percentage: function(frm) {
        calculate_gst_and_totals(frm);
    },
    // ─── INDIVIDUAL EQUIPMENT ENTRY TRIGGERS ──────────────────
    equipment: function(frm) {
        if (!frm.doc.equipment) return;

        frappe.db.get_value('Equipment', frm.doc.equipment,
            ['equipment_name', 'hsn_code', 'brand', 'manufacturer', 'unit', 'specification', 'approx_cost_inr', 'last_purchase_cost_inr', 'gst_percentage'],
            function(r) {
                if (r) {
                    frm.set_value('equipment_name', r.equipment_name || '');
                    frm.set_value('hsn_code', r.hsn_code || '');
                    frm.set_value('brand', r.brand || '');
                    frm.set_value('manufacturer', r.manufacturer || '');
                    frm.set_value('unit', r.unit || 'Nos');
                    frm.set_value('specification', r.specification || '');

                    const cost = flt(r.approx_cost_inr) || flt(r.last_purchase_cost_inr) || 10000;
                    const gst_pct = flt(r.gst_percentage) || 18;

                    frm.set_value('rate', cost);
                    frm.set_value('gst_percentage', gst_pct);
                }
            }
        );
    },

    add_equipment_btn: function(frm) {
        if (!frm.doc.equipment && !frm.doc.equipment_name) {
            frappe.msgprint(__('Please select an Equipment Code or enter Equipment Name before adding to table.'));
            return;
        }

        let item = frm.add_child('items');
        item.equipment = frm.doc.equipment || '';
        item.equipment_name = frm.doc.equipment_name || '';
        item.hsn_code = frm.doc.hsn_code || '';
        item.brand = frm.doc.brand || '';
        item.manufacturer = frm.doc.manufacturer || '';
        item.quantity = flt(frm.doc.quantity) || 1;
        item.unit = frm.doc.unit || 'Nos';
        item.rate = flt(frm.doc.rate) || 0;
        item.discount_percent = flt(frm.doc.discount_percent) || 0;
        item.gst_percentage = flt(frm.doc.gst_percentage) || 18;
        item.specification = frm.doc.specification || '';

        frm.refresh_field('items');
        calculate_gst_and_totals(frm);

        // Reset individual input fields for next entry
        frm.set_value('equipment', '');
        frm.set_value('equipment_name', '');
        frm.set_value('hsn_code', '');
        frm.set_value('brand', '');
        frm.set_value('manufacturer', '');
        frm.set_value('quantity', 1);
        frm.set_value('rate', 0);
        frm.set_value('specification', '');

        frappe.show_alert({
            message: __('Equipment item added to order table!'),
            indicator: 'green'
        });
    },

    standard_terms: function(frm) {
        if (frm.doc.standard_terms && frm.doc.standard_terms.length > 0) {
            const terms_list = frm.doc.standard_terms.map(row => row.standard_term).filter(Boolean);
            if (terms_list.length > 0) {
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Terms and Conditions',
                        filters: { name: ['in', terms_list] },
                        fields: ['name', 'terms'],
                        limit: 50
                    },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            const terms_map = {};
                            r.message.forEach(item => {
                                terms_map[item.name] = item.terms;
                            });
                            let concatenated_terms = '';
                            terms_list.forEach((t_name, idx) => {
                                if (terms_map[t_name]) {
                                    concatenated_terms += `<h3>${idx + 1}. ${t_name}</h3>${terms_map[t_name]}<br><hr>`;
                                }
                            });
                            frm.set_df_property('terms_preview', 'options', concatenated_terms);
                        } else {
                            frm.set_df_property('terms_preview', 'options', '');
                        }
                    }
                });
            } else {
                frm.set_df_property('terms_preview', 'options', '');
            }
        } else {
            frm.set_df_property('terms_preview', 'options', '');
        }
    },

});

// ─── CHILD TABLE GRID TRIGGERS (Vendor Purchase Order Item) ───
frappe.ui.form.on('Vendor Purchase Order Item', {
    equipment: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.equipment) return;

        frappe.db.get_value('Equipment', row.equipment,
            ['equipment_name', 'hsn_code', 'brand', 'manufacturer', 'unit', 'specification', 'approx_cost_inr', 'last_purchase_cost_inr', 'gst_percentage'],
            function(r) {
                if (r) {
                    frappe.model.set_value(cdt, cdn, 'equipment_name', r.equipment_name || '');
                    frappe.model.set_value(cdt, cdn, 'hsn_code', r.hsn_code || '');
                    frappe.model.set_value(cdt, cdn, 'brand', r.brand || '');
                    frappe.model.set_value(cdt, cdn, 'manufacturer', r.manufacturer || '');
                    frappe.model.set_value(cdt, cdn, 'unit', r.unit || 'Nos');
                    frappe.model.set_value(cdt, cdn, 'specification', r.specification || '');
                    
                    const cost = flt(r.approx_cost_inr) || flt(r.last_purchase_cost_inr) || 10000;
                    const gst_pct = flt(r.gst_percentage) || 18;
                    
                    frappe.model.set_value(cdt, cdn, 'rate', cost);
                    frappe.model.set_value(cdt, cdn, 'gst_percentage', gst_pct);

                    calculate_gst_and_totals(frm);
                }
            }
        );
    },

    quantity: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    rate: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    discount_percent: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    gst_percentage: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    items_remove: function(frm) { calculate_gst_and_totals(frm); }
});

// ─── MASTER CALCULATION ENGINE ────────────────────────────────
// ─── MASTER CALCULATION ENGINE ────────────────────────────────
function calculate_gst_and_totals(frm) {
    const is_lut = frm.doc.is_lut_applicable;
    const is_internal = (frm.doc.po_type || '') === 'Internal PO';

    let total_taxable_value = 0;
    let total_item_tax = 0;

    // We need to handle LUT reversion asynchronously for items with Equipment master
    // To keep it synchronous-safe, we collect items needing reversion and use a queue
    const reversion_promises = [];

    if (frm.doc.items && frm.doc.items.length > 0) {
        frm.doc.items.forEach(row => {
            if (is_lut) {
                row.gst_percentage = 0.1;
            } else {
                // ── LUT REVERSION ─────────────────────────────────────────────
                // If the item's GST% is exactly 0.1, it was set by LUT.
                // Restore from Equipment master (async but we handle it after)
                if (flt(row.gst_percentage) === 0.1 && row.equipment) {
                    reversion_promises.push(
                        frappe.db.get_value('Equipment', row.equipment, 'gst_percentage')
                            .then(r => {
                                const master_gst = (r && r.message && flt(r.message.gst_percentage) > 0)
                                    ? flt(r.message.gst_percentage)
                                    : 18.0;
                                row.gst_percentage = master_gst;
                            })
                    );
                }
            }
        });
    }

    const _do_calculate = () => {
        let tv = 0;
        let tt = 0;

        if (frm.doc.items && frm.doc.items.length > 0) {
            frm.doc.items.forEach(row => {
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
            frm.refresh_field('items');
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

        // GST Type Determination
        const vendor_gstin = (frm.doc.vendor_gstin || frm._vendor_gstin || '');
        const company_gstin = (frm.doc.company_gstin || frm._company_gstin || '');

        let gst_type = 'IGST';
        let cgst = 0, sgst = 0, igst = 0;

        if (is_lut) {
            gst_type = 'IGST';
            igst = total_item_tax;
        } else if (vendor_gstin.length >= 2 && company_gstin.length >= 2 && vendor_gstin.substring(0, 2) === company_gstin.substring(0, 2)) {
            gst_type = 'CGST + SGST';
            cgst = total_item_tax / 2;
            sgst = total_item_tax / 2;
        } else {
            gst_type = 'IGST';
            igst = total_item_tax;
        }

        // Internal Margin (Internal PO only)
        let internal_margin_amount = 0;
        let internal_margin_pct = 0;
        if (is_internal) {
            internal_margin_pct = flt(frm.doc.internal_margin_percentage) || 5.0;
            internal_margin_amount = flt((total_taxable_value + logistics_cost) * (internal_margin_pct / 100), 2);
        }

        const grand_total = flt(total_taxable_value + total_item_tax + logistics_cost + internal_margin_amount, 2);
        const advance_amount = flt(grand_total * (advance_pct / 100), 2);
        const balance_due = flt(grand_total - advance_amount, 2);

        frm.set_value('taxable_value', flt(total_taxable_value, 2));
        frm.set_value('logistics_cost', logistics_cost);
        frm.set_value('gst_type', gst_type);
        frm.set_value('cgst_amount', flt(cgst, 2));
        frm.set_value('sgst_amount', flt(sgst, 2));
        frm.set_value('igst_amount', flt(igst, 2));
        frm.set_value('tax_amount', flt(total_item_tax, 2));
        if (is_internal) {
            frm.set_value('internal_margin_percentage', internal_margin_pct);
            frm.set_value('internal_margin_amount', internal_margin_amount);
        } else {
            frm.set_value('internal_margin_percentage', 0);
            frm.set_value('internal_margin_amount', 0);
        }
        frm.set_value('grand_total', grand_total);
        frm.set_value('advance_amount', advance_amount);
        frm.set_value('balance_due', balance_due);
    };

    // If there are LUT reversion fetches pending, wait for them then calculate
    if (reversion_promises.length > 0) {
        Promise.all(reversion_promises).then(_do_calculate);
    } else {
        _do_calculate();
    }
}

function set_port_filter(frm) {
    frm.set_query('port', function() {
        if (frm.doc.default_port) {
            const ports = frm.doc.default_port.split(',').map(p => p.trim()).filter(Boolean);
            if (ports.length > 0) {
                return { filters: [['Port', 'name', 'in', ports]] };
            }
        }
        return { filters: { 'is_active': 1 } };
    });
}

function setup_verification_approval_panel(frm) {
    const user_roles = frappe.user_roles;
    const has_verifier_role = user_roles.includes('PO Verifier') || user_roles.includes('Procurement Manager') || user_roles.includes('System Manager') || user_roles.includes('Administrator');
    const has_approver_role = user_roles.includes('PO Approver') || user_roles.includes('Procurement Manager') || user_roles.includes('System Manager') || user_roles.includes('Administrator');
    const is_manager = user_roles.includes('Procurement Manager') || user_roles.includes('System Manager') || user_roles.includes('Administrator');

    const state = frm.doc.workflow_state || 'Draft';

    // 1. Enable/Disable entire form based on active role allowed to edit in current state
    let can_edit = false;
    if (is_manager) {
        can_edit = true;
    } else if (state === 'Draft' && user_roles.includes('PO Generator')) {
        can_edit = true;
    } else if (state === 'Generated (Yet to be Verified)' && user_roles.includes('PO Verifier')) {
        can_edit = true;
    } else if (state === 'Verified (Yet to be approved)' && user_roles.includes('PO Approver')) {
        can_edit = true;
    }

    if (can_edit) {
        frm.enable_form();
    } else {
        frm.disable_form();
        frm.dashboard.clear_comment_input();
    }

    // 2. Verifier comments: ONLY editable during 'Generated (Yet to be Verified)' stage by authorized verifiers
    if (state === 'Generated (Yet to be Verified)' && has_verifier_role && can_edit) {
        frm.set_df_property('verifier_comments', 'read_only', 0);
    } else {
        frm.set_df_property('verifier_comments', 'read_only', 1);
    }

    // 3. Approver comments: ONLY editable during 'Verified (Yet to be approved)' stage by authorized approvers
    if (state === 'Verified (Yet to be approved)' && has_approver_role && can_edit) {
        frm.set_df_property('approver_comments', 'read_only', 0);
    } else {
        frm.set_df_property('approver_comments', 'read_only', 1);
    }

    // 4. Ensure audit metadata fields are permanently read-only
    ['verified_by', 'verified_on', 'verifier_status', 'approved_by', 'approved_on', 'approver_status', 'prepared_by', 'signatory'].forEach(field => {
        frm.set_df_property(field, 'read_only', 1);
    });
}

function render_sidebar_custom_info(frm) {
    if (!frm.sidebar || !frm.sidebar.sidebar) return;

    const sidebar_menu = frm.sidebar.sidebar.find('.sidebar-menu');
    if (!sidebar_menu.length) return;

    // Clear any previously appended custom info
    sidebar_menu.find('.custom-sidebar-info').remove();

    // 1. Revision Number
    const revision = frm.doc.revision;
    if (revision !== undefined && revision !== null) {
        sidebar_menu.append(`
            <li class="custom-sidebar-info" style="border-top: 1px dashed var(--border-color); margin-top: 8px; padding-top: 8px;">
                <strong>${__('Revision No')}:</strong> ${revision}
            </li>
        `);
    }

    // 2. Remarks (if any)
    if (frm.doc.remarks) {
        sidebar_menu.append(`
            <li class="custom-sidebar-info" style="margin-top: 4px;">
                <strong>${__('Remarks')}:</strong> <br><span class="text-muted">${frappe.utils.escape_html(frm.doc.remarks)}</span>
            </li>
        `);
    }

    // 3. Verifier Comments (if any)
    if (frm.doc.verifier_comments) {
        sidebar_menu.append(`
            <li class="custom-sidebar-info" style="margin-top: 4px;">
                <strong>${__('Verifier Comments')}:</strong> <br><span class="text-muted">${frappe.utils.escape_html(frm.doc.verifier_comments)}</span>
            </li>
        `);
    }

    // 4. Approver Comments (if any)
    if (frm.doc.approver_comments) {
        sidebar_menu.append(`
            <li class="custom-sidebar-info" style="margin-top: 4px;">
                <strong>${__('Approver Comments')}:</strong> <br><span class="text-muted">${frappe.utils.escape_html(frm.doc.approver_comments)}</span>
            </li>
        `);
    }
}

function handle_shipment_type_change(frm) {
    let shipment_type = frm.doc.shipment_type;
    let subtype_options = [];

    if (shipment_type === 'Containerized') {
        subtype_options = [
            '',
            '20 gp container',
            '40 gp container',
            '20 hq container',
            '40 hq container',
            '20 SOC container',
            '40 SOC container'
        ];
    } else if (shipment_type === 'Flat Rack') {
        subtype_options = [
            '',
            '20 Flat track',
            '40 Flat track'
        ];
    } else if (shipment_type === 'Oversized') {
        subtype_options = [
            '',
            '20 ODC',
            '40 ODC'
        ];
    }

    if (subtype_options.length > 0) {
        frm.set_df_property('shipment_subtype', 'options', subtype_options.join('\n'));
        frm.set_df_property('shipment_subtype', 'hidden', 0);
        frm.set_df_property('shipment_subtype', 'reqd', 1);
    } else {
        frm.set_value('shipment_subtype', '');
        frm.set_df_property('shipment_subtype', 'hidden', 1);
        frm.set_df_property('shipment_subtype', 'reqd', 0);
    }
}

function render_workflow_activity_history(frm) {
    if (frm.doc.__islocal || !frm.doc.name) {
        frm.set_df_property('workflow_history_html', 'options', '');
        return;
    }

    frappe.call({
        method: 'sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order.get_workflow_activity_history',
        args: { docname: frm.doc.name },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let html = `
                    <div style="margin-bottom: 10px; text-align: right;">
                        <button class="btn btn-xs btn-default btn-export-excel" style="font-weight: 500; font-size: 11px;">
                            <i class="fa fa-download" style="margin-right: 4px; color: #15803d;"></i> Export to Excel
                        </button>
                    </div>
                    <div class="table-responsive" style="border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden;">
                        <table class="table table-bordered table-condensed" style="margin: 0; background: #fff; font-size: 12px; color: #374151; table-layout: fixed; width: 100%;">
                            <colgroup>
                                <col style="width: 4%">
                                <col style="width: 16%">
                                <col style="width: 20%">
                                <col style="width: 22%">
                                <col style="width: 38%">
                            </colgroup>
                            <thead>
                                <tr style="background: #1e3a5f; color: #fff; font-weight: 600;">
                                    <th style="padding: 8px 10px;">#</th>
                                    <th style="padding: 8px 10px;">Date &amp; Time</th>
                                    <th style="padding: 8px 10px;">User</th>
                                    <th style="padding: 8px 10px;">Workflow State</th>
                                    <th style="padding: 8px 10px;">Remarks / Comments</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                r.message.forEach((row, idx) => {
                    let rowBg = idx % 2 === 0 ? '#ffffff' : '#f8fafc';
                    html += `
                        <tr style="background: ${rowBg};">
                            <td style="padding: 7px 10px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280;">${row.no}</td>
                            <td style="padding: 7px 10px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #374151;">${row.datetime}</td>
                            <td style="padding: 7px 10px; border-top: 1px solid #e5e7eb;">
                                <div style="font-weight: 600; color: #111827;">${row.user}</div>
                                <div style="font-size: 10px; color: #9ca3af;">${row.email}</div>
                            </td>
                            <td style="padding: 7px 10px; border-top: 1px solid #e5e7eb;">
                                <span style="display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 600; background: #dbeafe; color: #1e40af;">${row.state}</span>
                            </td>
                            <td style="padding: 7px 10px; border-top: 1px solid #e5e7eb; white-space: pre-wrap; word-wrap: break-word; color: #374151;">${row.remarks || '<span style="color:#d1d5db;">—</span>'}</td>
                        </tr>
                    `;
                });
                html += `
                            </tbody>
                        </table>
                    </div>
                `;
                frm.set_df_property('workflow_history_html', 'options', html);
                
                // Bind click event to export button
                setTimeout(() => {
                    $(frm.wrapper).find('.btn-export-excel').off('click').on('click', function() {
                        export_history_to_excel(frm.doc.name, r.message);
                    });
                }, 150);
            } else {
                frm.set_df_property('workflow_history_html', 'options', '');
            }
        }
    });
}

function export_history_to_excel(po_name, data) {
    let csv = 'No,Date & Time,User Name,User Email,Action,Workflow State,Remarks / Comments\n';
    data.forEach(row => {
        let remarks = (row.remarks || '').replace(/"/g, '""');
        let user = (row.user || '').replace(/"/g, '""');
        let action = (row.action || '').replace(/"/g, '""');
        let state = (row.state || '').replace(/"/g, '""');
        csv += `${row.no},"${row.datetime}","${user}","${row.email}","${action}","${state}","${remarks}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `${po_name}_workflow_history.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}



function set_quotation_governance_access(frm, state) {
    const is_locked = !frm.is_new() && state !== 'Draft';
    ['quotations', 'quotation_comparison_sheet'].forEach(fieldname => {
        frm.set_df_property(fieldname, 'read_only', is_locked ? 1 : 0);
    });

    const quotation_grid = frm.get_field('quotations') && frm.get_field('quotations').grid;
    if (quotation_grid) {
        quotation_grid.cannot_add_rows = is_locked;
        quotation_grid.cannot_delete_rows = is_locked;
        quotation_grid.refresh();
    }
}


function set_entity_policy_filters(frm) {
    const sri_entity = 'Sarveksha Realty and Inframine LLP';
    if (frm.doc.po_type === 'Internal PO') {
        frm.set_query('vendor', () => ({ filters: { supplier_name: sri_entity, disabled: 0 } }));
        frm.set_query('company', () => ({ filters: [['name', '!=', sri_entity]] }));
        return;
    }

    frm.set_query('vendor', () => ({ filters: { disabled: 0 } }));
    frm.set_query('company', () => ({}));
}
