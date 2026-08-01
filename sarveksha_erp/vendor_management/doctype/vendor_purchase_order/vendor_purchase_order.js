// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vendor Purchase Order', {

    // ─── ON FORM LOAD ─────────────────────────────────────────
    refresh: function(frm) {
        const colors = {
            'Draft': 'gray',
            'Pending Verification': 'orange',
            'Verification Returned': 'red',
            'Pending Approval': 'blue',
            'Approved': 'green',
            'Printed': 'green',
            'Submitted': 'blue',
            'Vendor Confirmed': 'purple',
            'Partially Paid': 'orange',
            'Fully Paid': 'green',
            'Shipped': 'teal',
            'Delivered': 'green',
            'Cancelled': 'red',
        };
        if (frm.doc.status && colors[frm.doc.status]) {
            frm.set_indicator_formatter('status', function(doc) {
                return colors[doc.status] || 'gray';
            });
        }

        // Configure Print Button & Menu Visibility based on Workflow Stage and User Roles
        const is_manager = frappe.user.has_role('Procurement Manager') || frappe.user.has_role('System Manager') || frappe.user.has_role('Administrator');
        const is_approved = (frm.doc.workflow_state === 'Approved' || frm.doc.workflow_state === 'Printed' || frm.doc.docstatus === 1);

        if (is_approved) {
            frm.add_custom_button(__('Print PO'), function() {
                frappe.set_route('print', 'Vendor Purchase Order', frm.doc.name);
            }, __('Actions'));
        } else if (!is_manager) {
            // Hide standard print menu for unapproved POs for regular users
            frm.page.hide_menu_item(__('Print'));
        }

        // Configure Verification & Approval Panel Dynamic Controls
        setup_verification_approval_panel(frm);

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
    },

    // ─── COMPANY TRIGGER ──────────────────────────────────────
    company: function(frm) {
        if (!frm.doc.company) return;

        frappe.db.get_value('Company', frm.doc.company,
            ['custom_default_port', 'default_currency', 'tax_id', 'country', 'custom_pan', 'default_letter_head', 'registration_details'],
            function(r) {
                if (r) {
                    if (r.custom_default_port) {
                        frm.set_value('default_port', r.custom_default_port);
                        set_port_filter(frm);
                        const first_port = r.custom_default_port.split(',')[0].trim();
                        frappe.db.exists('Port', first_port).then(exists => {
                            if (exists) {
                                frm.set_value('port', first_port);
                            }
                        });
                    }
                    if (r.default_currency) {
                        frm.set_value('currency', r.default_currency);
                    }
                    frm._company_gstin = r.tax_id || '';
                    frm.set_value('company_gstin', r.tax_id || '');
                    frm.set_value('company_pan', r.custom_pan || '');

                    // Format & set Company Address & Details
                    let details_arr = [];
                    if (r.registration_details) details_arr.push(r.registration_details);
                    if (r.tax_id) details_arr.push('Tax ID / GSTIN: ' + r.tax_id);
                    if (r.custom_pan) details_arr.push('PAN: ' + r.custom_pan);

                    if (details_arr.length > 0) {
                        frm.set_value('company_address', details_arr.join('\n'));
                    }

                    // Letter Head selection: fetch default_letter_head from Company first
                    if (r.default_letter_head) {
                        frm.set_value('letter_head', r.default_letter_head);
                    } else {
                        const company_name = (frm.doc.company || '').toLowerCase();
                        const country = (r.country || '').toLowerCase();
                        let lh = 'India (Sarveksha Realty)';
                        if (company_name.includes('botswana') || country.includes('botswana')) lh = 'Botswana (Sarveksha Botswana)';
                        else if (company_name.includes('baani')) lh = 'Cameroon (Baani Minerals)';
                        else if (company_name.includes('mining') || country.includes('cameroon')) lh = 'Cameroon (Sarveksha Mining SARL)';
                        else if (company_name.includes('bstp') || country.includes('guinea')) lh = 'Guinea (Sarveksha BSTP SAS)';
                        else if (company_name.includes('sl limited') || country.includes('sierra')) lh = 'Sierra Leone (Sarveksha SL Limited)';
                        else if (country.includes('india')) lh = 'India (Sarveksha Realty)';
                        frm.set_value('letter_head', lh);
                    }

                    // Auto-select standard terms if not already set
                    if (!frm.doc.standard_terms) {
                        const company_name = (frm.doc.company || '').toLowerCase();
                        let default_t = 'Standard Export PO Terms';
                        if (frm.doc.is_lut_applicable) default_t = 'LUT Certificate Terms';
                        else if (company_name.includes('bstp')) default_t = 'Guinea BSTP SAS Procurement Terms';
                        else if (company_name.includes('mining') || company_name.includes('baani')) default_t = 'Cameroon Mining & Minerals Terms';
                        else if (company_name.includes('sl limited')) default_t = 'Sierra Leone Procurement Terms';
                        else if (company_name.includes('botswana')) default_t = 'Botswana Mining & Equipment Terms';
                        else default_t = 'Standard Export PO Terms';

                        frm.set_value('standard_terms', default_t);
                        frm.trigger('standard_terms');
                    }
                }
                calculate_gst_and_totals(frm);
            }
        );
    },

    // ─── VENDOR TRIGGER ───────────────────────────────────────
    vendor: function(frm) {
        if (!frm.doc.vendor) return;

        frappe.db.get_value('Supplier', frm.doc.vendor,
            ['tax_id', 'custom_pan', 'custom_bank_name', 'custom_account_number', 'custom_ifsc'],
            function(r) {
                if (!r) return;
                if (r.tax_id) frm.set_value('vendor_gstin', r.tax_id);
                if (r.custom_pan) frm.set_value('vendor_pan', r.custom_pan);
                if (r.custom_bank_name) frm.set_value('vendor_bank_name', r.custom_bank_name);
                if (r.custom_account_number) frm.set_value('vendor_account_number', r.custom_account_number);
                if (r.custom_ifsc) frm.set_value('vendor_ifsc', r.custom_ifsc);

                frm._vendor_gstin = r.tax_id || '';
                calculate_gst_and_totals(frm);
            }
        );
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
            frm.set_value('standard_terms', 'LUT Certificate Terms');
            frm.trigger('standard_terms');
        }
        calculate_gst_and_totals(frm);
    },
    // ─── INDIVIDUAL EQUIPMENT ENTRY TRIGGERS ──────────────────
    equipment: function(frm) {
        if (!frm.doc.equipment) return;

        frappe.db.get_doc('Equipment', frm.doc.equipment).then(doc => {
            frm.set_value('equipment_name', doc.equipment_name || '');
            frm.set_value('hsn_code', doc.hsn_code || '');
            frm.set_value('brand', doc.brand || '');
            frm.set_value('manufacturer', doc.manufacturer || '');
            frm.set_value('unit', doc.unit || 'Nos');
            frm.set_value('specification', doc.specification || '');

            const cost = flt(doc.approx_cost_inr) || flt(doc.last_purchase_cost_inr) || 10000;
            const gst_pct = flt(doc.gst_percentage) || 18;

            frm.set_value('rate', cost);
            frm.set_value('gst_percentage', gst_pct);
        });
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
        if (frm.doc.standard_terms) {
            frappe.db.get_value('Terms and Conditions', frm.doc.standard_terms, 'terms', (r) => {
                if (r && r.terms) {
                    frm.set_df_property('terms_preview', 'options', r.terms);
                } else {
                    frm.set_df_property('terms_preview', 'options', '');
                }
            });
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

        frappe.db.get_doc('Equipment', row.equipment).then(doc => {
            frappe.model.set_value(cdt, cdn, 'equipment_name', doc.equipment_name || '');
            frappe.model.set_value(cdt, cdn, 'hsn_code', doc.hsn_code || '');
            frappe.model.set_value(cdt, cdn, 'brand', doc.brand || '');
            frappe.model.set_value(cdt, cdn, 'manufacturer', doc.manufacturer || '');
            frappe.model.set_value(cdt, cdn, 'unit', doc.unit || 'Nos');
            frappe.model.set_value(cdt, cdn, 'specification', doc.specification || '');
            
            const cost = flt(doc.approx_cost_inr) || flt(doc.last_purchase_cost_inr) || 10000;
            const gst_pct = flt(doc.gst_percentage) || 18;
            
            frappe.model.set_value(cdt, cdn, 'rate', cost);
            frappe.model.set_value(cdt, cdn, 'gst_percentage', gst_pct);

            calculate_gst_and_totals(frm);
        });
    },

    quantity: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    rate: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    discount_percent: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    gst_percentage: function(frm, cdt, cdn) { calculate_gst_and_totals(frm); },
    items_remove: function(frm) { calculate_gst_and_totals(frm); }
});

// ─── MASTER CALCULATION ENGINE ────────────────────────────────
function calculate_gst_and_totals(frm) {
    const is_lut = (frm.doc.is_lut_applicable && frm.doc.company && frm.doc.company.includes("Sarveksha Realty"));
    
    let total_taxable_value = 0;
    let total_item_tax = 0;

    if (frm.doc.items && frm.doc.items.length > 0) {
        frm.doc.items.forEach(row => {
            if (is_lut) {
                row.gst_percentage = 0.1;
            }
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

            total_taxable_value += row.taxable_amount;
            total_item_tax += row.tax_amount;
        });
        frm.refresh_field('items');
    }

    const freight = flt(frm.doc.freight) || 0;
    const insurance = flt(frm.doc.insurance) || 0;
    const packing = flt(frm.doc.packing_charges) || 0;
    const other = flt(frm.doc.other_charges) || 0;
    const advance_pct = flt(frm.doc.advance_percentage) || 0;

    // GST Type Determination
    const vendor_gstin = (frm.doc.vendor_gstin || frm._vendor_gstin || '');
    const company_gstin = (frm.doc.company_gstin || frm._company_gstin || '');

    let gst_type = 'IGST';
    let cgst = 0, sgst = 0, igst = 0;

    if (vendor_gstin.length >= 2 && company_gstin.length >= 2 && vendor_gstin.substring(0, 2) === company_gstin.substring(0, 2)) {
        gst_type = 'CGST + SGST';
        cgst = total_item_tax / 2;
        sgst = total_item_tax / 2;
        igst = 0;
    } else {
        gst_type = 'IGST';
        igst = total_item_tax;
        cgst = 0;
        sgst = 0;
    }

    const grand_total = total_taxable_value + total_item_tax + freight + insurance + packing + other;
    const advance_amount = grand_total * (advance_pct / 100);
    const balance_due = grand_total - advance_amount;

    frm.set_value('taxable_value', flt(total_taxable_value, 2));
    frm.set_value('gst_type', gst_type);
    frm.set_value('cgst_amount', flt(cgst, 2));
    frm.set_value('sgst_amount', flt(sgst, 2));
    frm.set_value('igst_amount', flt(igst, 2));
    frm.set_value('tax_amount', flt(total_item_tax, 2));
    frm.set_value('grand_total', flt(grand_total, 2));
    frm.set_value('advance_amount', flt(advance_amount, 2));
    frm.set_value('balance_due', flt(balance_due, 2));
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
    const user_roles = frappe.user.get_roles();
    const has_verifier_role = user_roles.includes('PO Verifier') || user_roles.includes('Procurement Manager') || user_roles.includes('System Manager');
    const has_approver_role = user_roles.includes('PO Approver') || user_roles.includes('Procurement Manager') || user_roles.includes('System Manager');
    const is_generator = user_roles.includes('PO Generator');

    const state = frm.doc.workflow_state || 'Draft';

    // 1. Verifier comments: ONLY editable during 'Pending Verification' stage by authorized verifiers
    if (state === 'Pending Verification' && has_verifier_role) {
        frm.set_df_property('verifier_comments', 'read_only', 0);
    } else {
        frm.set_df_property('verifier_comments', 'read_only', 1);
    }

    // 2. Approver comments: ONLY editable during 'Pending Approval' stage by authorized approvers
    if (state === 'Pending Approval' && has_approver_role) {
        frm.set_df_property('approver_comments', 'read_only', 0);
    } else {
        frm.set_df_property('approver_comments', 'read_only', 1);
    }

    // 3. Ensure audit metadata fields are permanently read-only
    ['verified_by', 'verified_on', 'verifier_status', 'approved_by', 'approved_on', 'approver_status', 'prepared_by'].forEach(field => {
        frm.set_df_property(field, 'read_only', 1);
    });

    // 4. Lock entire form for PO Generator once submitted for verification
    if (is_generator && !user_roles.includes('Procurement Manager') && !user_roles.includes('System Manager')) {
        if (['Pending Verification', 'Pending Approval', 'Approved', 'Printed'].includes(state)) {
            frm.disable_form();
            frm.dashboard.clear_comment_input();
        }
    }
}
