// Copyright (c) 2026, Sarveksha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Proforma Invoice', {
    setup: function(frm) {
        // Enforce: ONLY Internal POs can be selected (No External/Vendor POs)
        frm.set_query('internal_po', function() {
            return {
                filters: {
                    'po_type': 'Internal PO'
                }
            };
        });
    },

    refresh: function(frm) {
        // Enforce: Items are strictly linked from PO - disable row add/delete
        frm.set_df_property('items', 'cannot_add_rows', true);
        frm.set_df_property('items', 'cannot_delete_rows', true);
        if (frm.fields_dict['items'] && frm.fields_dict['items'].grid) {
            frm.fields_dict['items'].grid.cannot_add_rows = true;
        }

        // Custom print format button
        if (!frm.doc.__islocal) {
            const open_pi_pdf = function() {
                const url = frappe.urllib.get_full_url(
                    `/api/method/frappe.utils.print_format.download_pdf?doctype=Proforma%20Invoice&name=${encodeURIComponent(frm.doc.name)}&format=${encodeURIComponent('Proforma Invoice Format')}`
                );
                window.open(url, '_blank');
            };
            frm.add_custom_button(__('Print Payment Invoice'), open_pi_pdf);
            frm.change_custom_button_type(__('Print Payment Invoice'), null, 'primary');
            frm.print_doc = open_pi_pdf;
        }

        // ── CANCEL PI BUTTON (Submitted docs — docstatus == 1) ─────────────
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Cancel PI'), function() {
                frappe.prompt(
                    [{
                        fieldname: 'reason',
                        fieldtype: 'Small Text',
                        label: 'Cancellation Reason',
                        reqd: 1,
                        description: 'Please provide the reason for cancelling this Proforma Invoice.'
                    }],
                    function(values) {
                        frappe.dom.freeze(__('Cancelling Proforma Invoice...'));
                        frappe.call({
                            method: 'sarveksha_erp.vendor_management.doctype.proforma_invoice.proforma_invoice.cancel_proforma_invoice',
                            args: {
                                pi_name: frm.doc.name,
                                reason: values.reason
                            },
                            callback: function(r) {
                                frappe.dom.unfreeze();
                                if (!r.exc) {
                                    frappe.show_alert({
                                        message: __('Proforma Invoice {0} cancelled successfully.', [frm.doc.name]),
                                        indicator: 'orange'
                                    });
                                    frm.reload_doc();
                                }
                            },
                            error: function() {
                                frappe.dom.unfreeze();
                            }
                        });
                    },
                    __('Cancel Proforma Invoice'),
                    __('Confirm Cancellation')
                );
            });
            // Make Cancel PI visually prominent (red/danger)
            frm.change_custom_button_type(__('Cancel PI'), null, 'danger');
        }

        // ── DELETE PI BUTTON (Draft docs — docstatus == 0, not new) ────────
        if (frm.doc.docstatus === 0 && !frm.doc.__islocal) {
            frm.add_custom_button(__('Delete PI'), function() {
                frappe.confirm(
                    __('Are you sure you want to permanently delete Proforma Invoice <b>{0}</b>? This action cannot be undone.', [frm.doc.name]),
                    function() {
                        frappe.dom.freeze(__('Deleting Proforma Invoice...'));
                        frappe.call({
                            method: 'frappe.client.delete',
                            args: {
                                doctype: 'Proforma Invoice',
                                name: frm.doc.name
                            },
                            callback: function(r) {
                                frappe.dom.unfreeze();
                                if (!r.exc) {
                                    frappe.show_alert({
                                        message: __('Proforma Invoice deleted successfully.'),
                                        indicator: 'green'
                                    });
                                    frappe.set_route('List', 'Proforma Invoice');
                                }
                            },
                            error: function() {
                                frappe.dom.unfreeze();
                            }
                        });
                    }
                );
            });
        }

        calculate_pi_totals(frm);
    },


    internal_po: function(frm) {
        if (!frm.doc.internal_po) return;

        frappe.db.get_value('Proforma Invoice', {
            internal_po: frm.doc.internal_po,
            docstatus: ['!=', 2],
            name: ['!=', frm.doc.name || '']
        }, 'name').then(r => {
            const existing_pi = r && r.message && r.message.name;
            if (existing_pi) {
                frappe.msgprint({
                    title: __('Proforma Invoice Already Exists'),
                    indicator: 'orange',
                    message: __('Proforma Invoice <b>{0}</b> has already been generated for Internal PO <b>{1}</b>. Another PI cannot be generated.<br><br>Passing on to the existing PI...', [existing_pi, frm.doc.internal_po])
                });
                frappe.set_route('Form', 'Proforma Invoice', existing_pi);
                return;
            }

            frappe.call({
                method: 'sarveksha_erp.vendor_management.doctype.proforma_invoice.proforma_invoice.get_internal_po_details',
                args: { internal_po: frm.doc.internal_po },
                callback: function(res) {
                    if (res.message) {
                        const data = res.message;
                        frm.set_value('po_reference_no', data.po_reference_no);
                        frm.set_value('po_date', data.po_date);
                        frm.set_value('buyer', data.buyer);
                        frm.set_value('buyer_address', data.buyer_address);
                        frm.set_value('currency', data.currency || 'USD');
                        frm.set_value('port_of_loading', data.port_of_loading || 'Mundra');
                        frm.set_value('port_of_discharge', data.port_of_discharge || 'Durban');
                        frm.set_value('final_destination', data.final_destination || '');
                        frm.set_value('margin_percentage', data.margin_percentage || 5.0);
                        frm.set_value('advance_percentage', data.advance_percentage || 100.0);

                        // Note: Logistics fields are intentionally NOT fetched automatically
                        // User must manually enter freight, insurance, packing, other charges

                        // Populate line items
                        frm.clear_table('items');
                        if (data.items && data.items.length > 0) {
                            data.items.forEach(it => {
                                let row = frm.add_child('items');
                                row.equipment = it.equipment;
                                row.item_description = it.item_description;
                                row.make_model = it.make_model;
                                row.hsn_code = it.hsn_code;
                                row.unit = it.unit;
                                row.quantity = it.quantity;
                                row.base_rate = it.base_rate;
                                row.amount = flt(it.quantity * it.base_rate, 2);
                            });
                        }
                        frm.refresh_field('items');
                        calculate_pi_totals(frm);
                    }
                }
            });
        });
    },

    margin_percentage: function(frm) {
        let margin = flt(frm.doc.margin_percentage);
        if (margin < 5.0 || margin > 30.0) {
            frappe.show_alert({
                message: __('Margin must be between 5% and 30%'),
                indicator: 'orange'
            });
        }
        calculate_pi_totals(frm);
    },

    freight: function(frm) { calculate_pi_totals(frm); },
    insurance: function(frm) { calculate_pi_totals(frm); },
    packing_charges: function(frm) { calculate_pi_totals(frm); },
    other_charges: function(frm) { calculate_pi_totals(frm); },
    advance_percentage: function(frm) { calculate_pi_totals(frm); }
});

frappe.ui.form.on('Proforma Invoice Item', {
    quantity: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.amount = flt(flt(row.quantity) * flt(row.base_rate), 2);
        frm.refresh_field('items');
        calculate_pi_totals(frm);
    },
    base_rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.amount = flt(flt(row.quantity) * flt(row.base_rate), 2);
        frm.refresh_field('items');
        calculate_pi_totals(frm);
    },
    items_remove: function(frm) {
        calculate_pi_totals(frm);
    }
});

function calculate_pi_totals(frm) {
    let total_items = 0;
    if (frm.doc.items && frm.doc.items.length > 0) {
        frm.doc.items.forEach(row => {
            const qty = flt(row.quantity) || 1;
            const rate = flt(row.base_rate) || 0;
            row.amount = flt(qty * rate, 2);
            total_items += row.amount;
        });
        frm.refresh_field('items');
    }

    const freight = flt(frm.doc.freight) || 0;
    const insurance = flt(frm.doc.insurance) || 0;
    const packing = flt(frm.doc.packing_charges) || 0;
    const other = flt(frm.doc.other_charges) || 0;
    const total_logistics = flt(freight + insurance + packing + other, 2);

    let margin_pct = flt(frm.doc.margin_percentage);
    if (margin_pct < 5.0) margin_pct = 5.0;
    if (margin_pct > 30.0) margin_pct = 30.0;

    const base_for_margin = total_items + total_logistics;
    const margin_amount = flt(base_for_margin * (margin_pct / 100), 2);
    const grand_total = flt(total_items + total_logistics + margin_amount, 2);

    const adv_pct = flt(frm.doc.advance_percentage) || 100.0;
    const advance_amount = flt(grand_total * (adv_pct / 100), 2);

    frm.set_value('total_item_amount', flt(total_items, 2));
    frm.set_value('total_logistics', total_logistics);
    frm.set_value('margin_amount', margin_amount);
    frm.set_value('grand_total', grand_total);
    frm.set_value('advance_amount', advance_amount);
}
