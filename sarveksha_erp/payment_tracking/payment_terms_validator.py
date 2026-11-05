"""Validation for reusable Payment Terms Templates."""

from decimal import Decimal, InvalidOperation

import frappe
from frappe import _

PORTION_TOLERANCE = Decimal("0.001")
REQUIRED_PORTION_TOTAL = Decimal("100")


def _value(row, fieldname):
    if hasattr(row, "get"):
        return row.get(fieldname)
    return getattr(row, fieldname, None)


def _decimal(value):
    try:
        return Decimal(str(value if value is not None else 0))
    except (InvalidOperation, TypeError, ValueError):
        return None


def validate_payment_terms_template(doc, method=None):
    """Require positive milestones, nonnegative credit days, and a 100% allocation."""
    terms = _value(doc, "terms") or []
    template_name = _value(doc, "template_name") or _("Payment Terms Template")

    if not terms:
        frappe.throw(
            _("{0} must contain at least one payment term.").format(template_name),
            frappe.ValidationError,
        )

    portion_total = Decimal(0)
    for row in terms:
        portion = _decimal(_value(row, "invoice_portion"))
        if portion is None or not portion.is_finite() or portion <= 0:
            frappe.throw(
                _("Each payment term in {0} must have an invoice portion greater than 0%.").format(
                    template_name
                ),
                frappe.ValidationError,
            )
        portion_total += portion

        credit_days = _decimal(_value(row, "credit_days"))
        if credit_days is None or not credit_days.is_finite() or credit_days < 0:
            frappe.throw(
                _("Credit days in {0} cannot be negative or invalid.").format(template_name),
                frappe.ValidationError,
            )

    if abs(portion_total - REQUIRED_PORTION_TOTAL) > PORTION_TOLERANCE:
        frappe.throw(
            _("{0} payment portions must total 100% (currently {1}%).").format(
                template_name, portion_total
            ),
            frappe.ValidationError,
        )
