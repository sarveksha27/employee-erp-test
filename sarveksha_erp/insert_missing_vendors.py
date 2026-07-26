import frappe
import json
import os

def execute():
    file_path = "/workspace/development/frappe-bench/missing_vendors.json"
    if not os.path.exists(file_path):
        print("missing_vendors.json not found")
        return

    with open(file_path, "r") as f:
        vendors = json.load(f)

    for v in vendors:
        supplier_name = v.get("Company")
        if not frappe.db.exists("Supplier", supplier_name):
            supplier = frappe.new_doc("Supplier")
            supplier.supplier_name = supplier_name
            supplier.supplier_group = "Hardware"
            supplier.supplier_type = "Company"
            supplier.pan = v.get("PAN")
            supplier.custom_gstin = v.get("GSTIN")
            supplier.insert(ignore_permissions=True)
            print(f"Inserted Supplier: {supplier_name}")
            
            # Bank Details
            if v.get("Bank Name") or v.get("Account No."):
                bank = frappe.new_doc("Bank Account")
                bank.party_type = "Supplier"
                bank.party = supplier_name
                bank.bank = v.get("Bank Name")
                bank.bank_account_no = v.get("Account No.")
                bank.branch_code = v.get("IFSC")
                bank.insert(ignore_permissions=True)
                print(f"Inserted Bank details for {supplier_name}")

            # Contact
            if v.get("Contact person") or v.get("Contact Email"):
                contact = frappe.new_doc("Contact")
                contact.first_name = v.get("Contact person") or supplier_name
                contact.email_id = v.get("Contact Email")
                phone = v.get("Contact Phone")
                contact.mobile_no = str(phone) if phone and str(phone).lower() != "nan" else None
                contact.append("links", {
                    "link_doctype": "Supplier",
                    "link_name": supplier_name
                })
                contact.insert(ignore_permissions=True)
                print(f"Inserted Contact for {supplier_name}")
                
    frappe.db.commit()
    print("Done backfilling missing vendors.")
