import frappe

def execute():
    print("=" * 60)
    print("FULL SYSTEM AUDIT REPORT")
    print("=" * 60)

    # 1. Companies
    companies = frappe.get_all("Company", fields=["name", "abbr", "country", "default_currency"])
    print(f"\n--- Companies ({len(companies)}) ---")
    for c in companies:
        print(f"  {c['name']} | {c['country']} | {c['default_currency']}")

    # 2. Fiscal Years
    fiscal_years = frappe.get_all("Fiscal Year", fields=["name", "year_start_date", "year_end_date"])
    print(f"\n--- Fiscal Years ({len(fiscal_years)}) ---")
    for fy in fiscal_years:
        print(f"  {fy['name']} | {fy['year_start_date']} to {fy['year_end_date']}")

    # 3. Suppliers
    suppliers = frappe.get_all("Supplier", fields=["name", "supplier_name", "supplier_group", "custom_independent_company"])
    print(f"\n--- Suppliers ({len(suppliers)}) ---")
    for s in suppliers:
        print(f"  {s['supplier_name']} | Group: {s['supplier_group']} | IndComp: {s['custom_independent_company']}")

    # 4. Vendor Payments
    payments = frappe.get_all("Vendor Payment", fields=["name", "vendor", "amount", "status"])
    print(f"\n--- Vendor Payments ({len(payments)}) ---")
    for p in payments:
        print(f"  {p['name']} | Vendor: {p['vendor']} | Amount: {p['amount']} | Status: {p['status']}")

    # 5. Custom Fields
    custom_fields = frappe.get_all("Custom Field", filters={"module": "Vendor Management"}, fields=["name", "dt", "fieldname", "label"])
    print(f"\n--- Custom Fields ({len(custom_fields)}) ---")
    for cf in custom_fields:
        print(f"  {cf['name']} | DocType: {cf['dt']} | Field: {cf['fieldname']} | Label: {cf['label']}")

    # 6. Workspace Sidebar
    try:
        ws_sb = frappe.get_doc("Workspace Sidebar", "Vendor Management")
        print(f"\n--- Workspace Sidebar ---")
        print(f"  Standard: {ws_sb.standard} | Items: {len(ws_sb.items)}")
    except Exception as e:
        print(f"\n--- Workspace Sidebar: {e}")
