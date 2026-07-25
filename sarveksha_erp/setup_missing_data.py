import frappe
from openpyxl import load_workbook
import os

def execute():
    frappe.set_user("Administrator")
    print("=" * 60)
    print("STARTING DATA SETUP...")
    print("=" * 60)

    # 1. CREATE MISSING COMPANIES
    companies = [
        {"company_name": "Sarveksha Realty and Inframine LLP", "abbr": "SRIL", "country": "India", "default_currency": "INR"},
        {"company_name": "Sarveksha BSTP SAS", "abbr": "SBSTP", "country": "Senegal", "default_currency": "XOF"},
        {"company_name": "Sarveksha Mining SARL", "abbr": "SMS", "country": "Guinea", "default_currency": "GNF"},
        {"company_name": "Sarveksha Botswana Proprietary Limited", "abbr": "SBPL", "country": "Botswana", "default_currency": "BWP"},
        {"company_name": "Odhav Holdings", "abbr": "OH", "country": "Mauritius", "default_currency": "USD"},
        {"company_name": "Sarveksha SL Limited", "abbr": "SSL", "country": "Sierra Leone", "default_currency": "SLL"},
        {"company_name": "Baani Minerals", "abbr": "BM", "country": "India", "default_currency": "INR"},
    ]

    for c_data in companies:
        if not frappe.db.exists("Company", c_data["company_name"]):
            doc = frappe.new_doc("Company")
            doc.update(c_data)
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Company: {c_data['company_name']}")
        else:
            print(f"  ✓ Company {c_data['company_name']} already exists.")
    
    frappe.db.commit()

    # 2. EXECUTE ORIGINAL SETUP SCRIPTS
    try:
        from sarveksha_erp.setup_vendor_module import execute as run_vendor
        run_vendor()
    except Exception as e:
        print("Error running setup_vendor_module:", e)

    try:
        from sarveksha_erp.setup_doctypes import execute as run_doctypes
        run_doctypes()
    except Exception as e:
        print("Error running setup_doctypes:", e)

    try:
        from sarveksha_erp.full_setup import execute as run_full
        run_full()
    except Exception as e:
        print("Error running full_setup:", e)

    # 3. IMPORT VENDOR EXCEL DATA
    file_path = os.path.join(frappe.get_app_path("sarveksha_erp"), "..", "datasets-needed", "VendorList-sarveksha.xlsx")
    if os.path.exists(file_path):
        print(f"\nProcessing Vendor Data from {file_path}...")
        try:
            wb = load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            # Assuming first row is headers. We find indices of required columns
            headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
            print(f"Found headers: {headers}")
            
            name_idx = -1
            group_idx = -1
            
            for i, header in enumerate(headers):
                if header.lower() == "supplier name" or header.lower() == "name" or header.lower() == "supplier":
                    name_idx = i
                elif "group" in header.lower():
                    group_idx = i
                    
            if name_idx == -1:
                name_idx = 0 # default to first column
                
            created_count = 0
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
                name = row[name_idx].value
                if not name:
                    continue
                name = str(name).strip()
                
                group = "All Supplier Groups"
                if group_idx != -1 and row[group_idx].value:
                    group_val = str(row[group_idx].value).strip()
                    if frappe.db.exists("Supplier Group", group_val):
                        group = group_val
                
                if not frappe.db.exists("Supplier", name):
                    supplier = frappe.new_doc("Supplier")
                    supplier.supplier_name = name
                    supplier.supplier_group = group
                    supplier.insert(ignore_permissions=True)
                    created_count += 1
                    
            frappe.db.commit()
            print(f"  ✓ Successfully imported {created_count} Suppliers.")
        except Exception as e:
            print(f"Error parsing Excel file: {e}")
    else:
        print(f"Excel file not found at {file_path}")

    print("\n✅ DATA SETUP COMPLETE.")