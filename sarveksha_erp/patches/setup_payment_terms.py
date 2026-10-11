# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe


def execute():
    """Create standard Payment Terms and Templates for procurement contracts."""
    setup_standard_payment_terms()
    setup_standard_payment_terms_templates()


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
