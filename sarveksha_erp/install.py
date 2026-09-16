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

    # 1. Ensure Role exists
    role_name = "Vendor & Equipment Manager"
    if not frappe.db.exists("Role", role_name):
        role_doc = frappe.new_doc("Role")
        role_doc.role_name = role_name
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
        setup_custom_docperm(dt, role_name, full_crud)
        setup_custom_docperm(dt, "System Manager", full_crud)
        frappe.clear_cache(doctype=dt)

    # Grant read/write on dependent doctypes so creating/editing suppliers and companies works seamlessly
    rel_crud = {"read": 1, "write": 1, "create": 1, "report": 1}
    for dt in ["Address", "Contact", "Dynamic Link", "Supplier Group", "Port", "UOM"]:
        if frappe.db.exists("DocType", dt):
            setup_custom_docperm(dt, role_name, rel_crud)
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

    # 3. Ensure Admin user (admin@sarveksha.com / admin)
    admin_email = "admin@sarveksha.com"
    prev_install = frappe.flags.in_install
    frappe.flags.in_install = True
    try:
        if not frappe.db.exists("User", admin_email):
            admin_user = frappe.new_doc("User")
            admin_user.email = admin_email
            admin_user.first_name = "Admin"
            admin_user.last_name = "Administrator"
            admin_user.username = "admin"
            admin_user.send_welcome_email = 0
            admin_user.flags.ignore_permissions = True
            admin_user.insert()
        else:
            frappe.db.set_value("User", admin_email, {
                "first_name": "Admin",
                "last_name": "Administrator",
                "enabled": 1,
                "user_type": "System User",
            })

        add_roles_direct(admin_email, ["System Manager", "Administrator", "Desk User", "All"])
        try:
            update_password(admin_email, "admin")
        except Exception:
            pass

        # Ensure Administrator password
        try:
            update_password("Administrator", "admin")
        except Exception:
            pass

        # 4. Ensure Master Data Manager user (master_manager@sarveksha.com and vendor_manager@sarveksha.com)
        for email, username, first_name in [
            ("master_manager@sarveksha.com", "master_manager", "Master Data Manager"),
            ("vendor_manager@sarveksha.com", "vendor_manager", "Vendor & Company Manager"),
        ]:
            if not frappe.db.exists("User", email):
                u = frappe.new_doc("User")
                u.email = email
                u.first_name = first_name
                u.username = username
                u.user_type = "System User"
                u.send_welcome_email = 0
                u.flags.ignore_permissions = True
                u.insert()
            else:
                frappe.db.set_value("User", email, {
                    "first_name": first_name,
                    "enabled": 1,
                    "user_type": "System User",
                })

            add_roles_direct(email, ["Vendor & Equipment Manager", "Desk User", "All", "PO Generator"])
            try:
                update_password(email, "admin")
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
