import frappe
from frappe.modules.export_file import export_to_files
def export_icon():
    export_to_files(record_list=[['Desktop Icon', 'Equipment Management']], record_module='Equipment Management')
    print("Exported successfully.")
