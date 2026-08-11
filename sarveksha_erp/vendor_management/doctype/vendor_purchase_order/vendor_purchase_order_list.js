frappe.listview_settings['Vendor Purchase Order'] = {
    refresh: function(listview) {
        if (frappe.session.user === 'Administrator') return;

        const user_roles = frappe.user_roles;
        const is_verifier_or_approver = (user_roles.includes('PO Verifier') || user_roles.includes('PO Approver'));
        const is_generator = user_roles.includes('PO Generator');

        if (is_verifier_or_approver && !is_generator) {
            listview.page.clear_primary_action();
        }
    }
};
