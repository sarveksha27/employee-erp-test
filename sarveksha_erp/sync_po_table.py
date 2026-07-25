import frappe
from frappe.database.mariadb.schema import MariaDBTable

def execute():
    meta = frappe.get_meta("Vendor Purchase Order")
    db_table = MariaDBTable("Vendor Purchase Order", meta)
    db_table.validate()
    db_table.sync()
    frappe.db.commit()
    exists = frappe.db.table_exists("tabVendor Purchase Order")
    print(f"Table created: {exists}")
