import frappe
from frappe.utils import getdate

def execute():
    print("=" * 60)
    print("COMPREHENSIVE CONFIGURATION SCRIPT")
    print("=" * 60)

    # ================================================================
    # 1. ADD MISSING COMPANY: Globe Multitrade and Service LLC
    # Boss said all companies are independent entities.
    # "Globe Multitrade and Service LLC" sounds UAE-based (LLC suffix)
    # Using USD as fallback since no country was specified
    # ================================================================
    if not frappe.db.exists("Company", "Globe Multitrade and Service LLC"):
        doc = frappe.get_doc({
            "doctype": "Company",
            "company_name": "Globe Multitrade and Service LLC",
            "abbr": "GMT",
            "country": "United Arab Emirates",
            "default_currency": "AED",
        })
        doc.insert(ignore_permissions=True)
        print("Created: Globe Multitrade and Service LLC (UAE, AED)")
    else:
        print("Already exists: Globe Multitrade and Service LLC")

    frappe.db.commit()

    # ================================================================
    # 2. CREATE FISCAL YEARS
    # - India: April to March (already exists as 2025-2026, 2026-2027)
    # - All others: January to December
    # ================================================================
    jan_dec_years = [
        ("2025", "2025-01-01", "2025-12-31"),
        ("2026", "2026-01-01", "2026-12-31"),
        ("2027", "2027-01-01", "2027-12-31"),
    ]

    non_india_company_names = [
        "Globe Multitrade and Service LLC",
        "Sarveksha BSTP SAS",
        "Sarveksha Mining SARL",
        "Sarveksha Botswana Proprietary Limited",
        "Odhav Holdings",
        "Sarveksha SL Limited",
        "Baani Minerals",
    ]

    for year_name, start, end in jan_dec_years:
        if not frappe.db.exists("Fiscal Year", year_name):
            fy = frappe.get_doc({
                "doctype": "Fiscal Year",
                "year": year_name,
                "year_start_date": start,
                "year_end_date": end,
                "companies": [{"company": c} for c in non_india_company_names if frappe.db.exists("Company", c)]
            })
            fy.insert(ignore_permissions=True)
            print(f"Created Fiscal Year: {year_name} ({start} to {end})")
        else:
            # If it exists but has no companies linked, add them
            fy = frappe.get_doc("Fiscal Year", year_name)
            existing_companies = [r.company for r in fy.companies]
            for c in non_india_company_names:
                if c not in existing_companies and frappe.db.exists("Company", c):
                    fy.append("companies", {"company": c})
            fy.save(ignore_permissions=True)
            print(f"Updated Fiscal Year: {year_name}")

    frappe.db.commit()

    # ================================================================
    # 3. ASSIGN CORRECT FISCAL YEARS TO EACH COMPANY
    # India companies -> Apr-Mar fiscal years (2025-2026, 2026-2027)
    # All others -> Jan-Dec fiscal years (2025, 2026, 2027)
    # ================================================================
    india_companies = [
        "Sarveksha Realty and Inframine LLP",
    ]
    india_fiscal_years = ["2025-2026", "2026-2027"]

    non_india_companies = [
        "Globe Multitrade and Service LLC",
        "Sarveksha BSTP SAS",
        "Sarveksha Mining SARL",
        "Sarveksha Botswana Proprietary Limited",
        "Odhav Holdings",
        "Sarveksha SL Limited",
        "Baani Minerals",
    ]
    non_india_fiscal_years = ["2025", "2026", "2027"]

    # Add India companies to India fiscal years
    for company_name in india_companies:
        for fy_name in india_fiscal_years:
            if frappe.db.exists("Fiscal Year", fy_name) and frappe.db.exists("Company", company_name):
                exists = frappe.db.exists("Fiscal Year Company", {"parent": fy_name, "company": company_name})
                if not exists:
                    fy = frappe.get_doc("Fiscal Year", fy_name)
                    fy.append("companies", {"company": company_name})
                    fy.save(ignore_permissions=True)
                    print(f"Linked {company_name} to FY {fy_name}")

    # Add non-India companies to Jan-Dec fiscal years
    for company_name in non_india_companies:
        for fy_name in non_india_fiscal_years:
            if frappe.db.exists("Fiscal Year", fy_name) and frappe.db.exists("Company", company_name):
                exists = frappe.db.exists("Fiscal Year Company", {"parent": fy_name, "company": company_name})
                if not exists:
                    fy = frappe.get_doc("Fiscal Year", fy_name)
                    fy.append("companies", {"company": company_name})
                    fy.save(ignore_permissions=True)
                    print(f"Linked {company_name} to FY {fy_name}")

    frappe.db.commit()

    # ================================================================
    # 4. DELETE DEMO TEST DATA
    # Remove the "Test Supplier" that was created as dummy data
    # ================================================================
    if frappe.db.exists("Supplier", "Test Supplier"):
        frappe.delete_doc("Supplier", "Test Supplier", ignore_permissions=True, force=True)
        print("Deleted dummy Test Supplier.")
    else:
        print("No dummy Test Supplier found.")

    frappe.db.commit()

    # ================================================================
    # 5. CREATE SUPPLIER GROUPS for better organization
    # ================================================================
    supplier_groups = [
        "Mining & Resources",
        "Construction & Infrastructure",
        "Equipment & Machinery",
        "Logistics & Transport",
        "Professional Services",
        "Technology",
        "Medical & Health",
        "Agriculture & Food",
    ]
    for sg_name in supplier_groups:
        if not frappe.db.exists("Supplier Group", sg_name):
            sg = frappe.get_doc({
                "doctype": "Supplier Group",
                "supplier_group_name": sg_name,
                "parent_supplier_group": "All Supplier Groups",
            })
            sg.insert(ignore_permissions=True)
            print(f"Created Supplier Group: {sg_name}")
        else:
            print(f"Already exists Supplier Group: {sg_name}")

    frappe.db.commit()
    print("\nAll done!")
