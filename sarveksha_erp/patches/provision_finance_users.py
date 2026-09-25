import frappe
from sarveksha_erp.install import setup_roles_permissions_and_users


def execute():
    """
    Member 1 (Pavitra) - Provision finance roles, users, and confidentiality firewall.
    Idempotent: safe to run multiple times.
    """
    setup_roles_permissions_and_users()
    frappe.db.commit()
