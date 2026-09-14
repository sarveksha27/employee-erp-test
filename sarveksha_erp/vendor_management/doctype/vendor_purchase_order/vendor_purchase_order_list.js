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
    }
};
