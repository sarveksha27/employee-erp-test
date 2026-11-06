import frappe
from frappe import _
from frappe.utils import flt


MILESTONE_ROLES = {"Accounts Clerk", "Accounts Manager", "System Manager", "Administrator"}


def _get_invoice_purchase_order(invoice):
    return invoice.get("vendor_purchase_order") or invoice.get("custom_vendor_purchase_order")


def _get_milestone_row(invoice, milestone_row_id):
    return next(
        (row for row in invoice.get("payment_schedule") or [] if row.name == milestone_row_id),
        None,
    )


def _require_milestone_fields():
    meta = frappe.get_meta("Payment Entry")
    missing = [
        fieldname
        for fieldname in ("custom_payment_term_milestone", "custom_milestone_row_id")
        if not meta.has_field(fieldname)
    ]
    if missing:
        frappe.throw(
            _("Milestone Payment fields are missing from Payment Entry: {0}. Run bench migrate.").format(
                ", ".join(missing)
            ),
            frappe.ValidationError,
        )


@frappe.whitelist()
def make_milestone_payment_entry(invoice_name, milestone_row_id):
    roles = set(frappe.get_roles())
    if not roles.intersection(MILESTONE_ROLES):
        frappe.throw(_("You are not allowed to create milestone payments."), frappe.PermissionError)

    if not invoice_name or not milestone_row_id:
        frappe.throw(_("Select an invoice and payment milestone."), frappe.ValidationError)

    invoice = frappe.get_doc("Purchase Invoice", invoice_name)
    invoice.check_permission("read")
    frappe.has_permission("Payment Entry", "create", throw=True)
    if invoice.docstatus != 1:
        frappe.throw(_("Milestone payments can only be created from submitted invoices."), frappe.ValidationError)
    if not _get_invoice_purchase_order(invoice):
        frappe.throw(_("This Purchase Invoice is not linked to a Vendor Purchase Order."), frappe.ValidationError)

    row = _get_milestone_row(invoice, milestone_row_id)
    if not row:
        frappe.throw(_("The selected milestone does not belong to this invoice."), frappe.ValidationError)
    if not row.payment_term:
        frappe.throw(_("The selected milestone has no Payment Term."), frappe.ValidationError)

    outstanding = flt(row.outstanding)
    if outstanding <= 0:
        frappe.throw(_("The selected milestone has no outstanding balance."), frappe.ValidationError)

    _require_milestone_fields()

    existing_entry = frappe.db.get_value(
        "Payment Entry",
        {"custom_milestone_row_id": milestone_row_id, "docstatus": 0},
        "name",
    )
    if existing_entry:
        frappe.has_permission("Payment Entry", "read", doc=existing_entry, throw=True)
        return existing_entry

    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

    payment_entry = get_payment_entry("Purchase Invoice", invoice.name, party_amount=outstanding)
    payment_entry.set("references", [])
    payment_entry.append(
        "references",
        {
            "reference_doctype": "Purchase Invoice",
            "reference_name": invoice.name,
            "payment_term": row.payment_term,
            "due_date": row.due_date,
            "total_amount": flt(invoice.grand_total),
            "outstanding_amount": outstanding,
            "allocated_amount": outstanding,
        },
    )
    payment_entry.payment_type = "Pay"
    payment_entry.party_type = "Supplier"
    payment_entry.party = invoice.supplier
    payment_entry.paid_amount = outstanding
    payment_entry.received_amount = outstanding
    payment_entry.custom_payment_term_milestone = row.payment_term
    payment_entry.custom_milestone_row_id = row.name
    payment_entry.workflow_state = "Draft"

    if payment_entry.meta.has_field("custom_vendor_purchase_order"):
        payment_entry.custom_vendor_purchase_order = _get_invoice_purchase_order(invoice)

    payment_entry.insert()
    return payment_entry.name


def validate_milestone_payment_entry(doc, method=None):
    milestone_row_id = doc.get("custom_milestone_row_id")
    if not milestone_row_id:
        return

    references = doc.get("references") or []
    if len(references) != 1 or references[0].reference_doctype != "Purchase Invoice":
        frappe.throw(
            _("A milestone Payment Entry must reference exactly one Purchase Invoice."),
            frappe.ValidationError,
        )

    reference = references[0]
    invoice = frappe.get_doc("Purchase Invoice", reference.reference_name)
    row = _get_milestone_row(invoice, milestone_row_id)
    if not row:
        frappe.throw(_("The selected milestone does not belong to the referenced invoice."), frappe.ValidationError)
    if (
        doc.payment_type != "Pay"
        or doc.party_type != "Supplier"
        or doc.party != invoice.supplier
    ):
        frappe.throw(_("A milestone Payment Entry must pay the invoice supplier."), frappe.ValidationError)
    if (
        reference.payment_term != row.payment_term
        or doc.get("custom_payment_term_milestone") != row.payment_term
    ):
        frappe.throw(_("The Payment Entry Payment Term does not match the selected milestone."), frappe.ValidationError)

    allocated_amount = flt(reference.allocated_amount)
    if allocated_amount <= 0 or allocated_amount > flt(row.outstanding):
        frappe.throw(
            _("The allocated amount must be positive and no greater than the milestone balance."),
            frappe.ValidationError,
        )


def sync_milestone_payment_status(doc, method=None):
    milestone_row_id = doc.get("custom_milestone_row_id")
    if not milestone_row_id:
        return

    reference = next(
        (
            ref
            for ref in doc.get("references") or []
            if ref.reference_doctype == "Purchase Invoice"
        ),
        None,
    )
    if not reference:
        frappe.log_error(
            title=_("Milestone Payment Entry has no Purchase Invoice reference"),
            message=doc.name,
        )
        return

    invoice = frappe.get_doc("Purchase Invoice", reference.reference_name)
    row = _get_milestone_row(invoice, milestone_row_id)
    if not row:
        frappe.log_error(
            title=_("Milestone Payment Entry references a missing schedule row"),
            message=f"Payment Entry: {doc.name}; milestone row: {milestone_row_id}",
        )
        return

    if frappe.get_meta("Payment Schedule").has_field("custom_milestone_status"):
        status = "Paid" if flt(row.outstanding) <= 0 else "Partially Paid" if flt(row.paid_amount) > 0 else "Pending"
        frappe.db.set_value(
            "Payment Schedule",
            row.name,
            "custom_milestone_status",
            status,
            update_modified=False,
        )

    po_name = _get_invoice_purchase_order(invoice)
    if not po_name:
        return

    purchase_order_fields = frappe.get_meta("Purchase Invoice").fields
    po_link_fields = [
        field.fieldname
        for field in purchase_order_fields
        if field.fieldname in ("vendor_purchase_order", "custom_vendor_purchase_order")
    ]
    if not po_link_fields:
        return

    conditions = " OR ".join(f"`{field}` = %s" for field in po_link_fields)
    invoices = frappe.db.sql(
        f"""
        SELECT COALESCE(SUM(grand_total), 0) AS billed_amount,
            COALESCE(SUM(outstanding_amount), 0) AS outstanding_amount
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1 AND ({conditions})
        """,
        tuple(po_name for _ in po_link_fields),
        as_dict=True,
    )[0]
    billed_amount = flt(invoices.billed_amount)
    outstanding_amount = max(flt(invoices.outstanding_amount), 0)
    paid_amount = max(billed_amount - outstanding_amount, 0)
    if billed_amount <= 0:
        return

    if outstanding_amount <= 0:
        tracking_status, payment_status = "Paid", "Fully Paid"
    elif paid_amount > 0:
        tracking_status, payment_status = "Partially Paid", "Partially Paid"
    else:
        return

    values = {
        "payment_tracking_status": tracking_status,
        "payment_workflow_status": tracking_status,
        "payment_status": payment_status,
        "billed_amount": billed_amount,
        "outstanding_amount": outstanding_amount,
        "balance_due": outstanding_amount,
        "payment_pending": 0,
        "payment_partially_paid": int(tracking_status == "Partially Paid"),
        "payment_fully_paid": int(tracking_status == "Paid"),
    }
    po_meta = frappe.get_meta("Vendor Purchase Order")
    values = {field: value for field, value in values.items() if po_meta.has_field(field)}
    frappe.db.set_value("Vendor Purchase Order", po_name, values, update_modified=True)
    frappe.get_doc("Vendor Purchase Order", po_name).notify_update()
