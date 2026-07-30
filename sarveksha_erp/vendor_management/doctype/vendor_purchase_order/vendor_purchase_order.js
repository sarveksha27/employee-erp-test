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
            ['custom_default_port', 'default_currency', 'tax_id', 'country', 'custom_pan'],
            function(r) {
                if (r) {
                    if (r.custom_default_port) {
                        frm.set_value('default_port', r.custom_default_port);
                        set_port_filter(frm);
                        // Safely verify if the port exists or fallback to sub-parts (like "Mundra" from "Mumbai, Mundra")
                        frappe.db.exists('Port', r.custom_default_port).then(exists => {
                            if (exists) {
                                frm.set_value('port', r.custom_default_port);
                            } else {
                                // Try splitting by comma
                                const parts = r.custom_default_port.split(',').map(p => p.trim());
                                let check_part = (idx) => {
                                    if (idx >= parts.length) return;
                                    frappe.db.exists('Port', parts[idx]).then(exists_part => {
                                        if (exists_part) {
                                            frm.set_value('port', parts[idx]);
                                        } else {
                                            check_part(idx + 1);
                                        }
                                    });
                                };
                                check_part(0);
                            }
                        });
                    } else {
                        frm.set_value('default_port', '');
                        set_port_filter(frm);
                    }
                    if (r.default_currency) {
                        frm.set_value('currency', r.default_currency);
                    }
                    // Store company GSTIN for intra/inter-state GST determination
                    frm._company_gstin = r.tax_id || '';
                    frm.set_value('company_gstin', r.tax_id || '');
                    frm.set_value('company_pan', r.custom_pan || '');

                    // ── AUTO-SET LETTER HEAD BASED ON COUNTRY ──────────
                    const country = (r.country || '').toLowerCase();
                    let lh = 'India (Sarveksha Realty)'; // default fallback
                    if (country.includes('india'))    lh = 'India (Sarveksha Realty)';
                    else if (country.includes('cameroon')) lh = 'Cameroon (Sarveksha Mining SARL)';
                    else if (country.includes('botswana')) lh = 'Botswana (Sarveksha Botswana)';
                    // Sierra Leone, Guinea, UAE → fallback to India letterhead
                    frm.set_value('letter_head', lh);
                }
                // Recalculate GST type after company change
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

                // Store vendor GSTIN for intra/inter-state determination
                frm._vendor_gstin = r.tax_id || '';
                calculate_gst_and_totals(frm);
            }
        );
    },

    // ─── EQUIPMENT TRIGGER ────────────────────────────────────────
    equipment: function(frm) {
        if (!frm.doc.equipment) {
            frm.set_value('equipment_name', '');
            frm.set_value('hsn_code', '');
            frm.set_value('brand', '');
            frm.set_value('manufacturer', '');
            frm.set_value('unit', '');
            frm.set_value('specification', '');
            frm.set_value('country_of_origin', '');
            frm.set_value('gst_percentage', 0);
            calculate_gst_and_totals(frm);
            return;
        }
        frappe.db.get_doc('Equipment', frm.doc.equipment).then(doc => {
            frm.set_value('equipment_name', doc.equipment_name || '');
            frm.set_value('hsn_code', doc.hsn_code || '');
            frm.set_value('brand', doc.brand || '');
            frm.set_value('manufacturer', doc.manufacturer || '');
            frm.set_value('unit', doc.unit || '');
            frm.set_value('specification', doc.specification || '');
            frm.set_value('country_of_origin', doc.country_of_origin || '');

            // ─── KEY STEP: Pull GST % from Equipment master ───
            const gst_pct = flt(doc.gst_percentage) || 18; // Default 18% if not set
            frm.set_value('gst_percentage', gst_pct);

            calculate_gst_and_totals(frm);

            frappe.show_alert({
                message: `Equipment details loaded for "${doc.equipment_name}" | GST: ${gst_pct}%`,
                indicator: 'green'
            }, 4);
        }).catch(err => {
            frappe.show_alert({
                message: 'Could not fetch equipment details.',
                indicator: 'orange'
            }, 4);
        });
    },

    // ─── PRICING TRIGGERS ─────────────────────────────────────
    rate: function(frm) { calculate_gst_and_totals(frm); },
    quantity: function(frm) { calculate_gst_and_totals(frm); },
    discount_percent: function(frm) { calculate_gst_and_totals(frm); },
    gst_percentage: function(frm) { calculate_gst_and_totals(frm); },
    freight: function(frm) { calculate_gst_and_totals(frm); },
    insurance: function(frm) { calculate_gst_and_totals(frm); },
    packing_charges: function(frm) { calculate_gst_and_totals(frm); },
    other_charges: function(frm) { calculate_gst_and_totals(frm); },
    advance_percentage: function(frm) { calculate_gst_and_totals(frm); },
    vendor_gstin: function(frm) { calculate_gst_and_totals(frm); },
    is_lut_applicable: function(frm) {
        if (frm.doc.is_lut_applicable) {
            if (frm.doc.company && frm.doc.company.includes("Sarveksha Realty")) {
                frm.set_value('gst_percentage', 0.1);
            }
        } else {
            // Re-fetch GST % from equipment
            if (frm.doc.equipment) {
                frappe.db.get_value('Equipment', frm.doc.equipment, 'gst_percentage', (r) => {
                    if (r) {
                        frm.set_value('gst_percentage', flt(r.gst_percentage) || 18);
                    }
                });
            } else {
                frm.set_value('gst_percentage', 18);
            }
        }
        calculate_gst_and_totals(frm);
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

// ─── MASTER CALCULATION ENGINE ────────────────────────────────
/**
 * Full Indian GST Calculation Engine:
 *
 * 1. Determine Taxable Value = (Rate × Qty) − Discount
 * 2. Determine GST Type:
 *    - Extract first 2 digits of Vendor GSTIN (state code)
 *    - Extract first 2 digits of Company GSTIN (state code)
 *    - If SAME STATE → CGST + SGST (each = GST% / 2)
 *    - If DIFFERENT STATE or export → IGST (= GST%)
 * 3. Grand Total = Taxable Value + Total Tax + Freight + Insurance + Packing + Other
 * 4. Advance Amount = Grand Total × (Advance% / 100)
 * 5. Balance Due = Grand Total − Advance Amount
 */
function calculate_gst_and_totals(frm) {
    const rate = flt(frm.doc.rate) || 0;
    const qty = flt(frm.doc.quantity) || 1;
    const discount_pct = flt(frm.doc.discount_percent) || 0;
    
    let gst_pct = flt(frm.doc.gst_percentage) || 0;
    if (frm.doc.is_lut_applicable && frm.doc.company && frm.doc.company.includes("Sarveksha Realty")) {
        gst_pct = 0.1;
        if (frm.doc.gst_percentage !== 0.1) {
            frm.set_value('gst_percentage', 0.1);
        }
    }

    const freight = flt(frm.doc.freight) || 0;
    const insurance = flt(frm.doc.insurance) || 0;
    const packing = flt(frm.doc.packing_charges) || 0;
    const other = flt(frm.doc.other_charges) || 0;
    const advance_pct = flt(frm.doc.advance_percentage) || 0;

    // Step 1: Taxable Value
    const base_amount = rate * qty;
    const discount_amount = base_amount * (discount_pct / 100);
    const taxable_value = base_amount - discount_amount;

    // Step 2: GST Type Determination (Intra-state vs Inter-state)
    const vendor_gstin = (frm.doc.vendor_gstin || frm._vendor_gstin || '');
    const company_gstin = (frm._company_gstin || '');

    let gst_type = 'IGST'; // Default: IGST for inter-state or unknown
    let cgst = 0, sgst = 0, igst = 0, total_tax = 0;

    if (vendor_gstin.length >= 2 && company_gstin.length >= 2) {
        const vendor_state_code = vendor_gstin.substring(0, 2);
        const company_state_code = company_gstin.substring(0, 2);
        gst_type = (vendor_state_code === company_state_code) ? 'CGST + SGST' : 'IGST';
    } else if (vendor_gstin.length >= 2) {
        // If company GSTIN not set, default to IGST (safer for exports)
        gst_type = 'IGST';
    }

    // Step 3: Calculate GST components
    if (gst_type === 'CGST + SGST') {
        cgst = taxable_value * (gst_pct / 200); // half of GST%
        sgst = taxable_value * (gst_pct / 200); // half of GST%
        igst = 0;
        total_tax = cgst + sgst;
    } else {
        igst = taxable_value * (gst_pct / 100);
        cgst = 0;
        sgst = 0;
        total_tax = igst;
    }

    // Step 4: Grand Total
    const grand_total = taxable_value + total_tax + freight + insurance + packing + other;

    // Step 5: Advance & Balance
    const advance_amount = grand_total * (advance_pct / 100);
    const balance_due = grand_total - advance_amount;

    // ─── SET ALL VALUES ───────────────────────────────────────
    frm.set_value('taxable_value', flt(taxable_value, 2));
    frm.set_value('gst_type', gst_type);
    frm.set_value('cgst_amount', flt(cgst, 2));
    frm.set_value('sgst_amount', flt(sgst, 2));
    frm.set_value('igst_amount', flt(igst, 2));
    frm.set_value('tax_amount', flt(total_tax, 2));
    frm.set_value('grand_total', flt(grand_total, 2));
    frm.set_value('advance_amount', flt(advance_amount, 2));
    frm.set_value('balance_due', flt(balance_due, 2));
}

function set_port_filter(frm) {
    frm.set_query('port', function() {
        if (frm.doc.default_port) {
            const ports = frm.doc.default_port.split(',').map(p => p.trim()).filter(Boolean);
            if (ports.length > 0) {
                return {
                    filters: [
                        ['Port', 'name', 'in', ports]
                    ]
                };
            }
        }
        return {
            filters: {
                'is_active': 1
            }
        };
    });
}
