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


def after_install():
    copy_letterhead_assets()
    sync_workspace_sidebars()


def after_migrate():
    copy_letterhead_assets()
    sync_workspace_sidebars()
