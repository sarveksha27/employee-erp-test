# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe


def execute():
    """Create standard Payment Terms, Templates and Terms & Conditions for procurement contracts."""
    setup_standard_payment_terms()
    setup_standard_payment_terms_templates()
    setup_standard_terms_and_conditions()


def setup_standard_payment_terms():
    terms = [
        {
            "doctype": "Payment Term",
            "payment_term_name": "100% Advance",
            "invoice_portion": 100.0,
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 0,
            "description": "100% Advance payment required upon order confirmation.",
        },
        {
            "doctype": "Payment Term",
            "payment_term_name": "30% Advance",
            "invoice_portion": 30.0,
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 0,
            "description": "30% Advance payment required upon order confirmation.",
        },
        {
            "doctype": "Payment Term",
            "payment_term_name": "70% Against BL",
            "invoice_portion": 70.0,
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 0,
            "description": "70% Balance payment against Bill of Lading (BL) copy.",
        },
        {
            "doctype": "Payment Term",
            "payment_term_name": "Net 30 Days",
            "invoice_portion": 100.0,
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 30,
            "description": "Full payment due within 30 days of invoice date.",
        },
    ]

    for t in terms:
        name = t["payment_term_name"]
        if not frappe.db.exists("Payment Term", name):
            doc = frappe.new_doc("Payment Term")
            doc.update(t)
            doc.flags.ignore_permissions = True
            doc.insert()
        else:
            doc = frappe.get_doc("Payment Term", name)
            doc.update(t)
            doc.flags.ignore_permissions = True
            doc.save()

    frappe.db.commit()


def setup_standard_payment_terms_templates():
    templates = [
        {
            "template_name": "100% Advance",
            "terms": [
                {
                    "payment_term": "100% Advance",
                    "invoice_portion": 100.0,
                    "due_date_based_on": "Day(s) after invoice date",
                    "credit_days": 0,
                    "description": "100% Advance payment required upon order confirmation.",
                }
            ],
        },
        {
            "template_name": "30% Advance - 70% Against BL",
            "terms": [
                {
                    "payment_term": "30% Advance",
                    "invoice_portion": 30.0,
                    "due_date_based_on": "Day(s) after invoice date",
                    "credit_days": 0,
                    "description": "30% Advance payment required upon order confirmation.",
                },
                {
                    "payment_term": "70% Against BL",
                    "invoice_portion": 70.0,
                    "due_date_based_on": "Day(s) after invoice date",
                    "credit_days": 0,
                    "description": "70% Balance payment against Bill of Lading (BL) copy.",
                },
            ],
        },
        {
            "template_name": "Net 30 Days",
            "terms": [
                {
                    "payment_term": "Net 30 Days",
                    "invoice_portion": 100.0,
                    "due_date_based_on": "Day(s) after invoice date",
                    "credit_days": 30,
                    "description": "Full payment due within 30 days of invoice date.",
                }
            ],
        },
    ]

    for tmpl in templates:
        name = tmpl["template_name"]
        if not frappe.db.exists("Payment Terms Template", name):
            doc = frappe.new_doc("Payment Terms Template")
            doc.template_name = name
            doc.allocate_payment_based_on_payment_terms = 1
            for row in tmpl["terms"]:
                doc.append("terms", row)
            doc.flags.ignore_permissions = True
            doc.insert()
        else:
            doc = frappe.get_doc("Payment Terms Template", name)
            doc.allocate_payment_based_on_payment_terms = 1
            doc.set("terms", [])
            for row in tmpl["terms"]:
                doc.append("terms", row)
            doc.flags.ignore_permissions = True
            doc.save()

    frappe.db.commit()


def setup_standard_terms_and_conditions():
    """Create standard procurement Terms and Conditions."""
    terms_data = [
        {
            "title": "Standard Export PO Terms",
            "terms": """<ol>
<li><strong>Payment Terms:</strong> Payment shall be made as per agreed milestones mentioned in the Purchase Order against submission of commercial invoice, packing list, and bill of lading.</li>
<li><strong>Inspection & Quality:</strong> Material subject to pre-shipment inspection by Authorized Inspector / Third Party (SGS / Intertek / Bureau Veritas). Seller must provide inspection test certificates prior to dispatch.</li>
<li><strong>Liquidated Damages (LD):</strong> In case of delayed delivery beyond the agreed schedule, Liquidated Damages shall be levied @ 0.5% of total PO value per week of delay, subject to a maximum cap of 10%.</li>
<li><strong>Warranty:</strong> Equipment carries a comprehensive warranty of 12 months from commissioning or 18 months from shipment date, whichever is earlier. Defective parts shall be replaced free of cost.</li>
<li><strong>Packaging & ISPM-15 Compliance:</strong> All wooden packaging, pallets, and crates must be heat treated and stamped in full compliance with ISPM-15 international phytosanitary standards.</li>
<li><strong>Force Majeure:</strong> Neither party shall be liable for failure to perform obligations due to acts of God, war, civil commotion, pandemic restrictions, or severe maritime shipping blockades.</li>
<li><strong>Governing Law & Jurisdiction:</strong> This contract shall be governed by Indian Laws, and any disputes shall be subject to the exclusive jurisdiction of courts in Mumbai, Maharashtra, India.</li>
</ol>""",
        },
        {
            "title": "Standard Domestic PO Terms",
            "terms": """<ol>
<li><strong>Prices:</strong> The prices are Nett & Ex-Godown / Ex-Works unless otherwise specified.</li>
<li><strong>Discount:</strong> As mentioned in this Purchase Order.</li>
<li><strong>Packing Charges:</strong> As per actuals. Supplier must pack goods in a manner compliant with transit safety.</li>
<li><strong>Inspection:</strong> Pre-dispatch inspection at supplier premises if requested.</li>
<li><strong>Warranty:</strong> Standard manufacturer warranty applies from date of delivery and commissioning.</li>
<li><strong>Delivery Schedule:</strong> Goods must be dispatched on or before the committed delivery date.</li>
<li><strong>Jurisdiction:</strong> Subject to registered office jurisdiction in Mumbai, Maharashtra, India.</li>
</ol>""",
        },
        {
            "title": "LUT Certificate Terms",
            "terms": "<p>Supply made under Letter of Undertaking (LUT) without payment of IGST under Rule 96A of CGST Rules, 2017.</p>",
        },
    ]

    for t in terms_data:
        name = t["title"]
        if not frappe.db.exists("Terms and Conditions", name):
            doc = frappe.new_doc("Terms and Conditions")
            doc.title = name
            doc.terms = t["terms"]
            doc.flags.ignore_permissions = True
            doc.insert()
        else:
            doc = frappe.get_doc("Terms and Conditions", name)
            doc.terms = t["terms"]
            doc.flags.ignore_permissions = True
            doc.save()

    frappe.db.commit()
