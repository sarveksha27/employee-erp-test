frappe.listview_settings['Vendor Purchase Order'] = {
    onload: function(listview) {
        // Remove standard "+ Add Vendor Purchase Order" primary button since dedicated buttons exist
        listview.page.clear_primary_action();

        const user_roles = frappe.user_roles;
        const is_generator_or_manager = user_roles.includes('PO Generator') || user_roles.includes('System Manager') || user_roles.includes('Administrator');

        if (is_generator_or_manager) {
            listview.page.add_inner_button(__('New External PO'), function() {
                frappe.new_doc('Vendor Purchase Order', { po_type: 'Vendor PO' });
            });
            listview.page.add_inner_button(__('New Internal PO'), function() {
                frappe.prompt([
                    {
                        fieldname: 'company',
                        label: __('Issuing Company'),
                        fieldtype: 'Link',
                        options: 'Company',
                        reqd: 1,
                        get_query: function() {
                            return {
                                filters: {
                                    name: ['!=', 'Sarveksha Realty and Inframine LLP']
                                }
                            };
                        }
                    }
                ], function(values) {
                    frappe.new_doc('Vendor Purchase Order', {
                        po_type: 'Internal PO',
                        vendor: 'Sarveksha Realty and Inframine LLP',
                        company: values.company
                    });
                }, __('New Internal PO'), __('Continue'));
            });
        }

        // Add PO Amount Summary button
        listview.page.add_inner_button(__('PO Amount Summary'), function() {
            show_po_summary_dialog(listview);
        });
    },

    refresh: function(listview) {
        // Always ensure standard primary "+ Add Vendor Purchase Order" button is hidden
        listview.page.clear_primary_action();

        // Add quick filter options for PO Type (All, External, Internal)
        if (!listview.po_type_filter_added) {
            listview.po_type_filter_added = true;

            listview.page.add_inner_button(__('All POs'), function() {
                listview.filter_area.remove('po_type');
                listview.refresh();
            }, __('Filter PO Type'));

            listview.page.add_inner_button(__('External POs'), function() {
                listview.filter_area.add('Vendor Purchase Order', 'po_type', '=', 'Vendor PO');
                listview.refresh();
            }, __('Filter PO Type'));

            listview.page.add_inner_button(__('Internal POs'), function() {
                listview.filter_area.add('Vendor Purchase Order', 'po_type', '=', 'Internal PO');
                listview.refresh();
            }, __('Filter PO Type'));
        }

        // Add Yearwise & Monthwise Quick Filters to List View
        if (!listview.date_quick_filters_added) {
            listview.date_quick_filters_added = true;

            const current_year = new Date().getFullYear();
            const prev_year = current_year - 1;

            // Year Filters
            listview.page.add_inner_button(__('All Years'), function() {
                listview.filter_area.remove('po_date');
                listview.refresh();
            }, __('Filter Year'));

            listview.page.add_inner_button(`${current_year} (Current)`, function() {
                listview.filter_area.remove('po_date');
                listview.filter_area.add('Vendor Purchase Order', 'po_date', 'Between', [`${current_year}-01-01`, `${current_year}-12-31`]);
                listview.refresh();
            }, __('Filter Year'));

            listview.page.add_inner_button(`${prev_year}`, function() {
                listview.filter_area.remove('po_date');
                listview.filter_area.add('Vendor Purchase Order', 'po_date', 'Between', [`${prev_year}-01-01`, `${prev_year}-12-31`]);
                listview.refresh();
            }, __('Filter Year'));

            // Month Filters
            listview.page.add_inner_button(__('Current Month'), function() {
                const now = new Date();
                const yr = now.getFullYear();
                const mo = String(now.getMonth() + 1).padStart(2, '0');
                const last_day = new Date(yr, now.getMonth() + 1, 0).getDate();
                listview.filter_area.remove('po_date');
                listview.filter_area.add('Vendor Purchase Order', 'po_date', 'Between', [`${yr}-${mo}-01`, `${yr}-${mo}-${last_day}`]);
                listview.refresh();
            }, __('Filter Month'));

            listview.page.add_inner_button(__('Previous Month'), function() {
                const now = new Date();
                const prev = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                const yr = prev.getFullYear();
                const mo = String(prev.getMonth() + 1).padStart(2, '0');
                const last_day = new Date(yr, prev.getMonth() + 1, 0).getDate();
                listview.filter_area.remove('po_date');
                listview.filter_area.add('Vendor Purchase Order', 'po_date', 'Between', [`${yr}-${mo}-01`, `${yr}-${mo}-${last_day}`]);
                listview.refresh();
            }, __('Filter Month'));

            listview.page.add_inner_button(__('Clear Month/Year Filter'), function() {
                listview.filter_area.remove('po_date');
                listview.refresh();
            }, __('Filter Month'));
        }
    }
};

function show_po_summary_dialog(listview) {
    const now = new Date();
    const current_year = now.getFullYear();
    const current_month_num = now.getMonth() + 1;
    const today = frappe.datetime.get_today();
    const first_day_month = frappe.datetime.month_start();

    const month_options = [
        '1 - January', '2 - February', '3 - March', '4 - April',
        '5 - May', '6 - June', '7 - July', '8 - August',
        '9 - September', '10 - October', '11 - November', '12 - December'
    ];

    const d = new frappe.ui.Dialog({
        title: __('PO Generated Amount Summary & Analytics'),
        size: 'large',
        fields: [
            {
                fieldname: 'sec_period_selection',
                fieldtype: 'Section Break',
                label: __('Period & Filtering')
            },
            {
                fieldname: 'filter_mode',
                label: __('Filter Mode'),
                fieldtype: 'Select',
                options: 'Monthwise\nYearwise\nCustom Date Range',
                default: 'Monthwise',
                reqd: 1
            },
            {
                fieldname: 'col_break_mode',
                fieldtype: 'Column Break'
            },
            {
                fieldname: 'filter_year',
                label: __('Year'),
                fieldtype: 'Select',
                options: `${current_year}\n${current_year - 1}\n${current_year - 2}\n${current_year - 3}`,
                default: String(current_year),
                depends_on: 'eval:doc.filter_mode != "Custom Date Range"'
            },
            {
                fieldname: 'filter_month',
                label: __('Month'),
                fieldtype: 'Select',
                options: '\n' + month_options.join('\n'),
                default: month_options[current_month_num - 1],
                depends_on: 'eval:doc.filter_mode == "Monthwise"'
            },
            {
                fieldname: 'sec_custom_dates',
                fieldtype: 'Section Break',
                label: __('Custom Range'),
                depends_on: 'eval:doc.filter_mode == "Custom Date Range"'
            },
            {
                fieldname: 'from_date',
                label: __('From Date'),
                fieldtype: 'Date',
                default: first_day_month
            },
            {
                fieldname: 'col_break_1',
                fieldtype: 'Column Break'
            },
            {
                fieldname: 'to_date',
                label: __('To Date'),
                fieldtype: 'Date',
                default: today
            },
            {
                fieldname: 'sec_more_filters',
                fieldtype: 'Section Break',
                collapsible: 1,
                label: __('Additional Entity Filters (Optional)')
            },
            {
                fieldname: 'company',
                label: __('Company'),
                fieldtype: 'Link',
                options: 'Company'
            },
            {
                fieldname: 'vendor',
                label: __('Supplier / Vendor'),
                fieldtype: 'Link',
                options: 'Supplier'
            },
            {
                fieldname: 'col_break_2',
                fieldtype: 'Column Break'
            },
            {
                fieldname: 'status',
                label: __('Status'),
                fieldtype: 'Select',
                options: '\nDraft\nPending Verification\nVerification Returned\nPending Approval\nApproved\nPrinted\nSubmitted\nVendor Confirmed\nPartially Paid\nFully Paid\nShipped\nDelivered\nCancelled'
            },
            {
                fieldname: 'po_type',
                label: __('PO Type'),
                fieldtype: 'Select',
                options: '\nVendor PO\nInternal PO'
            },
            {
                fieldname: 'sec_results',
                fieldtype: 'Section Break',
                label: __('Summary Results')
            },
            {
                fieldname: 'summary_html',
                fieldtype: 'HTML'
            }
        ],
        primary_action_label: __('Generate Summary'),
        primary_action: function() {
            const values = d.get_values();
            if (!values) return;

            const mode = values.filter_mode;
            const args = {
                company: values.company || '',
                vendor: values.vendor || '',
                status: values.status || '',
                po_type: values.po_type || ''
            };

            if (mode === 'Yearwise') {
                args.year = values.filter_year || String(current_year);
            } else if (mode === 'Monthwise') {
                args.year = values.filter_year || String(current_year);
                if (values.filter_month) {
                    const mMatch = values.filter_month.match(/^(\d+)/);
                    args.month = mMatch ? parseInt(mMatch[1]) : values.filter_month;
                }
            } else {
                args.from_date = values.from_date;
                args.to_date = values.to_date;
            }

            frappe.call({
                method: 'sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order.get_po_generated_amount_summary',
                args: args,
                freeze: true,
                freeze_message: __('Calculating PO Summary...'),
                callback: function(r) {
                    if (r.message) {
                        // Dynamically update available years if provided by server
                        if (r.message.available_years && r.message.available_years.length > 0) {
                            const cur_yr_str = String(d.get_value('filter_year') || current_year);
                            const yr_options = r.message.available_years.map(String).join('\n');
                            d.set_df_property('filter_year', 'options', yr_options);
                            d.set_value('filter_year', cur_yr_str);
                        }
                        render_po_summary_html(d, r.message, listview);
                    }
                }
            });
        }
    });

    // Auto trigger on mode or year or month change
    d.fields_dict.filter_mode.$input.on('change', function() {
        setTimeout(() => d.get_primary_btn().trigger('click'), 100);
    });
    d.fields_dict.filter_year.$input.on('change', function() {
        setTimeout(() => d.get_primary_btn().trigger('click'), 100);
    });
    d.fields_dict.filter_month.$input.on('change', function() {
        setTimeout(() => d.get_primary_btn().trigger('click'), 100);
    });

    d.show();
    // Automatically generate initial summary
    d.get_primary_btn().trigger('click');
}

function render_po_summary_html(dialog, data, listview) {
    const $wrapper = dialog.get_field('summary_html').$wrapper;
    $wrapper.empty();

    let currency_badges = '';
    for (const curr in data.by_currency) {
        const cinfo = data.by_currency[curr];
        currency_badges += `
            <div style="background:#f8f9fa; border:1px solid #dcdcdc; border-radius:6px; padding:10px 14px; min-width:180px; margin-right:12px; margin-bottom:10px;">
                <div style="font-size:11px; text-transform:uppercase; color:#6c757d; font-weight:bold;">${curr} Total (${cinfo.count} POs)</div>
                <div style="font-size:18px; font-weight:bold; color:#171717; margin-top:2px;">${cinfo.formatted_total}</div>
                <div style="font-size:10px; color:#8d99ae; margin-top:3px;">Taxable: ${format_currency(cinfo.taxable_value, curr)} | Tax: ${format_currency(cinfo.tax_amount, curr)}</div>
            </div>
        `;
    }

    if (!currency_badges) {
        currency_badges = `
            <div style="color:#6c757d; font-style:italic; padding:8px 0;">No Purchase Orders found in the selected period.</div>
        `;
    }

    // Month breakdown table (shown if multiple months or Yearwise)
    let month_section = '';
    if (data.by_month && data.by_month.length > 0) {
        let month_rows = '';
        data.by_month.forEach(m => {
            month_rows += `
                <tr>
                    <td style="padding:6px 8px; border-bottom:1px solid #eee;"><strong>${m.label || m.month_name}</strong></td>
                    <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:center;">${m.count}</td>
                    <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right;">${format_currency(m.taxable_value)}</td>
                    <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right;"><strong>${format_currency(m.total_amount)}</strong></td>
                    <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right;">${m.percentage}%</td>
                    <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:center;">
                        <a href="javascript:void(0)" class="btn btn-default btn-xs btn-drill-month" data-year="${m.year}" data-month="${m.month}" style="font-size:10px; padding:2px 6px;">
                            ${__('View Month')}
                        </a>
                    </td>
                </tr>
            `;
        });

        month_section = `
            <div style="margin-bottom:16px;">
                <h6 style="margin-bottom:6px; font-weight:bold; color:#495057;">Month-by-Month Performance & Trend</h6>
                <table style="width:100%; border-collapse:collapse; font-size:12px; border:1px solid #e9ecef;">
                    <thead>
                        <tr style="background:#f1f3f5;">
                            <th style="padding:6px 8px; text-align:left;">Month</th>
                            <th style="padding:6px 8px; text-align:center;">PO Count</th>
                            <th style="padding:6px 8px; text-align:right;">Taxable Value</th>
                            <th style="padding:6px 8px; text-align:right;">Grand Total</th>
                            <th style="padding:6px 8px; text-align:right;">Share %</th>
                            <th style="padding:6px 8px; text-align:center;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${month_rows}
                    </tbody>
                </table>
            </div>
        `;
    }

    let status_rows = '';
    (data.by_status || []).forEach(st => {
        status_rows += `
            <tr>
                <td style="padding:6px 8px; border-bottom:1px solid #eee;"><strong>${st.status}</strong></td>
                <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:center;">${st.count}</td>
                <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right;">${format_currency(st.total_amount)}</td>
                <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right;">${st.percentage}%</td>
            </tr>
        `;
    });

    let vendor_rows = '';
    (data.by_vendor || []).slice(0, 10).forEach(v => {
        vendor_rows += `
            <tr>
                <td style="padding:6px 8px; border-bottom:1px solid #eee;">${v.vendor}</td>
                <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:center;">${v.count}</td>
                <td style="padding:6px 8px; border-bottom:1px solid #eee; text-align:right;">${format_currency(v.total_amount, v.currency)}</td>
            </tr>
        `;
    });

    const html = `
        <div style="padding:4px 0;">
            <div style="display:flex; flex-wrap:wrap; margin-bottom:14px;">
                <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:6px; padding:10px 14px; min-width:140px; margin-right:12px; margin-bottom:10px;">
                    <div style="font-size:11px; text-transform:uppercase; color:#4338ca; font-weight:bold;">Total PO Count</div>
                    <div style="font-size:20px; font-weight:bold; color:#312e81; margin-top:2px;">${data.total_pos}</div>
                    <div style="font-size:10px; color:#6366f1; margin-top:3px;">${data.period.from_date} to ${data.period.to_date}</div>
                </div>
                ${currency_badges}
            </div>

            ${month_section}

            <div style="display:flex; gap:16px; flex-wrap:wrap;">
                <div style="flex:1; min-width:280px;">
                    <h6 style="margin-bottom:6px; font-weight:bold; color:#495057;">Status Breakdown</h6>
                    <table style="width:100%; border-collapse:collapse; font-size:12px; border:1px solid #e9ecef;">
                        <thead>
                            <tr style="background:#f1f3f5;">
                                <th style="padding:6px 8px; text-align:left;">Status</th>
                                <th style="padding:6px 8px; text-align:center;">Count</th>
                                <th style="padding:6px 8px; text-align:right;">Amount</th>
                                <th style="padding:6px 8px; text-align:right;">Share</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${status_rows || '<tr><td colspan="4" style="text-align:center; padding:8px; color:#888;">No data</td></tr>'}
                        </tbody>
                    </table>
                </div>

                <div style="flex:1; min-width:280px;">
                    <h6 style="margin-bottom:6px; font-weight:bold; color:#495057;">Top Vendors</h6>
                    <table style="width:100%; border-collapse:collapse; font-size:12px; border:1px solid #e9ecef;">
                        <thead>
                            <tr style="background:#f1f3f5;">
                                <th style="padding:6px 8px; text-align:left;">Supplier</th>
                                <th style="padding:6px 8px; text-align:center;">Count</th>
                                <th style="padding:6px 8px; text-align:right;">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${vendor_rows || '<tr><td colspan="3" style="text-align:center; padding:8px; color:#888;">No data</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>

            <div style="margin-top:16px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11px; color:#6c757d;">
                    ${__('Period')}: <strong>${data.period.from_date}</strong> to <strong>${data.period.to_date}</strong>
                </span>
                <button class="btn btn-primary btn-sm" id="btn-filter-listview" style="font-size:11px;">
                    <i class="octicon octicon-filter"></i> ${__('Apply This Period to List View')}
                </button>
            </div>
        </div>
    `;

    $wrapper.html(html);

    // Apply period to desk list view
    $wrapper.find('#btn-filter-listview').on('click', function() {
        dialog.hide();
        listview.filter_area.remove('po_date');
        listview.filter_area.add('Vendor Purchase Order', 'po_date', 'Between', [data.period.from_date, data.period.to_date]);
        listview.refresh();
    });

    // Drill down to month from table
    $wrapper.find('.btn-drill-month').on('click', function() {
        const yr = $(this).data('year');
        const mo = $(this).data('month');
        dialog.set_value('filter_mode', 'Monthwise');
        dialog.set_value('filter_year', String(yr));
        // Find matching month in options
        const m_options = [
            '1 - January', '2 - February', '3 - March', '4 - April',
            '5 - May', '6 - June', '7 - July', '8 - August',
            '9 - September', '10 - October', '11 - November', '12 - December'
        ];
        dialog.set_value('filter_month', m_options[parseInt(mo) - 1]);
        dialog.get_primary_btn().trigger('click');
    });
}
