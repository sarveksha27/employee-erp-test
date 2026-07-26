"""
Script to append missing Supplier and Company custom fields to custom_field.json
Run: python3 append_custom_fields.py
"""
import json

FIXTURE_PATH = "sarveksha_erp/fixtures/custom_field.json"

def make_field(dt, fieldname, fieldtype, label, insert_after,
               options=None, reqd=0, depends_on=None, description=None,
               in_list_view=0, in_standard_filter=0, in_global_search=0,
               bold=0, default=None, search_index=0):
    return {
        "alignment": "",
        "allow_in_quick_entry": 0,
        "allow_on_submit": 0,
        "bold": bold,
        "button_color": "",
        "collapsible": 0,
        "collapsible_depends_on": None,
        "columns": 0,
        "default": default,
        "depends_on": depends_on,
        "description": description,
        "docstatus": 0,
        "doctype": "Custom Field",
        "dt": dt,
        "fetch_from": None,
        "fetch_if_empty": 0,
        "fieldname": fieldname,
        "fieldtype": fieldtype,
        "hidden": 0,
        "hide_border": 0,
        "hide_days": 0,
        "hide_seconds": 0,
        "ignore_user_permissions": 0,
        "ignore_xss_filter": 0,
        "in_global_search": in_global_search,
        "in_list_view": in_list_view,
        "in_preview": 0,
        "in_standard_filter": in_standard_filter,
        "insert_after": insert_after,
        "is_system_generated": 0,
        "is_virtual": 0,
        "label": label,
        "length": 0,
        "link_filters": None,
        "mandatory_depends_on": None,
        "mask": 0,
        "modified": "2026-07-25 10:00:00.000000",
        "module": "Vendor Management",
        "name": f"{dt}-{fieldname}",
        "no_copy": 0,
        "non_negative": 0,
        "options": options,
        "permlevel": 0,
        "placeholder": None,
        "precision": "",
        "print_hide": 0,
        "print_hide_if_no_value": 0,
        "print_width": None,
        "read_only": 0,
        "read_only_depends_on": None,
        "report_hide": 0,
        "reqd": reqd,
        "search_index": search_index,
        "set_only_once": 0,
        "show_dashboard": 0,
        "sort_options": 0,
        "translatable": 0,
        "unique": 0,
        "width": None,
    }

NEW_FIELDS = [
    # ── SUPPLIER fields (Member 2) ─────────────────────────────────────────
    make_field("Supplier", "custom_vendor_details_section", "Section Break",
               "Sarveksha Vendor Details", "supplier_type", bold=1),

    make_field("Supplier", "custom_vendor_code", "Data",
               "Vendor Code", "custom_vendor_details_section",
               in_global_search=1, in_standard_filter=1, search_index=1,
               description="Unique vendor code for internal tracking"),

    make_field("Supplier", "custom_vendor_type", "Select",
               "Vendor Type", "custom_vendor_code",
               options="\nManufacturer\nTrader\nService Provider\nLogistics",
               in_list_view=1, in_standard_filter=1),

    make_field("Supplier", "custom_pan", "Data",
               "PAN Number", "custom_vendor_type"),

    make_field("Supplier", "custom_tin", "Data",
               "TIN Number", "custom_pan"),

    make_field("Supplier", "custom_website", "Data",
               "Website", "custom_tin"),

    # Bank Details section
    make_field("Supplier", "custom_bank_details_section", "Section Break",
               "Bank Details", "custom_website", bold=1),

    make_field("Supplier", "custom_bank_name", "Data",
               "Bank Name", "custom_bank_details_section"),

    make_field("Supplier", "custom_bank_branch", "Data",
               "Bank Branch", "custom_bank_name"),

    make_field("Supplier", "custom_account_number", "Data",
               "Account Number", "custom_bank_branch"),

    make_field("Supplier", "custom_ifsc", "Data",
               "IFSC Code", "custom_account_number"),

    make_field("Supplier", "custom_swift_code", "Data",
               "SWIFT Code", "custom_ifsc",
               description="For international wire transfers"),

    make_field("Supplier", "custom_iban", "Data",
               "IBAN", "custom_swift_code"),

    make_field("Supplier", "custom_bank_currency", "Link",
               "Bank Currency", "custom_iban", options="Currency"),

    # Tax & GST section
    make_field("Supplier", "custom_tax_section", "Section Break",
               "Tax & GST", "custom_bank_currency", bold=1),

    make_field("Supplier", "custom_gst_applicable", "Check",
               "GST Applicable", "custom_tax_section", default="0"),

    make_field("Supplier", "custom_gst_percentage", "Percent",
               "GST Percentage", "custom_gst_applicable",
               depends_on="eval:doc.custom_gst_applicable"),

    make_field("Supplier", "custom_tds_applicable", "Check",
               "TDS Applicable", "custom_gst_percentage", default="0"),

    make_field("Supplier", "custom_tds_percentage", "Percent",
               "TDS Percentage", "custom_tds_applicable",
               depends_on="eval:doc.custom_tds_applicable"),

    # Operational section
    make_field("Supplier", "custom_operational_section", "Section Break",
               "Operational Details", "custom_tds_percentage", bold=1),

    make_field("Supplier", "custom_vendor_rating", "Rating",
               "Vendor Rating", "custom_operational_section",
               description="1 = Poor, 5 = Excellent"),

    make_field("Supplier", "custom_preferred_vendor", "Check",
               "Preferred Vendor", "custom_vendor_rating",
               default="0", in_standard_filter=1),

    make_field("Supplier", "custom_lead_time_days", "Int",
               "Lead Time (Days)", "custom_preferred_vendor",
               description="Average number of days from PO to delivery"),

    make_field("Supplier", "custom_approved", "Check",
               "Approved Vendor", "custom_lead_time_days",
               default="0", in_list_view=1, in_standard_filter=1,
               description="Tick when vendor is formally approved by management"),

    make_field("Supplier", "custom_vendor_remarks", "Small Text",
               "Vendor Remarks", "custom_approved"),

    make_field("Supplier", "custom_vendor_documents", "Attach",
               "Vendor Documents", "custom_vendor_remarks",
               description="Upload vendor certificates, agreements, etc."),

    # ── COMPANY fields (Member 1) ──────────────────────────────────────────
    make_field("Company", "custom_registration_section", "Section Break",
               "Registration & Compliance", "website", bold=1),

    make_field("Company", "custom_registration_no", "Data",
               "Company Registration No.", "custom_registration_section"),

    make_field("Company", "custom_pan", "Data",
               "PAN", "custom_registration_no"),

    make_field("Company", "custom_tan", "Data",
               "TAN", "custom_pan"),

    make_field("Company", "custom_tin", "Data",
               "TIN", "custom_tan"),

    make_field("Company", "custom_vat_number", "Data",
               "VAT Number", "custom_tin"),

    make_field("Company", "custom_import_export_code", "Data",
               "IEC (Import Export Code)", "custom_vat_number",
               description="Import Export Code — for SRI: AFTFS2557J"),

    # Export & Logistics section
    make_field("Company", "custom_export_section", "Section Break",
               "Export & Logistics", "custom_import_export_code", bold=1),

    make_field("Company", "custom_default_port", "Data",
               "Default Port", "custom_export_section",
               description="Default port of dispatch/arrival (e.g. Mundra, Conakry, Freetown)"),

    make_field("Company", "custom_default_cfa", "Data",
               "Default CFA (Clearing & Forwarding Agent)", "custom_default_port"),

    # Branding & Signatory section
    make_field("Company", "custom_branding_section", "Section Break",
               "Branding & Signatory", "custom_default_cfa", bold=1),

    make_field("Company", "custom_company_seal", "Attach Image",
               "Company Seal", "custom_branding_section",
               description="Upload the company seal/stamp image"),

    make_field("Company", "custom_authorized_signatory", "Data",
               "Authorized Signatory", "custom_company_seal",
               description="Name of the person authorized to sign POs and documents"),
]

# Load existing fixture
with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Check which fields already exist (avoid duplicates)
existing_names = {entry.get("name") for entry in data}
to_add = [f for f in NEW_FIELDS if f["name"] not in existing_names]

print(f"Existing fields: {len(data)}")
print(f"Fields to add: {len(to_add)}")
for f in to_add:
    print(f"  + {f['name']}")

data.extend(to_add)

# Write back
with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
    f.write("\n")

print(f"\nDone. Total fields now: {len(data)}")
print("Saved to", FIXTURE_PATH)
