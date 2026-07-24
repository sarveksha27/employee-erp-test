import frappe
from sarveksha_erp.setup_missing_data import execute as run_all_setup

def after_install():
    try:
        run_all_setup()
    except Exception as e:
        print("Error during after_install setup:", e)
