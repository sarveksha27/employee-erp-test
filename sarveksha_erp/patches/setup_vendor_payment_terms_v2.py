"""Seed the standard procurement payment terms and reusable templates."""

import frappe

DAY_AFTER_INVOICE = "Day(s) after invoice date"

STANDARD_TERMS = (
    {
        "payment_term_name": "100% Advance",
        "invoice_portion": 100,
        "credit_days": 0,
        "description": "100% Advance payment required upon order confirmation.",
    },
    {
        "payment_term_name": "30% Advance",
        "invoice_portion": 30,
        "credit_days": 0,
        "description": "30% Advance payment required upon order confirmation.",
    },
    {
        "payment_term_name": "70% Against BL",
        "invoice_portion": 70,
        "credit_days": 0,
        "description": "70% Balance payment against Bill of Lading (BL) copy.",
    },
    {
        "payment_term_name": "Net 30 Days",
        "invoice_portion": 100,
        "credit_days": 30,
        "description": "Full payment due within 30 days of invoice date.",
    },
    {
        "payment_term_name": "Net 45 Days",
        "invoice_portion": 100,
        "credit_days": 45,
        "description": "Full payment due within 45 days of invoice date.",
    },
    {
        "payment_term_name": "Net 60 Days",
        "invoice_portion": 100,
        "credit_days": 60,
        "description": "Full payment due within 60 days of invoice date.",
    },
)

STANDARD_TEMPLATES = (
    {
        "template_name": "Standard Vendor Terms - 30/70",
        "terms": (("30% Advance", 30, 0), ("70% Against BL", 70, 0)),
    },
    {
        "template_name": "100% Advance",
        "terms": (("100% Advance", 100, 0),),
    },
    {
        "template_name": "30% Advance - 70% Against BL",
        "terms": (("30% Advance", 30, 0), ("70% Against BL", 70, 0)),
    },
    {
        "template_name": "Net 30 Days",
        "terms": (("Net 30 Days", 100, 30),),
    },
    {
        "template_name": "Net 45 Days",
        "terms": (("Net 45 Days", 100, 45),),
    },
    {
        "template_name": "Net 60 Days",
        "terms": (("Net 60 Days", 100, 60),),
    },
)


def execute():
    """Create missing standard terms/templates without duplicating or overwriting records."""
    for term_data in STANDARD_TERMS:
        name = term_data["payment_term_name"]
        if frappe.db.exists("Payment Term", name):
            continue

        term = frappe.new_doc("Payment Term")
        term.update(
            {
                **term_data,
                "doctype": "Payment Term",
                "due_date_based_on": DAY_AFTER_INVOICE,
            }
        )
        term.flags.ignore_permissions = True
        term.insert()

    for template_data in STANDARD_TEMPLATES:
        name = template_data["template_name"]
        if frappe.db.exists("Payment Terms Template", name):
            continue

        template = frappe.new_doc("Payment Terms Template")
        template.template_name = name
        template.allocate_payment_based_on_payment_terms = 1
        for payment_term, portion, credit_days in template_data["terms"]:
            template.append(
                "terms",
                {
                    "payment_term": payment_term,
                    "invoice_portion": portion,
                    "due_date_based_on": DAY_AFTER_INVOICE,
                    "credit_days": credit_days,
                },
            )
        template.flags.ignore_permissions = True
        template.insert()
