import calendar
import datetime

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, nowdate


def calculate_due_date_from_term(term_doc, base_date):
    """
    Computes milestone due date based on Payment Term rules:
    - credit_days
    - credit_months with safe month-end roll-forward
    - due_date_based_on ("Day(s) after invoice date", "Day(s) after end of the invoice month", "Month(s) after the end of the invoice month")
    """
    if isinstance(base_date, str):
        base_date = getdate(base_date)

    if not term_doc:
        return base_date

    due_date_based_on = getattr(term_doc, "due_date_based_on", "Day(s) after invoice date")
    credit_days = getattr(term_doc, "credit_days", 0) or 0
    credit_months = getattr(term_doc, "credit_months", 0) or 0

    if due_date_based_on == "Day(s) after end of the invoice month":
        last_day = calendar.monthrange(base_date.year, base_date.month)[1]
        month_end = datetime.date(base_date.year, base_date.month, last_day)
        return add_days(month_end, credit_days)

    elif due_date_based_on == "Month(s) after the end of the invoice month":
        month = base_date.month + credit_months
        year = base_date.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        last_day = calendar.monthrange(year, month)[1]
        target_day = min(base_date.day, last_day)
        return datetime.date(year, month, target_day)

    # Default: Day(s) after invoice date
    target = add_days(base_date, credit_days)
    if credit_months:
        month = target.month + credit_months
        year = target.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        last_day = calendar.monthrange(year, month)[1]
        target_day = min(target.day, last_day)
        target = datetime.date(year, month, target_day)

    return target


@frappe.whitelist()
def make_purchase_invoice_from_po(po_name):
    """
    Maps a Vendor Purchase Order into a draft ERPNext Purchase Invoice:
    - Transcribes Supplier, Company, Currency, Conversion Rate
    - Sets custom_vendor_purchase_order link to PO
    - Maps Items (item_code, qty, rate, uom, description)
    - Transfers milestone schedule from PO to standard ERPNext payment_schedule
    - Reallocates milestone portions to match invoice total with paise precision
    """
    po = frappe.get_doc("Vendor Purchase Order", po_name)

    invoice = frappe.new_doc("Purchase Invoice")
    invoice.supplier = po.get("supplier") or po.get("vendor")
    invoice.company = po.company
    invoice.currency = po.currency
    invoice.conversion_rate = flt(getattr(po, "conversion_rate", 1.0) or 1.0)
    invoice.posting_date = nowdate()
    invoice.custom_vendor_purchase_order = po.name

    if getattr(po, "payment_terms_template", None):
        invoice.payment_terms_template = po.payment_terms_template

    # Map Items
    for item in po.get("items", []):
        inv_item = invoice.append("items", {})
        item_code = getattr(item, "item_code", None) or getattr(item, "equipment", None) or "ITEM-001"
        item_name = getattr(item, "item_name", None) or getattr(item, "equipment_name", None) or item_code
        qty = flt(getattr(item, "qty", None) or getattr(item, "quantity", 1.0))
        rate = flt(getattr(item, "rate", 0.0))
        uom = getattr(item, "uom", None) or getattr(item, "unit", None) or "Nos"
        description = getattr(item, "description", None) or getattr(item, "specification", None) or item_name

        inv_item.item_code = item_code
        inv_item.item_name = item_name
        inv_item.description = description
        inv_item.qty = qty
        inv_item.uom = uom
        inv_item.rate = rate
        inv_item.amount = flt(qty * rate, 2)

    # Calculate totals
    invoice.run_method("calculate_taxes_and_totals")

    # Transfer payment schedule
    po_schedule = po.get("payment_schedule", [])
    if po_schedule:
        invoice.set("payment_schedule", [])
        for row in po_schedule:
            sch_row = invoice.append("payment_schedule", {})
            sch_row.payment_term = getattr(row, "payment_term", None)
            sch_row.description = getattr(row, "description", None)
            sch_row.invoice_portion = flt(getattr(row, "invoice_portion", 0.0), 4)
            sch_row.discount_type = getattr(row, "discount_type", None)
            sch_row.discount_date = getattr(row, "discount_date", None)
            sch_row.discount = flt(getattr(row, "discount", 0.0), 2)
            sch_row.paid_amount = 0.0

            # Derive due date
            if getattr(row, "payment_term", None) and frappe.db.exists("Payment Term", row.payment_term):
                term_doc = frappe.get_doc("Payment Term", row.payment_term)
                sch_row.due_date = calculate_due_date_from_term(term_doc, invoice.posting_date)
            else:
                sch_row.due_date = getattr(row, "due_date", None) or invoice.posting_date

    # Reallocate milestone portions with cent/paise balancing
    reallocate_invoice_milestone_schedule(invoice)

    return invoice


def reallocate_invoice_milestone_schedule(doc, method=None):
    """
    Hook on Purchase Invoice 'validate' / 'before_save':
    Re-distributes milestone payment amounts and outstandings if grand_total, taxes,
    or freight charges differ from originating PO.
    Maintains exact 2-decimal cent/paise balancing by absorbing rounding difference on the N-th row.
    """
    if not doc.get("payment_schedule"):
        return

    total = flt(getattr(doc, "rounded_total", None) or getattr(doc, "grand_total", 0.0), 2)
    if total <= 0:
        return

    schedule = doc.payment_schedule
    n = len(schedule)

    allocated_sum = 0.0
    for idx, row in enumerate(schedule):
        portion = flt(row.invoice_portion, 4)
        paid = flt(getattr(row, "paid_amount", 0.0), 2)

        if idx < n - 1:
            row_amount = flt(total * (portion / 100.0), 2)
            allocated_sum += row_amount
        else:
            # Final milestone absorbs remainder to achieve exact zero-variance balancing
            row_amount = flt(total - allocated_sum, 2)

        row.payment_amount = row_amount
        row.outstanding = flt(row_amount - paid, 2)


def validate_invoice_milestone_schedule_before_submit(doc, method=None):
    """
    Hook on Purchase Invoice 'before_submit':
    Verifies that the sum of payment amounts in payment_schedule strictly equals
    the invoice rounded_total or grand_total within +/- 0.01 tolerance.
    """
    if not doc.get("payment_schedule"):
        return

    target_total = flt(getattr(doc, "rounded_total", None) or getattr(doc, "grand_total", 0.0), 2)
    schedule_total = flt(sum(flt(r.payment_amount, 2) for r in doc.payment_schedule), 2)

    variance = abs(target_total - schedule_total)
    if variance > 0.01:
        frappe.throw(
            _(
                "Payment Schedule Total ({0}) does not match Invoice Grand Total ({1}). "
                "Please re-save the invoice to recalculate milestone allocations."
            ).format(schedule_total, target_total)
        )
