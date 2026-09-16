import frappe
from sarveksha_erp.install import setup_roles_permissions_and_users


def execute():
    """
    Ensure standard Sarveksha roles, permissions, and users are provisioned
    across all environments (local, other devices, and Frappe Cloud).
    """
    setup_roles_permissions_and_users()
