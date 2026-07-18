import frappe

def execute():
    cols = frappe.db.sql("DESC `tabVendor Payment`", as_dict=True)
    print("Vendor Payment columns:")
    for c in cols:
        print(f"  {c['Field']} ({c['Type']})")
