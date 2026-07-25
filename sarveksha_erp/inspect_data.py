import frappe
import json

def execute():
    print("--- SUPPLIERS ---")
    suppliers = frappe.get_all("Supplier", fields=["name", "supplier_name"])
    print(json.dumps(suppliers[:5], indent=2))
    
    print("--- GLOBAL DEFAULTS ---")
    print(frappe.db.get_single_value("Global Defaults", "default_company"))
    
    print("--- CUSTOM FIELDS ON SUPPLIER ---")
    fields = frappe.get_all("Custom Field", filters={"dt": "Supplier"}, fields=["fieldname", "fieldtype", "label"])
    print(json.dumps(fields, indent=2))
    
    print("--- SUPPLIER DOC TYPE FIELDS ---")
    meta = frappe.get_meta("Supplier")
    f_list = [{"fieldname": f.fieldname, "label": f.label, "fieldtype": f.fieldtype} for f in meta.fields]
    print(json.dumps([f for f in f_list if "bank" in (f["fieldname"] or "").lower() or "pan" in (f["fieldname"] or "").lower() or "gst" in (f["fieldname"] or "").lower()], indent=2))
