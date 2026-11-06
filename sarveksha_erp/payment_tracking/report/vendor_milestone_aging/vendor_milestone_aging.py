import frappe
from frappe import _
from frappe.utils import flt, getdate, today


AGING_BUCKETS = (
    (0, "Current"),
    (30, "1-30 Days"),
    (60, "31-60 Days"),
    (90, "61-90 Days"),
    (float("inf"), "90+ Days"),
)


def get_aging_bucket(due_date, outstanding_amount, report_date=None):
    if flt(outstanding_amount) <= 0:
        return "Current"

    report_date = getdate(report_date or today())
    days_overdue = (report_date - getdate(due_date)).days
    if days_overdue <= 0:
        return "Current"
    for max_days, label in AGING_BUCKETS[1:]:
        if days_overdue <= max_days:
            return label
    return AGING_BUCKETS[-1][1]


def get_milestone_status(due_date, outstanding_amount, report_date=None):
    if flt(outstanding_amount) <= 0:
        return "Paid"
    if getdate(due_date) < getdate(report_date or today()):
        return "Overdue"
    return "Pending"


def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not filters.company:
        frappe.throw(_("Company is required."), frappe.ValidationError)
    if filters.from_date and filters.to_date and getdate(filters.from_date) > getdate(filters.to_date):
        frappe.throw(_("From Date cannot be later than To Date."), frappe.ValidationError)

    frappe.has_permission("Purchase Invoice", "read", throw=True)
    invoice_meta = frappe.get_meta("Purchase Invoice")
    po_field = next(
        (
            fieldname
            for fieldname in ("vendor_purchase_order", "custom_vendor_purchase_order")
            if invoice_meta.has_field(fieldname)
        ),
        None,
    )
    po_select = f"pi.`{po_field}`" if po_field else "NULL"

    conditions = ["pi.docstatus = 1", "pi.company = %s"]
    values = [filters.company]
    if filters.supplier:
        conditions.append("pi.supplier = %s")
        values.append(filters.supplier)
    if filters.from_date:
        conditions.append("ps.due_date >= %s")
        values.append(filters.from_date)
    if filters.to_date:
        conditions.append("ps.due_date <= %s")
        values.append(filters.to_date)

    rows = frappe.db.sql(
        f"""
        SELECT pi.supplier AS vendor, {po_select} AS po_reference, pi.currency,
            pi.name AS invoice, ps.payment_term AS milestone_term,
            ps.due_date, ps.invoice_portion AS milestone_portion,
            ps.payment_amount AS milestone_amount,
            ps.paid_amount, ps.outstanding AS outstanding_amount
        FROM `tabPurchase Invoice` pi
        JOIN `tabPayment Schedule` ps
            ON ps.parent = pi.name
            AND ps.parenttype = 'Purchase Invoice'
            AND ps.parentfield = 'payment_schedule'
        WHERE {" AND ".join(conditions)}
        ORDER BY ps.due_date, pi.name, ps.idx
        """,
        values,
        as_dict=True,
    )

    report_date = getdate(today())
    results = []
    for row in rows:
        row.aging_bucket = get_aging_bucket(row.due_date, row.outstanding_amount, report_date)
        row.status = get_milestone_status(row.due_date, row.outstanding_amount, report_date)
        if filters.status in ("Pending", "Overdue", "Paid") and row.status != filters.status:
            continue
        results.append(row)

    return get_columns(), results


def get_columns():
    return [
        {"label": _("Vendor"), "fieldname": "vendor", "fieldtype": "Link", "options": "Supplier", "width": 150},
        {
            "label": _("PO Reference"),
            "fieldname": "po_reference",
            "fieldtype": "Link",
            "options": "Vendor Purchase Order",
            "width": 160,
        },
        {
            "label": _("Invoice"),
            "fieldname": "invoice",
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 150,
        },
        {"label": _("Milestone Term"), "fieldname": "milestone_term", "fieldtype": "Data", "width": 150},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": _("Milestone Portion"), "fieldname": "milestone_portion", "fieldtype": "Percent", "width": 120},
        {
            "label": _("Milestone Amount"),
            "fieldname": "milestone_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 130,
        },
        {
            "label": _("Paid Amount"),
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Outstanding Amount"),
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140,
        },
        {"label": _("Aging Bucket"), "fieldname": "aging_bucket", "fieldtype": "Data", "width": 110},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
