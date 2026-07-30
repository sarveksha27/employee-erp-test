// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vendor Purchase Order', {

    // ─── ON FORM LOAD ─────────────────────────────────────────
    refresh: function(frm) {
        const colors = {
            'Draft': 'gray',
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

        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Print PO'), function() {
                frappe.set_route('print', 'Vendor Purchase Order', frm.doc.name);
            }, __('Actions'));
        }

        // Recalculate on every refresh to keep values consistent
        calculate_gst_and_totals(frm);
        set_port_filter(frm);
    },

    // ─── COMPANY TRIGGER ──────────────────────────────────────
    company: function(frm) {
        if (!frm.doc.company) return;

        frappe.db.get_value('Company', frm.doc.company,
            ['custom_default_port', 'default_currency', 'tax_id', 'country', 'custom_pan'],
            function(r) {
                if (r) {
                    if (r.custom_default_port) {
                        frm.set_value('default_port', r.custom_default_port);
                        set_port_filter(frm);
                        frappe.db.exists('Port', r.custom_default_port).then(exists => {
                            if (exists) {
                                frm.set_value('port', r.custom_default_port);
                            }
                        });
                    }
                    if (r.default_currency) {
                        frm.set_value('currency', r.default_currency);
                    }
                    frm._company_gstin = r.tax_id || '';
                    frm.set_value('company_gstin', r.tax_id || '');
                    frm.set_value('company_pan', r.custom_pan || '');

                    const country = (r.country || '').toLowerCase();
                    let lh = 'India (Sarveksha Realty)';
                    if (country.includes('india'))    lh = 'India (Sarveksha Realty)';
                    else if (country.includes('cameroon')) lh = 'Cameroon (Sarveksha Mining SARL)';
                    else if (country.includes('botswana')) lh = 'Botswana (Sarveksha Botswana)';
                    frm.set_value('letter_head', lh);
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
    vendor_gstin: function(frm) { calculate_gst_and_totals(frm); }
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
    let total_taxable_value = 0;
    let total_item_tax = 0;

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
