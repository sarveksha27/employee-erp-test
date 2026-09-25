import os
import shutil
import frappe


def copy_letterhead_assets():
    """Copy bundled letterhead assets to site public files directory so print formats display correctly."""
    app_files_dir = frappe.get_app_path("sarveksha_erp", "public", "files")
    if not os.path.exists(app_files_dir):
        return

    site_files_dir = frappe.get_site_path("public", "files")
    os.makedirs(site_files_dir, exist_ok=True)

    for fname in os.listdir(app_files_dir):
        src = os.path.join(app_files_dir, fname)
        dst = os.path.join(site_files_dir, fname)
        if os.path.isfile(src) and not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass


def sync_workspace_sidebars():
    """Ensure Workspace Sidebar documents are forcefully reloaded from app definitions."""
    if not frappe.db.table_exists("Workspace Sidebar"):
        return

    try:
        from frappe.modules.import_file import import_file_by_path
        sidebar_paths = [
            frappe.get_app_path("sarveksha_erp", "vendor_management", "workspace_sidebar", "vendor_management", "vendor_management.json"),
            frappe.get_app_path("sarveksha_erp", "equipment_management", "workspace_sidebar", "equipment_management", "equipment_management.json"),
        ]
        for p in sidebar_paths:
            if os.path.exists(p):
                import_file_by_path(p, force=True)
        frappe.db.commit()
    except Exception:
        pass


def setup_custom_docperm(parent, role, perms):
    """Helper to upsert a Custom DocPerm record."""
    filters = {"parent": parent, "role": role, "permlevel": 0}
    name = frappe.db.get_value("Custom DocPerm", filters, "name")
    if name:
        doc = frappe.get_doc("Custom DocPerm", name)
    else:
        doc = frappe.new_doc("Custom DocPerm")
        doc.parent = parent
        doc.parenttype = "DocType"
        doc.parentfield = "permissions"
        doc.role = role
        doc.permlevel = 0
    for k, v in perms.items():
        setattr(doc, k, v)
    doc.flags.ignore_permissions = True
    doc.save()


def setup_roles_permissions_and_users():
    """
    Sets up the Vendor & Equipment Manager role, full CRUD permissions for Vendors,
    Company, and Equipments, and provisions the Administrator and Master Data Manager users.
    """
    from frappe.utils.password import update_password

    # 1. Ensure Roles exist
    roles_to_ensure = [
        "Vendor & Equipment Manager",
        "PO Generator",
        "PO Verifier",
        "PO Approver",
        "Accounts Clerk",
        "Accounts Manager",
    ]
    for r in roles_to_ensure:
        if not frappe.db.exists("Role", r):
            role_doc = frappe.new_doc("Role")
            role_doc.role_name = r
            role_doc.desk_access = 1
            role_doc.flags.ignore_permissions = True
            role_doc.insert()

    # 2. Grant full CRUD permissions on Supplier, Company, Equipment to Vendor & Equipment Manager and System Manager
    full_crud = {
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "report": 1,
        "export": 1,
        "print": 1,
        "email": 1,
        "share": 1,
    }
    for dt in ["Supplier", "Company", "Equipment"]:
        setup_custom_docperm(dt, "Vendor & Equipment Manager", full_crud)
        setup_custom_docperm(dt, "System Manager", full_crud)
        frappe.clear_cache(doctype=dt)

    # Grant read/write on dependent doctypes so creating/editing suppliers and companies works seamlessly
    rel_crud = {"read": 1, "write": 1, "create": 1, "report": 1}
    for dt in ["Address", "Contact", "Dynamic Link", "Supplier Group", "Port", "UOM"]:
        if frappe.db.exists("DocType", dt):
            setup_custom_docperm(dt, "Vendor & Equipment Manager", rel_crud)
            frappe.clear_cache(doctype=dt)

    # 3. Finance role permissions: Accounts Clerk can create/read/write but NOT submit Payment Entry
    clerk_perms = {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "print": 1, "email": 1}
    manager_perms = {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1, "print": 1, "email": 1, "report": 1, "export": 1}

    for dt in ["Payment Entry", "Purchase Invoice", "Journal Entry"]:
        if frappe.db.exists("DocType", dt):
            setup_custom_docperm(dt, "Accounts Clerk", clerk_perms)
            setup_custom_docperm(dt, "Accounts Manager", manager_perms)
            frappe.clear_cache(doctype=dt)

    # 4. PROCUREMENT CONFIDENTIALITY FIREWALL — explicitly deny PO roles access to Payment Entry & Journal Entry
    no_access = {"read": 0, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "print": 0, "email": 0, "report": 0, "export": 0}
    for po_role in ["PO Generator", "PO Verifier", "PO Approver"]:
        for dt in ["Payment Entry", "Journal Entry"]:
            if frappe.db.exists("DocType", dt):
                setup_custom_docperm(dt, po_role, no_access)
                frappe.clear_cache(doctype=dt)

    def add_roles_direct(email, roles):
        for role in roles:
            if not frappe.db.exists("Has Role", {"parent": email, "role": role}):
                hr = frappe.new_doc("Has Role")
                hr.parent = email
                hr.parenttype = "User"
                hr.parentfield = "roles"
                hr.role = role
                hr.flags.ignore_permissions = True
                hr.insert()

    # 3. Provision all standard Sarveksha users
    users_to_provision = [
        {
            "email": "admin@sarveksha.com",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "Administrator",
            "roles": ["System Manager", "Administrator", "Desk User", "All"],
        },
        {
            "email": "po_generator@sarveksha.com",
            "username": "po_generator",
            "first_name": "PO Generator",
            "last_name": "Generator",
            "roles": ["PO Generator", "Desk User", "Purchase User", "Accounts User", "All"],
        },
        {
            "email": "po_verifier@sarveksha.com",
            "username": "po_verifier",
            "first_name": "PO Verifier",
            "last_name": "Verifier",
            "roles": ["PO Verifier", "Desk User", "Purchase User", "Accounts User", "All"],
        },
        {
            "email": "po_approver@sarveksha.com",
            "username": "po_approver",
            "first_name": "PO Approver",
            "last_name": "Approver",
            "roles": ["PO Approver", "Desk User", "Accounts Manager", "Purchase Manager", "All"],
        },
        {
            "email": "vendor_manager@sarveksha.com",
            "username": "vendor_manager",
            "first_name": "Vendor & Company Manager",
            "last_name": "",
            "roles": ["Vendor & Equipment Manager", "Desk User", "All", "PO Generator"],
        },
        {
            "email": "master_manager@sarveksha.com",
            "username": "master_manager",
            "first_name": "Master Data Manager",
            "last_name": "",
            "roles": ["Vendor & Equipment Manager", "Desk User", "All", "PO Generator"],
        },
        {
            "email": "finance_clerk1@sarveksha.com",
            "username": "finance_clerk1",
            "first_name": "Finance Clerk 1",
            "last_name": "",
            "roles": ["Accounts Clerk", "Accounts User", "Desk User", "All"],
        },
        {
            "email": "finance_clerk2@sarveksha.com",
            "username": "finance_clerk2",
            "first_name": "Finance Clerk 2",
            "last_name": "",
            "roles": ["Accounts Clerk", "Accounts User", "Desk User", "All"],
        },
        {
            "email": "finance_manager1@sarveksha.com",
            "username": "finance_manager1",
            "first_name": "Finance Manager 1",
            "last_name": "",
            "roles": ["Accounts Manager", "Accounts User", "Desk User", "All"],
        },
        {
            "email": "finance_manager2@sarveksha.com",
            "username": "finance_manager2",
            "first_name": "Finance Manager 2",
            "last_name": "",
            "roles": ["Accounts Manager", "Accounts User", "Desk User", "All"],
        },
    ]

    prev_install = frappe.flags.in_install
    frappe.flags.in_install = True
    try:
        for uinfo in users_to_provision:
            email = uinfo["email"]
            if not frappe.db.exists("User", email):
                u = frappe.new_doc("User")
                u.email = email
                u.first_name = uinfo["first_name"]
                u.last_name = uinfo.get("last_name") or ""
                u.username = uinfo["username"]
                u.user_type = "System User"
                u.send_welcome_email = 0
                u.flags.ignore_permissions = True
                u.insert()
            else:
                frappe.db.set_value("User", email, {
                    "first_name": uinfo["first_name"],
                    "last_name": uinfo.get("last_name") or "",
                    "enabled": 1,
                    "user_type": "System User",
                })

            add_roles_direct(email, uinfo["roles"])
            try:
                update_password(email, "admin")
            except Exception:
                pass

        # Ensure Administrator password
        try:
            update_password("Administrator", "admin")
        except Exception:
            pass
    finally:
        frappe.flags.in_install = prev_install

    frappe.db.commit()


def after_install():
    copy_letterhead_assets()
    sync_workspace_sidebars()
    setup_roles_permissions_and_users()


def after_migrate():
    copy_letterhead_assets()
    sync_workspace_sidebars()
    setup_roles_permissions_and_users()
