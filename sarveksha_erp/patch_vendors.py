import frappe
import openpyxl

def execute():
    wb_old = openpyxl.load_workbook('/workspace/development/frappe-bench/apps/sarveksha_erp/datasets-needed/VendorList-sarveksha.xlsx')
    ws_old = wb_old.active
    
    old_data = {}
    for row in ws_old.iter_rows(min_row=2, values_only=True):
        if row[1]:
            name = str(row[1]).strip()
            old_data[name] = row
            
    updates = 0
    for name, old_row in old_data.items():
        if frappe.db.exists("Supplier", name):
            # Check Bank Details (cols 4, 5, 6, 7)
            bank_name = str(old_row[4]).strip() if old_row[4] else None
            branch = str(old_row[5]).strip() if old_row[5] else None
            ac_no = str(old_row[6]).strip() if old_row[6] else None
            ifsc = str(old_row[7]).strip() if old_row[7] else None
            
            supplier = frappe.get_doc("Supplier", name)
            changed = False
            
            if bank_name and bank_name != 'None' and not supplier.custom_bank_name:
                supplier.custom_bank_name = bank_name
                changed = True
            if branch and branch != 'None' and not supplier.custom_bank_branch:
                supplier.custom_bank_branch = branch
                changed = True
            if ac_no and ac_no != 'None' and not supplier.custom_account_number:
                supplier.custom_account_number = ac_no
                changed = True
            if ifsc and ifsc != 'None' and not supplier.custom_ifsc:
                supplier.custom_ifsc = ifsc
                changed = True
                
            if changed:
                print(f"Updating custom bank fields for Supplier: {name}")
                supplier.save(ignore_permissions=True)
                updates += 1
                
    frappe.db.commit()
    print(f"DONE! Made {updates} Supplier custom field updates.")
