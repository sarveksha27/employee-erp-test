import frappe
import json
import os

def execute():
    try:
        # Update Doctype
        dt = frappe.get_doc("DocType", "Vendor Payment")
        dt.custom = 0
        dt.save(ignore_permissions=True)
        frappe.db.commit()
        print("Vendor Payment is now a standard doctype.")
        
        # Export again
        frappe.utils.commands.export_doc("DocType", "Vendor Payment")
        print("Exported standard doctype.")
    except Exception as e:
        print("Error:", e)
