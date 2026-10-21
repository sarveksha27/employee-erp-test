import frappe


VALID_COMPANIES = {
    "Sarveksha Realty and Inframine LLP",
    "Sarveksha BSTP SAS",
    "Sarveksha Mining SARL",
    "Sarveksha Cameroon PLC",
    "Sarveksha Botswana Proprietary Limited",
    "Sarveksha SL Limited",
    "Baani Minerals",
    "Globe Multitrade and Service LLC",
    "Odhav Holdings",
}

VALID_USERS = {
    "Administrator",
    "Guest",
    "admin@sarveksha.com",
    "umeshraj14pj@gmail.com",
    "finance_clerk1@sarveksha.com",
    "finance_clerk2@sarveksha.com",
    "finance_manager1@sarveksha.com",
    "finance_manager2@sarveksha.com",
    "po_generator@sarveksha.com",
    "po_verifier@sarveksha.com",
    "po_approver@sarveksha.com",
    "vendor_manager@sarveksha.com",
    "master_manager@sarveksha.com",
}


def cleanup_test_documents():
    """Purge synthetic test documents, dummy stock entries, and orphan test transactions."""
    # 1. Payment Entry
    for pe in frappe.get_all("Payment Entry", fields=["name"]):
        if "test" in pe.name.lower() or pe.name == "ACC-PAY-2026-00001":
            frappe.db.delete("Payment Entry Reference", {"parent": pe.name})
            frappe.db.delete("Payment Entry", {"name": pe.name})

    # Clean orphaned test payment proof files from disk and database
    import glob, os
    proof_pattern = frappe.get_site_path("public", "files", "Payment_Proof_*.pdf")
    for f in glob.glob(proof_pattern):
        try:
            os.remove(f)
        except Exception:
            pass
    frappe.db.delete("File", {"file_name": ["like", "Payment_Proof_%"]})

    # 2. Test transactional records across stock and maintenance
    for dt in [
        "Stock Ledger Entry",
        "Stock Entry",
        "Bin",
        "BOM",
        "Project",
        "Employee",
        "Shareholder",
        "Loyalty Program",
        "Dunning Type",
        "Asset Maintenance Team",
    ]:
        if frappe.db.table_exists(dt):
            records = frappe.get_all(
                dt,
                fields=["name"]
                + (["company"] if frappe.get_meta(dt).has_field("company") else []),
            )
            for r in records:
                comp = r.get("company")
                if (
                    (comp and comp not in VALID_COMPANIES)
                    or r.name.startswith("_Test")
                    or r.name.startswith("Test ")
                ):
                    frappe.db.delete(dt, {"name": r.name})


def cleanup_test_masters():
    """Purge test items, customers, suppliers, payment terms, and templates."""
    # 1. Items
    if frappe.db.table_exists("Item"):
        test_items = frappe.get_all("Item", filters={"name": ["like", "%Test%"]})
        for item in test_items:
            frappe.db.delete("Item Price", {"item_code": item.name})
            if frappe.db.table_exists("Item Tax"):
                frappe.db.delete("Item Tax", {"parent": item.name})
            if frappe.db.table_exists("Item Default"):
                frappe.db.delete("Item Default", {"parent": item.name})
            frappe.db.delete("Bin", {"item_code": item.name})
            frappe.db.delete("Item", {"name": item.name})

    # 2. Customers
    if frappe.db.table_exists("Customer"):
        test_cust = [
            c.name
            for c in frappe.get_all("Customer")
            if c.name.startswith("_Test") or c.name.startswith("Test ")
        ]
        for c in test_cust:
            frappe.db.delete("Dynamic Link", {"link_doctype": "Customer", "link_name": c})
            frappe.db.delete("Customer", {"name": c})

    # 3. Suppliers
    if frappe.db.table_exists("Supplier"):
        test_supp = [
            s.name
            for s in frappe.get_all("Supplier")
            if s.name.startswith("_Test") or s.name.startswith("Test ")
        ]
        for s in test_supp:
            frappe.db.delete("Dynamic Link", {"link_doctype": "Supplier", "link_name": s})
            frappe.db.delete("Supplier", {"name": s})

    # 4. Payment Terms & Templates
    if frappe.db.table_exists("Payment Terms Template"):
        test_templates = [
            t.name
            for t in frappe.get_all("Payment Terms Template")
            if t.name.startswith("_Test")
        ]
        for pt in test_templates:
            frappe.db.delete("Payment Terms Template Detail", {"parent": pt})
            frappe.db.delete("Payment Terms Template", {"name": pt})

    if frappe.db.table_exists("Payment Term"):
        test_terms = [
            t.name for t in frappe.get_all("Payment Term") if t.name.startswith("_Test")
        ]
        for pt in test_terms:
            frappe.db.delete("Payment Term", {"name": pt})


def cleanup_test_users():
    """Purge test users and dummy contacts/addresses."""
    if frappe.db.table_exists("User"):
        all_users = [u.name for u in frappe.get_all("User")]
        users_to_delete = [u for u in all_users if u not in VALID_USERS]
        for u in users_to_delete:
            frappe.db.delete("Has Role", {"parent": u})
            frappe.db.delete("User Permission", {"user": u})
            frappe.db.delete("Contact", {"email_id": u})
            frappe.db.delete("User", {"name": u})

    if frappe.db.table_exists("Contact"):
        test_contacts = [
            c.name
            for c in frappe.get_all("Contact")
            if c.name.startswith("_Test") or c.name.startswith("Test ")
        ]
        for c in test_contacts:
            frappe.db.delete("Dynamic Link", {"parent": c})
            frappe.db.delete("Contact", {"name": c})

    if frappe.db.table_exists("Address"):
        test_addrs = [
            a.name
            for a in frappe.get_all("Address")
            if a.name.startswith("_Test") or a.name.startswith("Test ")
        ]
        for a in test_addrs:
            frappe.db.delete("Dynamic Link", {"parent": a})
            frappe.db.delete("Address", {"name": a})


def cleanup_test_companies():
    """Purge all dummy companies created by standard ERPNext test suites."""
    if not frappe.db.table_exists("Company"):
        return

    all_companies = [c.name for c in frappe.get_all("Company")]
    companies_to_delete = [c for c in all_companies if c not in VALID_COMPANIES]

    company_tables = [
        "Mode of Payment Account",
        "Sales Taxes and Charges Template",
        "Purchase Taxes and Charges Template",
        "Item Tax Template",
        "Process Deferred Accounting",
        "Account",
        "Cost Center",
        "Warehouse",
        "Department",
        "Tax Withholding Account",
        "Bank Account",
        "Party Account",
    ]

    for tc in companies_to_delete:
        for dt in company_tables:
            if frappe.db.table_exists(dt) and frappe.get_meta(dt).has_field("company"):
                frappe.db.delete(dt, {"company": tc})
        frappe.db.delete("Company", {"name": tc})


def sync_sarveksha_companies_registration():
    """Ensure all official Sarveksha companies have their accurate registration details."""
    company_configs = {
        "Sarveksha Realty and Inframine LLP": {
            "abbr": "SRI",
            "country": "India",
            "default_currency": "INR",
            "tax_id": "27AFTFS2557J1Z8",
            "custom_registration_no": "LLPIN-ACS-0698",
            "registration_details": "Infrastructure; Building and Public Works; Mining and Terch Services. | Reg. No. LLPIN-ACS-0698 | GSTIN - 27AFTFS2557J1Z8",
            "default_letter_head": "India (Sarveksha Realty)",
        },
        "Sarveksha BSTP SAS": {
            "abbr": "SBSTP",
            "country": "Guinea",
            "default_currency": "USD",
            "tax_id": "684060320",
            "custom_registration_no": "RCCM / GN / TCC .2024. B. 02459",
            "registration_details": "BATIMENT ET TRAVAUX PUBLICS; COMMERCE GENERAL (IMPORT-EXPORT); REPRESENTATION COMMERCIALE; AGRO-BUSINESS; PECHE; CONSULTATION; TRANSPORT LOGISTIQUE; PRESTATIONS DE SERVICES; DIVERS. | RCCM / GN / TCC .2024. B. 02459 | Code Neif: 684060320 Dt. 21.02.2024",
            "default_letter_head": "Guinea (Sarveksha BSTP SAS)",
        },
        "Sarveksha Mining SARL": {
            "abbr": "SMSA",
            "country": "Cameroon",
            "default_currency": "USD",
            "custom_registration_no": "CM-NSI-02-2025-B12-00560",
            "registration_details": "BATIMENT ET TRAVAUX PUBLICS; COMMERCE GENERAL (IMPORT-EXPORT); REPRESENTATION COMMERCIALE; AGRO-BUSINESS; PECHE; CONSULTATION; TRANSPORT LOGISTIQUE; PRESTATIONS DE SERVICES; DIVERS. | RCCM: CM-NSI-02-2025-B12-00560",
            "default_letter_head": "Cameroon (Sarveksha Mining SARL)",
        },
        "Sarveksha Cameroon PLC": {
            "abbr": "SCPLC",
            "country": "Cameroon",
            "default_currency": "USD",
            "custom_registration_no": "RC / YAO / 2025 / B / 969",
            "registration_details": "Mining, Mining Services, Construction, Public Works, Trading and Commerce | RCCM: RC / YAO / 2025 / B / 969",
            "default_letter_head": "Cameroon (Sarveksha Cameroon PLC)",
        },
        "Sarveksha Botswana Proprietary Limited": {
            "abbr": "SBPL",
            "country": "Botswana",
            "default_currency": "USD",
            "custom_registration_no": "BW00009608412",
            "registration_details": "Equipment and Public Works; General Trading; Construction & Civil & Erection Work | UIN: BW00009608412",
            "default_letter_head": "Botswana (Sarveksha Botswana)",
        },
        "Sarveksha SL Limited": {
            "abbr": "SSL",
            "country": "Sierra Leone",
            "default_currency": "USD",
            "tax_id": "1001412648",
            "custom_registration_no": "SL120624SARVE22162",
            "registration_details": "Mining, Mineral Processing, Mining Services, Mineral Trading, Public Works; General Trading; Construction & Civil & Erection Work | Reg No : SL120624SARVE22162 | TIN NO : 1001412648",
            "default_letter_head": "Sierra Leone (Sarveksha SL Limited)",
        },
        "Baani Minerals": {
            "abbr": "BM",
            "country": "Cameroon",
            "default_currency": "USD",
            "custom_registration_no": "CM-NSI-02-2025-B12-00784",
            "registration_details": "Mining, Mining Services, Construction, Public Works, Trading and Commerce | RCCM: CM-NSI-02-2025-B12-00784",
            "default_letter_head": "Cameroon (Baani Minerals)",
        },
        "Globe Multitrade and Service LLC": {
            "abbr": "GMSL",
            "country": "United Arab Emirates",
            "default_currency": "AED",
            "registration_details": "Globe Multitrade and Service LLC – Sharjah",
            "default_letter_head": "India (Sarveksha Realty)",
        },
        "Odhav Holdings": {
            "abbr": "OH",
            "country": "Sierra Leone",
            "default_currency": "USD",
            "registration_details": "Odhav Holdings - Sierra Leone. YOE-2025",
            "default_letter_head": "Sierra Leone (Sarveksha SL Limited)",
        },
    }

    for name, config in company_configs.items():
        if not frappe.db.exists("Company", name):
            doc = frappe.new_doc("Company")
            doc.company_name = name
            doc.abbr = config.get("abbr")
            doc.country = config.get("country", "India")
            doc.default_currency = config.get("default_currency", "USD")
            doc.default_letter_head = config.get("default_letter_head")
            doc.registration_details = config.get("registration_details")
            doc.create_chart_of_accounts_based_on = "Standard Template"
            doc.flags.ignore_permissions = True
            doc.insert()
        else:
            for k in [
                "tax_id",
                "custom_registration_no",
                "registration_details",
                "default_letter_head",
            ]:
                if k in config:
                    frappe.db.set_value("Company", name, k, config[k])


def execute():
    """Patch entry point to remove test data and sync official entities."""
    cleanup_test_documents()
    cleanup_test_masters()
    cleanup_test_users()
    cleanup_test_companies()
    from sarveksha_erp.install import setup_letterheads
    setup_letterheads()
    sync_sarveksha_companies_registration()
    frappe.db.commit()
