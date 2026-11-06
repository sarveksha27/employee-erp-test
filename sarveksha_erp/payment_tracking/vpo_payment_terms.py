# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import calendar
import datetime

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, nowdate


@frappe.whitelist()
def get_supplier_default_payment_terms(supplier):
    """
    Retrieves default payment terms template configured on Supplier or Supplier Group.
    Falls back to Supplier Group if Supplier has no payment_terms set.

    Returns:
        {
            "payment_terms_template": str,
            "terms": [
                {
                    "payment_term": str,
                    "description": str,
                    "invoice_portion": float,
                    "credit_days": int,
                    "due_date_based_on": str
                }
            ]
        }
    """
    if not supplier:
        return {}

    # 1. Try supplier-level default
    supplier_data = frappe.db.get_value(
        "Supplier", supplier, ["payment_terms", "supplier_group"], as_dict=True
    )
    if not supplier_data:
        return {}

    template_name = supplier_data.get("payment_terms")

    # 2. Fall back to supplier group
    if not template_name and supplier_data.get("supplier_group"):
        template_name = frappe.db.get_value(
            "Supplier Group", supplier_data.get("supplier_group"), "payment_terms"
        )

    if not template_name:
        return {}

    if not frappe.db.exists("Payment Terms Template", template_name):
        return {}

    tmpl = frappe.get_doc("Payment Terms Template", template_name)
    terms = []
    for row in tmpl.terms:
        term_detail = {
            "payment_term": row.payment_term,
            "description": row.description or "",
            "invoice_portion": flt(row.invoice_portion, 4),
            "credit_days": row.credit_days or 0,
            "credit_months": row.credit_months or 0,
            "due_date_based_on": row.due_date_based_on or "Day(s) after invoice date",
        }
        terms.append(term_detail)

    return {
        "payment_terms_template": template_name,
        "terms": terms,
    }


def calculate_vpo_payment_schedule(doc):
    """
    Recalculates milestone currency amounts based on doc.grand_total.

    Formula for row 1 to N-1:
        Milestone Amount = flt(doc.grand_total * (row.invoice_portion / 100.0), 2)

    Rounding Reconciliation:
        Allocated Sum = sum(Milestone Amount for rows 1 to N-1)
        Final Row Amount = doc.grand_total - Allocated Sum

    Ensures sum(milestone amounts) == doc.grand_total exactly to 2 decimal places.
    Sets due_date on each row using posting date or current date + credit_days.
    """
    if not doc.get("payment_schedule"):
        return

    grand_total = flt(getattr(doc, "grand_total", 0.0), 2)
    if grand_total <= 0:
        return

    schedule = doc.payment_schedule
    n = len(schedule)
    base_date = getdate(getattr(doc, "po_date", None) or nowdate())

    allocated_sum = 0.0
    for idx, row in enumerate(schedule):
        portion = flt(getattr(row, "invoice_portion", 0.0), 4)
        credit_days = int(getattr(row, "credit_days", 0) or 0)
        credit_months = int(getattr(row, "credit_months", 0) or 0)

        if idx < n - 1:
            row_amount = flt(grand_total * (portion / 100.0), 2)
            allocated_sum += row_amount
        else:
            # Final milestone absorbs remainder for exact paise balancing
            row_amount = flt(grand_total - allocated_sum, 2)

        row.payment_amount = row_amount
        paid = flt(getattr(row, "paid_amount", 0.0) or 0.0, 2)
        row.outstanding = flt(row_amount - paid, 2)

        # Compute due_date
        due_date_based_on = (
            getattr(row, "due_date_based_on", "Day(s) after invoice date")
            or "Day(s) after invoice date"
        )
        if due_date_based_on == "Day(s) after end of the invoice month":
            last_day = calendar.monthrange(base_date.year, base_date.month)[1]
            month_end = datetime.date(base_date.year, base_date.month, last_day)
            row.due_date = add_days(month_end, credit_days)
        elif due_date_based_on in (
            "Month(s) after the end of the invoice month",
            "Month(s) after invoice date",
        ):
            row.due_date = _safe_add_months(base_date, credit_months)
        else:
            # Default: Day(s) after invoice date
            row.due_date = add_days(base_date, credit_days)


def _safe_add_months(base_date, months):
    """Safely add months with month-end roll-forward handling."""
    if isinstance(base_date, str):
        base_date = getdate(base_date)
    month = base_date.month + months
    year = base_date.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    last_day = calendar.monthrange(year, month)[1]
    target_day = min(base_date.day, last_day)
    return datetime.date(year, month, target_day)


def validate_vpo_payment_schedule(doc):
    """
    Validates that the payment_schedule on a Vendor Purchase Order is complete and balanced
    before forwarding. Called from the VPO validate() method when workflow state is advancing.

    Checks:
    1. payment_terms_template is set
    2. payment_schedule has at least one row
    3. sum(payment_amount) equals grand_total within tolerance 0.01

    Raises frappe.ValidationError if any check fails.
    """
    if not getattr(doc, "payment_terms_template", None):
        frappe.throw(
            _("Cannot approve or forward PO without a complete and balanced Payment Schedule."),
            frappe.ValidationError,
        )

    schedule = doc.get("payment_schedule", [])
    if not schedule:
        frappe.throw(
            _("Cannot approve or forward PO without a complete and balanced Payment Schedule."),
            frappe.ValidationError,
        )

    grand_total = flt(getattr(doc, "grand_total", 0.0), 2)
    schedule_total = flt(sum(flt(row.payment_amount, 2) for row in schedule), 2)

    if round(abs(grand_total - schedule_total), 2) > 0.01:
        frappe.throw(
            _("Cannot approve or forward PO without a complete and balanced Payment Schedule."),
            frappe.ValidationError,
        )
