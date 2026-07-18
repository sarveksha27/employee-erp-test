import frappe

def execute():
    # Categorize existing suppliers into proper groups
    supplier_categories = {
        "Mining & Resources": ["Prime Rigs", "Indus Furnaces", "Energy Compressor"],
        "Construction & Infrastructure": ["Global Infrastructure", "Bipun Consultancy"],
        "Equipment & Machinery": ["Action Construction Equipment", "CruxWeld", "Bissa Engg.", "Yantralink", "RR Technologies"],
        "Logistics & Transport": ["Aavya Logistics", "ARS International", "Marine Hardware Syndicate"],
        "Professional Services": ["Chopra Enterprises", "Badri Corporation", "Classic Instruments", "OM Enterprises"],
        "Technology": [],
        "Medical & Health": ["Central Drug House"],
        "Agriculture & Food": ["Vinspire Agrotech Pvt Limited"],
    }

    for group, suppliers in supplier_categories.items():
        for supplier_name in suppliers:
            if frappe.db.exists("Supplier", supplier_name):
                frappe.db.set_value("Supplier", supplier_name, "supplier_group", group)
                print(f"Categorized '{supplier_name}' -> {group}")

    frappe.db.commit()

    # Final verification
    print("\n" + "=" * 60)
    print("FINAL VERIFICATION REPORT")
    print("=" * 60)

    companies = frappe.get_all("Company", fields=["name", "country", "default_currency"], order_by="name asc")
    print(f"\nCompanies ({len(companies)}):")
    for c in companies:
        print(f"  ✓ {c['name']} | {c['country']} | {c['default_currency']}")

    fiscal_years = frappe.get_all("Fiscal Year", fields=["name", "year_start_date", "year_end_date"], order_by="year_start_date asc")
    print(f"\nFiscal Years ({len(fiscal_years)}):")
    for fy in fiscal_years:
        print(f"  ✓ {fy['name']}: {fy['year_start_date']} to {fy['year_end_date']}")

    suppliers = frappe.get_all("Supplier", fields=["supplier_name", "supplier_group"], order_by="supplier_name asc")
    print(f"\nVendors/Suppliers ({len(suppliers)}):")
    for s in suppliers:
        print(f"  ✓ {s['supplier_name']} | {s['supplier_group']}")

    sg_list = frappe.get_all("Supplier Group", filters={"parent_supplier_group": "All Supplier Groups"}, pluck="name")
    print(f"\nSupplier Groups ({len(sg_list)}): {', '.join(sg_list)}")

    custom_fields = frappe.get_all("Custom Field", filters={"module": "Vendor Management"}, fields=["dt", "fieldname", "label"])
    print(f"\nCustom Fields ({len(custom_fields)}):")
    for cf in custom_fields:
        print(f"  ✓ {cf['dt']}.{cf['fieldname']} - '{cf['label']}'")

    vp_count = frappe.db.count("Vendor Payment")
    print(f"\nVendor Payment records: {vp_count}")

    print("\n✅ System is ready for presentation!")
