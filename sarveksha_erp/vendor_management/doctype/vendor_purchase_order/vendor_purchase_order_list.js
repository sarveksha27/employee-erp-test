frappe.listview_settings['Vendor Purchase Order'] = {
    refresh: function(listview) {
        const user_roles = frappe.user.get_roles();
        const allowed_creator_roles = ["PO Generator", "Procurement Manager", "System Manager", "Administrator"];
        const has_creation_role = user_roles.some(role => allowed_creator_roles.includes(role));
        if (!has_creation_role) {
            listview.page.clear_primary_action();
        }
    }
};
