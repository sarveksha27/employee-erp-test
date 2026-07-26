"""
Creates individual custom field JSON files in the proper Frappe module structure.
These are applied automatically on bench migrate — no fixture manipulation needed.
Run: python3 create_custom_field_files.py
"""
import json, os

BASE_SUPPLIER = "sarveksha_erp/vendor_management/custom_field"
BASE_COMPANY  = "sarveksha_erp/vendor_management/custom_field"

FIELDS = [
    # ── SUPPLIER fields ──────────────────────────────────────────────────────
    ("Supplier", "custom_vendor_details_section", "Section Break",
     "Sarveksha Vendor Details", "supplier_type", None, 0, None, None, 0, 0, 1),
    ("Supplier", "custom_vendor_code",  "Data",   "Vendor Code",  "custom_vendor_details_section", None, 0, None, "Unique vendor code", 0, 1, 0),
    ("Supplier", "custom_vendor_type",  "Select", "Vendor Type",  "custom_vendor_code",
     "\nManufacturer\nTrader\nService Provider\nLogistics", 0, None, None, 1, 1, 0),
    ("Supplier", "custom_pan",          "Data",   "PAN Number",   "custom_vendor_type",   None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_tin",          "Data",   "TIN Number",   "custom_pan",           None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_website",      "Data",   "Website",      "custom_tin",           None, 0, None, None, 0, 0, 0),

    ("Supplier", "custom_bank_details_section", "Section Break",
     "Bank Details", "custom_website", None, 0, None, None, 0, 0, 1),
    ("Supplier", "custom_bank_name",       "Data", "Bank Name",       "custom_bank_details_section", None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_bank_branch",     "Data", "Bank Branch",     "custom_bank_name",   None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_account_number",  "Data", "Account Number",  "custom_bank_branch", None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_ifsc",            "Data", "IFSC Code",       "custom_account_number", None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_swift_code",      "Data", "SWIFT Code",      "custom_ifsc",        None, 0, None, "For international wire transfers", 0, 0, 0),
    ("Supplier", "custom_iban",            "Data", "IBAN",            "custom_swift_code",  None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_bank_currency",   "Link", "Bank Currency",   "custom_iban",        "Currency", 0, None, None, 0, 0, 0),

    ("Supplier", "custom_tax_section", "Section Break", "Tax & GST", "custom_bank_currency", None, 0, None, None, 0, 0, 1),
    ("Supplier", "custom_gst_applicable",  "Check",   "GST Applicable",  "custom_tax_section",       None, 0, "0",  None, 0, 0, 0),
    ("Supplier", "custom_gst_percentage",  "Percent", "GST Percentage",  "custom_gst_applicable",    None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_tds_applicable",  "Check",   "TDS Applicable",  "custom_gst_percentage",    None, 0, "0",  None, 0, 0, 0),
    ("Supplier", "custom_tds_percentage",  "Percent", "TDS Percentage",  "custom_tds_applicable",    None, 0, None, None, 0, 0, 0),

    ("Supplier", "custom_operational_section", "Section Break", "Operational Details", "custom_tds_percentage", None, 0, None, None, 0, 0, 1),
    ("Supplier", "custom_vendor_rating",    "Rating",     "Vendor Rating",   "custom_operational_section", None, 0, None, "1=Poor, 5=Excellent", 0, 0, 0),
    ("Supplier", "custom_preferred_vendor", "Check",      "Preferred Vendor","custom_vendor_rating",       None, 0, "0", None, 0, 1, 0),
    ("Supplier", "custom_lead_time_days",   "Int",        "Lead Time (Days)","custom_preferred_vendor",    None, 0, None, "Avg days PO to delivery", 0, 0, 0),
    ("Supplier", "custom_approved",         "Check",      "Approved Vendor", "custom_lead_time_days",      None, 0, "0", "Tick when formally approved", 1, 1, 0),
    ("Supplier", "custom_vendor_remarks",   "Small Text", "Vendor Remarks",  "custom_approved",            None, 0, None, None, 0, 0, 0),
    ("Supplier", "custom_vendor_documents", "Attach",     "Vendor Documents","custom_vendor_remarks",      None, 0, None, "Upload certificates, agreements", 0, 0, 0),

    # ── COMPANY fields ───────────────────────────────────────────────────────
    ("Company", "custom_registration_section", "Section Break",
     "Registration & Compliance", "website", None, 0, None, None, 0, 0, 1),
    ("Company", "custom_registration_no",       "Data", "Company Registration No.", "custom_registration_section", None, 0, None, None, 0, 0, 0),
    ("Company", "custom_pan",                   "Data", "PAN",                     "custom_registration_no",      None, 0, None, None, 0, 0, 0),
    ("Company", "custom_tan",                   "Data", "TAN",                     "custom_pan",                  None, 0, None, None, 0, 0, 0),
    ("Company", "custom_tin",                   "Data", "TIN",                     "custom_tan",                  None, 0, None, None, 0, 0, 0),
    ("Company", "custom_vat_number",            "Data", "VAT Number",              "custom_tin",                  None, 0, None, None, 0, 0, 0),
    ("Company", "custom_import_export_code",    "Data", "IEC (Import Export Code)","custom_vat_number",
     None, 0, None, "IEC for SRI = AFTFS2557J", 0, 0, 0),

    ("Company", "custom_export_section", "Section Break",
     "Export & Logistics", "custom_import_export_code", None, 0, None, None, 0, 0, 1),
    ("Company", "custom_default_port", "Data", "Default Port", "custom_export_section",
     None, 0, None, "e.g. Mundra, Conakry, Freetown, Douala", 0, 0, 0),
    ("Company", "custom_default_cfa",  "Data", "Default CFA (Clearing & Forwarding Agent)",
     "custom_default_port", None, 0, None, None, 0, 0, 0),

    ("Company", "custom_branding_section", "Section Break",
     "Branding & Signatory", "custom_default_cfa", None, 0, None, None, 0, 0, 1),
    ("Company", "custom_company_seal",         "Attach Image", "Company Seal",
     "custom_branding_section", None, 0, None, "Upload company seal/stamp", 0, 0, 0),
    ("Company", "custom_authorized_signatory", "Data", "Authorized Signatory",
     "custom_company_seal", None, 0, None, "Person authorized to sign POs", 0, 0, 0),
]

created = 0
skipped = 0
for (dt, fieldname, fieldtype, label, insert_after,
     options, reqd, default, description,
     in_list_view, in_standard_filter, bold) in FIELDS:

    name = f"{dt}-{fieldname}"
    dirpath = os.path.join(BASE_SUPPLIER, fieldname)
    filepath = os.path.join(dirpath, f"{fieldname}.json")

    if os.path.exists(filepath):
        print(f"SKIP (exists): {name}")
        skipped += 1
        continue

    os.makedirs(dirpath, exist_ok=True)
    # create __init__.py
    init_path = os.path.join(dirpath, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "w").close()

    data = {
        "alignment": "",
        "allow_in_quick_entry": 0,
        "allow_on_submit": 0,
        "bold": bold,
        "button_color": "",
        "collapsible": 0,
        "columns": 0,
        "creation": "2026-07-25 10:00:00.000000",
        "default": default,
        "depends_on": None,
        "description": description,
        "docstatus": 0,
        "doctype": "Custom Field",
        "dt": dt,
        "fetch_if_empty": 0,
        "fieldname": fieldname,
        "fieldtype": fieldtype,
        "hidden": 0,
        "hide_border": 0,
        "hide_days": 0,
        "hide_seconds": 0,
        "ignore_user_permissions": 0,
        "ignore_xss_filter": 0,
        "in_global_search": 0,
        "in_list_view": in_list_view,
        "in_preview": 0,
        "in_standard_filter": in_standard_filter,
        "insert_after": insert_after,
        "is_system_generated": 0,
        "is_virtual": 0,
        "label": label,
        "length": 0,
        "mask": 0,
        "modified": "2026-07-25 10:00:00.000000",
        "modified_by": "Administrator",
        "module": "Vendor Management",
        "name": name,
        "no_copy": 0,
        "non_negative": 0,
        "options": options,
        "owner": "Administrator",
        "permlevel": 0,
        "precision": "",
        "print_hide": 0,
        "print_hide_if_no_value": 0,
        "read_only": 0,
        "report_hide": 0,
        "reqd": reqd,
        "search_index": 0,
        "set_only_once": 0,
        "show_dashboard": 0,
        "sort_options": 0,
        "translatable": 0,
        "unique": 0,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"CREATED: {name}")
    created += 1

print(f"\nDone. Created={created}, Skipped={skipped}")
