// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vendor Purchase Order', {

    // ─── ON FORM LOAD ─────────────────────────────────────────
    refresh: function(frm) {
        // Colour the status badge
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

        // Show print button when submitted
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Print PO'), function() {
                frappe.set_route('print', 'Vendor Purchase Order', frm.doc.name);
            }, __('Actions'));
        }
    },

    // ─── COMPANY TRIGGER ──────────────────────────────────────
    // Fetches default port from Company (works once Member 1 adds custom_default_port)
    company: function(frm) {
        if (!frm.doc.company) return;

        frappe.db.get_value('Company', frm.doc.company,
            ['custom_default_port', 'default_currency'],
            function(r) {
                if (r) {
                    // Set default port if the field exists on Company
                    if (r.custom_default_port) {
                        frm.set_value('port', r.custom_default_port);
                        frm.set_value('default_port', r.custom_default_port);
                    }
                    // Set default currency from company
                    if (r.default_currency) {
                        frm.set_value('currency', r.default_currency);
                    }
                }
            }
        );
    },

    // ─── VENDOR TRIGGER ───────────────────────────────────────
    // Fetches bank details and tax info from Supplier
    // Works once Member 2 adds custom fields to Supplier DocType
    vendor: function(frm) {
        if (!frm.doc.vendor) return;

        frappe.db.get_value('Supplier', frm.doc.vendor,
            [
                'tax_id',                    // GSTIN (standard ERPNext field)
                'custom_pan',                // PAN (Member 2 will add)
                'custom_bank_name',          // Bank Name (Member 2 will add)
                'custom_account_number',     // Account No (Member 2 will add)
                'custom_ifsc',               // IFSC (Member 2 will add)
            ],
            function(r) {
                if (!r) return;

                // Standard field - always works
                if (r.tax_id) frm.set_value('vendor_gstin', r.tax_id);

                // Custom fields - gracefully handles if not yet added by Member 2
                if (r.custom_pan) frm.set_value('vendor_pan', r.custom_pan);
                if (r.custom_bank_name) frm.set_value('vendor_bank_name', r.custom_bank_name);
                if (r.custom_account_number) frm.set_value('vendor_account_number', r.custom_account_number);
                if (r.custom_ifsc) frm.set_value('vendor_ifsc', r.custom_ifsc);
            }
        );
    },

    // ─── EQUIPMENT TRIGGER ────────────────────────────────────
    // TODO: This will be enabled when Member 3 pushes the Equipment DocType
    // For now it's a no-op since the equipment field is Data type (not Link)
    equipment: function(frm) {
        // When Member 3 is done, uncomment this block and change equipment field to Link(Equipment):
        /*
        if (!frm.doc.equipment) return;
        frappe.db.get_doc('Equipment', frm.doc.equipment).then(doc => {
            frm.set_value('equipment_name', doc.equipment_name);
            frm.set_value('hsn_code', doc.hsn_code);
            frm.set_value('brand', doc.brand);
            frm.set_value('manufacturer', doc.manufacturer);
            frm.set_value('unit', doc.unit);
            frm.set_value('specification', doc.specification);
            frm.set_value('country_of_origin', doc.country_of_origin);
        });
        */
    },

    // ─── GRAND TOTAL AUTO-CALCULATION ─────────────────────────
    // Triggers on any pricing field change
    rate: function(frm) { calculate_grand_total(frm); },
    quantity: function(frm) { calculate_grand_total(frm); },
    discount_percent: function(frm) { calculate_grand_total(frm); },
    tax_amount: function(frm) { calculate_grand_total(frm); },
    freight: function(frm) { calculate_grand_total(frm); },
    insurance: function(frm) { calculate_grand_total(frm); },
    packing_charges: function(frm) { calculate_grand_total(frm); },
    other_charges: function(frm) { calculate_grand_total(frm); },

    // ─── ADVANCE AMOUNT AUTO-CALCULATION ──────────────────────
    advance_percentage: function(frm) { calculate_advance(frm); },
    grand_total: function(frm) { calculate_advance(frm); },

});

// ─── HELPER FUNCTIONS ─────────────────────────────────────────

function calculate_grand_total(frm) {
    const rate = flt(frm.doc.rate) || 0;
    const qty = flt(frm.doc.quantity) || 1;
    const discount = flt(frm.doc.discount_percent) || 0;
    const tax = flt(frm.doc.tax_amount) || 0;
    const freight = flt(frm.doc.freight) || 0;
    const insurance = flt(frm.doc.insurance) || 0;
    const packing = flt(frm.doc.packing_charges) || 0;
    const other = flt(frm.doc.other_charges) || 0;

    const base_amount = rate * qty;
    const discount_amount = base_amount * (discount / 100);
    const net_amount = base_amount - discount_amount;
    const grand_total = net_amount + tax + freight + insurance + packing + other;

    frm.set_value('grand_total', grand_total);
    calculate_advance(frm);
}

function calculate_advance(frm) {
    const grand_total = flt(frm.doc.grand_total) || 0;
    const advance_pct = flt(frm.doc.advance_percentage) || 0;
    const advance = grand_total * (advance_pct / 100);
    frm.set_value('advance_amount', advance);
}
