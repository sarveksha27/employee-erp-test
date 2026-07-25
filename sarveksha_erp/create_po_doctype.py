import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    print("Creating Vendor Purchase Order DocType...")

    if frappe.db.exists("DocType", "Vendor Purchase Order"):
        print("  DocType already exists — deleting to recreate cleanly")
        frappe.delete_doc("DocType", "Vendor Purchase Order", ignore_permissions=True, force=True)
        frappe.db.commit()

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Vendor Purchase Order",
        "module": "Vendor Management",
        "is_submittable": 1,
        "naming_rule": 'By "Naming Series" field',
        "autoname": "naming_series:",
        "title_field": "vendor",
        "search_fields": "vendor,company,status",
        "description": "Purchase Order raised by Sarveksha to a Vendor for equipment procurement",
        "fields": [
            # ----- NAMING & STATUS -----
            {
                "fieldname": "naming_series",
                "fieldtype": "Select",
                "label": "Series",
                "options": "SRI.PO.-.####\nSRI.RPO.-.####",
                "default": "SRI.PO.-.####",
                "reqd": 1,
                "in_list_view": 0,
            },
            {
                "fieldname": "status",
                "fieldtype": "Select",
                "label": "Status",
                "options": "Draft\nSubmitted\nVendor Confirmed\nPartially Paid\nFully Paid\nShipped\nDelivered\nCancelled",
                "default": "Draft",
                "reqd": 1,
                "in_list_view": 1,
                "in_filter": 1,
            },
            {
                "fieldname": "revision",
                "fieldtype": "Int",
                "label": "Revision No.",
                "default": "0",
            },
            {"fieldname": "col_break_header", "fieldtype": "Column Break"},
            {
                "fieldname": "po_date",
                "fieldtype": "Date",
                "label": "PO Date",
                "reqd": 1,
                "default": "Today",
                "in_list_view": 1,
            },
            {
                "fieldname": "company",
                "fieldtype": "Link",
                "label": "Company",
                "options": "Company",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "default_port",
                "fieldtype": "Data",
                "label": "Default Port",
                "read_only": 1,
                "description": "Auto-fetched from Company once Member 1 adds custom_default_port field",
            },
            # ----- SECTION: VENDOR -----
            {"fieldname": "sec_vendor", "fieldtype": "Section Break", "label": "Vendor Details"},
            {
                "fieldname": "vendor",
                "fieldtype": "Link",
                "label": "Vendor",
                "options": "Supplier",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "vendor_gstin",
                "fieldtype": "Data",
                "label": "Vendor GSTIN",
                "read_only": 1,
                "fetch_from": "vendor.tax_id",
            },
            {
                "fieldname": "vendor_pan",
                "fieldtype": "Data",
                "label": "Vendor PAN",
                "read_only": 1,
            },
            {"fieldname": "col_break_vendor", "fieldtype": "Column Break"},
            {
                "fieldname": "vendor_bank_name",
                "fieldtype": "Data",
                "label": "Vendor Bank",
                "read_only": 1,
                "description": "Auto-fetched from Supplier once Member 2 adds custom_bank_name",
            },
            {
                "fieldname": "vendor_account_number",
                "fieldtype": "Data",
                "label": "Vendor Account No.",
                "read_only": 1,
            },
            {
                "fieldname": "vendor_ifsc",
                "fieldtype": "Data",
                "label": "IFSC Code",
                "read_only": 1,
            },
            # ----- SECTION: EQUIPMENT -----
            {"fieldname": "sec_equipment", "fieldtype": "Section Break", "label": "Equipment Details"},
            {
                "fieldname": "equipment",
                "fieldtype": "Data",
                "label": "Equipment",
                "description": "⚠️ TEMP: Will become Link(Equipment) once Member 3 pushes the Equipment DocType",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "equipment_name",
                "fieldtype": "Data",
                "label": "Equipment Name",
            },
            {
                "fieldname": "hsn_code",
                "fieldtype": "Data",
                "label": "HSN Code",
            },
            {
                "fieldname": "brand",
                "fieldtype": "Data",
                "label": "Brand",
            },
            {
                "fieldname": "manufacturer",
                "fieldtype": "Data",
                "label": "Manufacturer",
            },
            {"fieldname": "col_break_equipment", "fieldtype": "Column Break"},
            {
                "fieldname": "quantity",
                "fieldtype": "Float",
                "label": "Quantity",
                "reqd": 1,
                "default": "1",
            },
            {
                "fieldname": "unit",
                "fieldtype": "Link",
                "label": "Unit of Measure",
                "options": "UOM",
            },
            {
                "fieldname": "country_of_origin",
                "fieldtype": "Link",
                "label": "Country of Origin",
                "options": "Country",
            },
            {
                "fieldname": "specification",
                "fieldtype": "Text Editor",
                "label": "Specification / Description",
            },
            # ----- SECTION: PRICING -----
            {"fieldname": "sec_pricing", "fieldtype": "Section Break", "label": "Pricing & Charges"},
            {
                "fieldname": "currency",
                "fieldtype": "Link",
                "label": "Currency",
                "options": "Currency",
                "default": "USD",
                "reqd": 1,
            },
            {
                "fieldname": "exchange_rate",
                "fieldtype": "Float",
                "label": "Exchange Rate",
                "default": "1",
                "description": "Exchange rate to INR base currency",
            },
            {
                "fieldname": "rate",
                "fieldtype": "Currency",
                "label": "Unit Rate",
                "options": "currency",
                "reqd": 1,
            },
            {
                "fieldname": "discount_percent",
                "fieldtype": "Percent",
                "label": "Discount %",
                "default": "0",
            },
            {"fieldname": "col_break_pricing", "fieldtype": "Column Break"},
            {
                "fieldname": "tax_amount",
                "fieldtype": "Currency",
                "label": "Tax / GST Amount",
                "options": "currency",
            },
            {
                "fieldname": "freight",
                "fieldtype": "Currency",
                "label": "Freight Charges",
                "options": "currency",
            },
            {
                "fieldname": "insurance",
                "fieldtype": "Currency",
                "label": "Insurance",
                "options": "currency",
            },
            {
                "fieldname": "packing_charges",
                "fieldtype": "Currency",
                "label": "Packing Charges",
                "options": "currency",
            },
            {
                "fieldname": "other_charges",
                "fieldtype": "Currency",
                "label": "Other Charges",
                "options": "currency",
            },
            {
                "fieldname": "grand_total",
                "fieldtype": "Currency",
                "label": "Grand Total",
                "options": "currency",
                "read_only": 1,
                "bold": 1,
                "in_list_view": 1,
            },
            # ----- SECTION: REFERENCES -----
            {"fieldname": "sec_references", "fieldtype": "Section Break", "label": "References & Logistics"},
            {
                "fieldname": "quotation_ref",
                "fieldtype": "Data",
                "label": "Quotation Reference",
            },
            {
                "fieldname": "quotation_date",
                "fieldtype": "Date",
                "label": "Quotation Date",
            },
            {
                "fieldname": "pi_number",
                "fieldtype": "Data",
                "label": "Proforma Invoice No.",
            },
            {
                "fieldname": "pi_date",
                "fieldtype": "Date",
                "label": "PI Date",
            },
            {"fieldname": "col_break_references", "fieldtype": "Column Break"},
            {
                "fieldname": "expected_delivery",
                "fieldtype": "Date",
                "label": "Expected Delivery Date",
            },
            {
                "fieldname": "delivery_location",
                "fieldtype": "Data",
                "label": "Delivery Location",
            },
            {
                "fieldname": "warehouse",
                "fieldtype": "Link",
                "label": "Destination Warehouse",
                "options": "Warehouse",
            },
            {
                "fieldname": "port",
                "fieldtype": "Data",
                "label": "Port",
                "description": "e.g., Mundra, Conakry, Freetown, Douala",
            },
            {
                "fieldname": "shipment_type",
                "fieldtype": "Select",
                "label": "Shipment Type",
                "options": "\nSea\nAir\nRoad\nCourier",
            },
            {
                "fieldname": "container_number",
                "fieldtype": "Data",
                "label": "Container Number",
            },
            # ----- SECTION: SHIPPING DOCUMENTS -----
            {"fieldname": "sec_shipping_docs", "fieldtype": "Section Break", "label": "Shipping Documents"},
            {
                "fieldname": "invoice_doc",
                "fieldtype": "Attach",
                "label": "Invoice",
            },
            {
                "fieldname": "shipping_bill",
                "fieldtype": "Attach",
                "label": "Shipping Bill",
            },
            {
                "fieldname": "bill_of_lading",
                "fieldtype": "Attach",
                "label": "Bill of Lading (BL)",
            },
            {
                "fieldname": "packing_list",
                "fieldtype": "Attach",
                "label": "Packing List",
            },
            {"fieldname": "col_break_shipping", "fieldtype": "Column Break"},
            {
                "fieldname": "commercial_invoice",
                "fieldtype": "Attach",
                "label": "Commercial Invoice",
            },
            {
                "fieldname": "certificate_of_origin",
                "fieldtype": "Attach",
                "label": "Certificate of Origin (COO)",
            },
            {
                "fieldname": "inspection_report",
                "fieldtype": "Attach",
                "label": "Inspection Report",
            },
            {
                "fieldname": "insurance_doc",
                "fieldtype": "Attach",
                "label": "Insurance Document",
            },
            {
                "fieldname": "cfa_doc",
                "fieldtype": "Attach",
                "label": "CFA / Clearing Agent Doc",
            },
            # ----- SECTION: PAYMENT -----
            {"fieldname": "sec_payment", "fieldtype": "Section Break", "label": "Payment Tracking"},
            {
                "fieldname": "payment_terms",
                "fieldtype": "Small Text",
                "label": "Payment Terms",
                "description": "e.g., 30% advance, 70% before dispatch",
            },
            {
                "fieldname": "advance_percentage",
                "fieldtype": "Percent",
                "label": "Advance %",
                "default": "0",
            },
            {
                "fieldname": "advance_amount",
                "fieldtype": "Currency",
                "label": "Advance Amount",
                "options": "currency",
                "read_only": 1,
            },
            {
                "fieldname": "payment_status",
                "fieldtype": "Select",
                "label": "Payment Status",
                "options": "Pending\nAdvance Paid\nPartially Paid\nFully Paid",
                "default": "Pending",
                "in_list_view": 0,
            },
            {"fieldname": "col_break_payment", "fieldtype": "Column Break"},
            {
                "fieldname": "second_payment",
                "fieldtype": "Currency",
                "label": "Second Payment Amount",
                "options": "currency",
            },
            {
                "fieldname": "final_payment",
                "fieldtype": "Currency",
                "label": "Final Payment Amount",
                "options": "currency",
            },
            {
                "fieldname": "company_bank",
                "fieldtype": "Data",
                "label": "Company Bank (SRI)",
                "description": "Bank account from which SRI pays the vendor",
            },
            # ----- SECTION: APPROVAL -----
            {"fieldname": "sec_approval", "fieldtype": "Section Break", "label": "Approval & Sign-off"},
            {
                "fieldname": "prepared_by",
                "fieldtype": "Link",
                "label": "Prepared By",
                "options": "User",
                "default": "__user",
            },
            {
                "fieldname": "verified_by",
                "fieldtype": "Link",
                "label": "Verified By",
                "options": "User",
            },
            {"fieldname": "col_break_approval", "fieldtype": "Column Break"},
            {
                "fieldname": "approved_by",
                "fieldtype": "Link",
                "label": "Approved By",
                "options": "User",
            },
            {
                "fieldname": "signatory",
                "fieldtype": "Data",
                "label": "Authorized Signatory",
            },
            # ----- SECTION: REMARKS -----
            {"fieldname": "sec_remarks", "fieldtype": "Section Break", "label": "Remarks & Attachments"},
            {
                "fieldname": "remarks",
                "fieldtype": "Small Text",
                "label": "Remarks",
            },
            {
                "fieldname": "attachments",
                "fieldtype": "Attach",
                "label": "Additional Attachments",
            },
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1, "write": 1, "create": 1, "delete": 1,
                "submit": 1, "cancel": 1, "amend": 1, "print": 1,
            },
            {
                "role": "Purchase Manager",
                "read": 1, "write": 1, "create": 1, "delete": 0,
                "submit": 1, "cancel": 0, "amend": 0, "print": 1,
            },
            {
                "role": "Purchase User",
                "read": 1, "write": 1, "create": 1, "delete": 0,
                "submit": 0, "cancel": 0, "amend": 0, "print": 1,
            },
        ],
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"  ✅ DocType 'Vendor Purchase Order' created successfully!")
    print(f"  Fields: {len([f for f in doc.fields if f.fieldtype not in ['Section Break', 'Column Break']])} data fields")
