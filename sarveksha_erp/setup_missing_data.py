import frappe
from openpyxl import load_workbook
import os

def execute():
    frappe.set_user("Administrator")
    print("=" * 60)
    print("STARTING DATA SETUP...")
    print("=" * 60)

    # 1. CLEANUP OBSOLETE COMPANIES
    if frappe.db.exists("Company", "Baani Minerals"):
        frappe.delete_doc("Company", "Baani Minerals", force=True)
        print("  ✓ Removed obsolete company: Baani Minerals")

    # 2. CREATE & UPDATE OFFICIAL COMPANIES
    company_records = [
        {
            "company_name": "Sarveksha Realty and Inframine LLP",
            "abbr": "SRIL",
            "country": "India",
            "default_currency": "INR",
            "tax_id": "27AFTFS2557J1Z8",
            "custom_registration_no": "ACS-0698",
            "custom_import_export_code": "AFTFS2557J",
            "custom_default_port": "Mundra, JNPT",
            "phone_no": "+91 9769008220",
            "email": "sudheerg@sarveksha.com",
            "website": "www.sarveksha.com"
        },
        {
            "company_name": "Sarveksha BSTP SAS",
            "abbr": "SBSTP",
            "country": "Guinea",
            "default_currency": "USD",
            "tax_id": "684060320",
            "custom_registration_no": "RCCM / GN / TCC .2024. B. 02459",
            "custom_default_port": "Conakry",
            "phone_no": "+224 626407133",
            "email": "svbstp@gmail.com",
            "website": "www.sarveksha.com"
        },
        {
            "company_name": "Sarveksha Mining SARL",
            "abbr": "SMS",
            "country": "Cameroon",
            "default_currency": "USD",
            "custom_registration_no": "CM-NSI-02-2025-B12-00560",
            "custom_default_port": "Douala",
            "phone_no": "+237652280756",
            "email": "cameroonprojects@sarveksha.com",
            "website": "www.sarveksha.com"
        },
        {
            "company_name": "Baani Resources SARL",
            "abbr": "BRS",
            "country": "Cameroon",
            "default_currency": "USD",
            "custom_registration_no": "CM-NSI-02-2025-B12-00784",
            "custom_default_port": "Douala",
            "phone_no": "+237652280756",
            "email": "cameroonprojects@sarveksha.com",
            "website": "www.sarveksha.com"
        },
        {
            "company_name": "Sarveksha Botswana Proprietary Limited",
            "abbr": "SBPL",
            "country": "Botswana",
            "default_currency": "USD",
            "custom_registration_no": "BW00009608412",
            "custom_default_port": "Durban",
            "phone_no": "+237652280756",
            "email": "sudheerg@sarveksha.com",
            "website": "www.sarveksha.com"
        },
        {
            "company_name": "Sarveksha SL Limited",
            "abbr": "SSL",
            "country": "Sierra Leone",
            "default_currency": "USD",
            "tax_id": "1001412648",
            "custom_registration_no": "SLI 20624 SARVE22162",
            "custom_default_port": "Freetown",
            "phone_no": "+232 74899999",
            "email": "svbstp@gmail.com",
            "website": "www.sarveksha.com"
        },
        {
            "company_name": "Odhav Holdings",
            "abbr": "OH",
            "country": "Mauritius",
            "default_currency": "USD",
            "email": "svbstp@gmail.com",
            "website": "www.sarveksha.com"
        },
        {
            "company_name": "Globe Multitrade and Service LLC",
            "abbr": "GMT",
            "country": "United Arab Emirates",
            "default_currency": "USD",
            "website": "www.sarveksha.com"
        }
    ]

    for cdata in company_records:
        cname = cdata["company_name"]
        if not frappe.db.exists("Company", cname):
            doc = frappe.new_doc("Company")
            doc.update(cdata)
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Company: {cname}")
        else:
            for k, v in cdata.items():
                if k != "company_name":
                    frappe.db.set_value("Company", cname, k, v)
            print(f"  ✓ Updated Company: {cname}")

    frappe.db.commit()

    # 3. IMPORT VENDOR EXCEL DATA
    file_path = os.path.join(frappe.get_app_path("sarveksha_erp"), "..", "datasets-needed", "VendorList-sarveksha.xlsx")
    if os.path.exists(file_path):
        print(f"\nProcessing Vendor Data from {file_path}...")
        try:
            wb = load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
            
            name_idx = -1
            group_idx = -1
            
            for i, header in enumerate(headers):
                if header.lower() == "supplier name" or header.lower() == "name" or header.lower() == "supplier":
                    name_idx = i
                elif "group" in header.lower():
                    group_idx = i
                    
            if name_idx == -1:
                name_idx = 0
                
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