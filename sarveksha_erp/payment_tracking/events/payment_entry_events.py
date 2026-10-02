# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import os
import frappe
from frappe import _
from frappe.utils import flt, fmt_money
from frappe.utils.pdf import get_pdf

if not hasattr(frappe, "get_pdf"):
    frappe.get_pdf = get_pdf


def on_payment_entry_submit(doc, method=None):
    """
    Member 4 - Post-Payment Execution Event Hook.

    Triggered when a Payment Entry is approved and submitted to the General Ledger:
    1. Locates all linked Vendor Purchase Orders (via Purchase Invoices or direct link).
    2. Renders the official Payment Receipt Proof PDF.
    3. Attaches the PDF file to each linked Vendor Purchase Order's sidebar attachments.
    4. Recalculates and synchronizes the PO payment tracking metrics and status.
    5. Dispatches dual notifications:
       - Real-time desk alert and email with PDF proof to the PO creator/procurement user.
       - General Ledger posting audit email to the Finance & Accounts team.
    """
    linked_po_names = get_linked_vendor_purchase_orders(doc)
    if not linked_po_names:
        return

    # Render Payment Receipt Proof PDF
    pdf_bytes = generate_payment_receipt_proof_pdf(doc)

    currency = (
        doc.paid_to_account_currency
        or doc.paid_from_account_currency
        or doc.get("party_account_currency")
        or "USD"
    )
    paid_amount = flt(doc.paid_amount or doc.received_amount or 0)
    formatted_amount = fmt_money(paid_amount, currency=currency)

    for po_name in linked_po_names:
        if not frappe.db.exists("Vendor Purchase Order", po_name):
            continue

        po = frappe.get_doc("Vendor Purchase Order", po_name)

        # 1. Attach the PDF file to the PO sidebar attachments
        if pdf_bytes:
            attach_payment_proof_to_po(po, doc, pdf_bytes)

        # 2. Recalculate and update PO payment tracking metrics & status
        recalculate_po_payment_status(po_name)

        # Reload PO with latest data
        po.reload()

        # 3. Dispatch Dual Notifications
        dispatch_procurement_notification(po, doc, currency, formatted_amount, pdf_bytes)
        dispatch_finance_audit_notification(po, doc, currency, formatted_amount)


def get_linked_vendor_purchase_orders(doc) -> set:
    """
    Finds all linked Vendor Purchase Order names from Payment Entry references or custom links.
    """
    po_names = set()

    # Direct field link on Payment Entry if present
    if doc.get("vendor_purchase_order"):
        po_names.add(doc.vendor_purchase_order)
    if doc.get("custom_vendor_purchase_order"):
        po_names.add(doc.custom_vendor_purchase_order)

    # From Payment Entry Reference child table (linked Purchase Invoices)
    invoice_names = [
        row.reference_name
        for row in (doc.get("references") or [])
        if row.reference_doctype == "Purchase Invoice" and row.reference_name
    ]

    if invoice_names:
        pos_from_invoices = frappe.get_all(
            "Purchase Invoice",
            filters={"name": ["in", invoice_names]},
            pluck="vendor_purchase_order",
        )
        for p in pos_from_invoices:
            if p:
                po_names.add(p)

    # From direct PO references in child table if any
    direct_pos = [
        row.reference_name
        for row in (doc.get("references") or [])
        if row.reference_doctype == "Vendor Purchase Order" and row.reference_name
    ]
    for p in direct_pos:
        if p:
            po_names.add(p)

    return po_names


def generate_payment_receipt_proof_pdf(doc) -> bytes:
    """
    Renders the Payment Receipt Proof print format into standard PDF bytes.
    """
    # 1. Try standard frappe.get_print
    try:
        pdf_bytes = frappe.get_print(
            doctype="Payment Entry",
            name=doc.name,
            print_format="Payment Receipt Proof",
            doc=doc,
            as_pdf=True,
            no_letterhead=0,
        )
        if pdf_bytes:
            return pdf_bytes
    except Exception as e:
        frappe.log_error(
            title=f"Payment Proof PDF get_print notice ({doc.name})",
            message=f"Falling back to template rendering: {str(e)}",
        )

    # 2. Template fallback rendering with frappe.get_pdf
    try:
        html_path = os.path.join(
            frappe.get_app_path("sarveksha_erp"),
            "payment_tracking",
            "print_format",
            "payment_receipt_proof",
            "payment_receipt_proof.html",
        )
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                template_str = f.read()
            rendered_html = frappe.render_template(template_str, {"doc": doc, "frappe": frappe})
            return frappe.get_pdf(rendered_html)
    except Exception as e:
        frappe.log_error(
            title=f"Payment Proof PDF Render Error ({doc.name})",
            message=f"Failed rendering HTML template: {str(e)}\n\n{frappe.get_traceback()}",
        )

    return b""


def attach_payment_proof_to_po(po, doc, pdf_bytes: bytes):
    """
    Attaches the generated PDF payment proof to the linked Vendor Purchase Order.
    """
    file_name = f"Payment_Proof_{doc.name}.pdf"

    # Remove previous files with same name to avoid duplicate clutter
    existing_files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Vendor Purchase Order",
            "attached_to_name": po.name,
            "file_name": file_name,
        },
        pluck="name",
    )
    for ef in existing_files:
        try:
            frappe.delete_doc("File", ef, ignore_permissions=True, force=True)
        except Exception:
            pass

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": "Vendor Purchase Order",
        "attached_to_name": po.name,
        "content": pdf_bytes,
        "is_private": 0,
    })
    file_doc.insert(ignore_permissions=True)


def recalculate_po_payment_status(po_name: str):
    """
    Recalculates all financial rollup metrics and synchronizes status on the Vendor Purchase Order.
    """
    if not po_name:
        return

    try:
        po = frappe.get_doc("Vendor Purchase Order", po_name)
    except Exception:
        return

    invoices = frappe.get_all(
        "Purchase Invoice",
        filters={"vendor_purchase_order": po_name, "docstatus": ["!=", 2]},
        fields=["name", "docstatus", "grand_total", "outstanding_amount"],
        order_by="modified desc",
    )

    from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order import (
        calculate_vendor_po_payment_rollup,
    )

    rollup = calculate_vendor_po_payment_rollup(bool(getattr(po, "payment_forwarded_on", None)), invoices)
    has_submitted_invoice = any(int(invoice.get("docstatus") or 0) == 1 for invoice in invoices)

    rollup["balance_due"] = (
        rollup["outstanding_amount"]
        if has_submitted_invoice
        else flt(getattr(po, "grand_total", 0)) - flt(getattr(po, "advance_amount", 0))
    )

    # Sync payment_tracking_status if field exists
    if hasattr(po, "payment_tracking_status") or (hasattr(po, "as_dict") and "payment_tracking_status" in po.as_dict()):
        rollup["payment_tracking_status"] = rollup.get("payment_workflow_status")

    frappe.db.set_value(getattr(po, "doctype", "Vendor Purchase Order"), getattr(po, "name", po_name), rollup, update_modified=True)
    if hasattr(po, "notify_update"):
        po.notify_update()
    elif frappe.db.exists("Vendor Purchase Order", po_name):
        frappe.get_doc("Vendor Purchase Order", po_name).notify_update()


def dispatch_procurement_notification(po, doc, currency: str, formatted_amount: str, pdf_bytes: bytes):
    """
    Dispatches real-time desk alert and email notification with PDF proof to the PO creator/procurement user.
    """
    creator_user = po.prepared_by or po.owner or "Administrator"
    po_identifier = po.ref_number or po.name
    utr_display = doc.reference_no or doc.name

    # 1. Real-time Desk Alert via WebSocket
    try:
        frappe.publish_realtime(
            event="msgprint",
            message=_(
                "Payment of {0} {1} has been successfully executed for Purchase Order {2} (Ref: {3}). "
                "Payment Receipt Proof has been attached to the Purchase Order."
            ).format(currency, formatted_amount, po_identifier, utr_display),
            user=creator_user,
            title=_("Payment Executed & Settled"),
            indicator="green",
        )
    except Exception:
        pass

    # 2. Desk Notification Log (Bell icon in Frappe desk)
    if frappe.db.exists("User", creator_user):
        try:
            notification = frappe.new_doc("Notification Log")
            notification.subject = f"Payment Executed for PO {po_identifier} ({currency} {formatted_amount})"
            notification.for_user = creator_user
            notification.type = "Alert"
            notification.document_type = "Vendor Purchase Order"
            notification.document_name = po.name
            notification.email_content = (
                f"Payment of {currency} {formatted_amount} has been successfully executed "
                f"for Purchase Order {po_identifier} (Bank Ref: {utr_display}). "
                f"The official Payment Receipt Proof PDF is attached to the Purchase Order."
            )
            notification.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(
                title=f"Failed to create Notification Log for {creator_user}",
                message=str(e),
            )

    # 3. Email Confirmation with PDF attachment
    creator_email = frappe.db.get_value("User", creator_user, "email") or (
        creator_user if "@" in creator_user else None
    )
    if creator_email and "@" in creator_email:
        attachments = []
        if pdf_bytes:
            attachments.append({
                "fname": f"Payment_Proof_{doc.name}.pdf",
                "fcontent": pdf_bytes,
            })

        vendor_name = frappe.db.get_value("Supplier", po.vendor, "supplier_name") or po.vendor
        try:
            frappe.sendmail(
                recipients=[creator_email],
                subject=f"Payment Confirmation: Sarveksha PO {po_identifier} - Funds Dispatched",
                message=f"""
                <div style="font-family: Arial, sans-serif; color: #1e293b; max-width: 600px;">
                    <h3 style="color: #0f766e; margin-bottom: 8px;">Payment Execution &amp; Settlement Confirmation</h3>
                    <p>Dear {frappe.db.get_value('User', creator_user, 'full_name') or creator_user},</p>
                    <p>We are pleased to inform you that payment for Purchase Order <b>{po_identifier}</b> has been successfully approved, executed, and posted to the General Ledger.</p>
                    <table style="border-collapse: collapse; width: 100%; margin: 14px 0; border: 1px solid #e2e8f0; font-size: 13px;">
                        <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">PO Reference:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{po_identifier}</td></tr>
                        <tr><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Vendor / Supplier:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{vendor_name}</td></tr>
                        <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Payment Entry:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{doc.name}</td></tr>
                        <tr><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Bank UTR / Ref:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{utr_display}</td></tr>
                        <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Net Amount Paid:</td><td style="padding: 6px 10px; font-weight: bold; color: #0f766e; border: 1px solid #e2e8f0;">{currency} {formatted_amount}</td></tr>
                        <tr><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Posting Date:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{doc.posting_date}</td></tr>
                        <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Payment Status:</td><td style="padding: 6px 10px; font-weight: bold; color: #059669; border: 1px solid #e2e8f0;">Paid (Completed)</td></tr>
                    </table>
                    <p>The official <b>Payment Receipt Proof PDF</b> is attached to this email and is now accessible directly under the Purchase Order attachments in the ERP desk.</p>
                    <p>You can now use the <b>"Send Payment Proof to Vendor"</b> button on the Purchase Order form to dispatch official payment advice to the supplier.</p>
                    <br>
                    <p style="margin: 0;">Best Regards,<br><b>Sarveksha Finance &amp; Accounts Team</b></p>
                </div>
                """,
                attachments=attachments,
                now=True,
            )
        except Exception as e:
            frappe.log_error(
                title=f"Failed sending payment email to procurement user {creator_email}",
                message=str(e),
            )


def dispatch_finance_audit_notification(po, doc, currency: str, formatted_amount: str):
    """
    Dispatches audit log email to the Finance & Accounts team confirming successful General Ledger posting.
    """
    finance_emails = set()

    # Find users with Accounts Manager or Accounts Clerk roles
    finance_user_records = frappe.get_all(
        "Has Role",
        filters={"role": ["in", ["Accounts Manager", "Accounts Clerk"]], "parenttype": "User"},
        pluck="parent",
    )
    if finance_user_records:
        for u in frappe.get_all(
            "User",
            filters={"name": ["in", list(finance_user_records)], "enabled": 1},
            fields=["email"],
        ):
            if u.email and "@" in u.email:
                finance_emails.add(u.email)

    # Known standard test accounts
    for default_email in ["finance_manager1@sarveksha.com", "finance_clerk1@sarveksha.com"]:
        if frappe.db.exists("User", default_email):
            finance_emails.add(default_email)

    if not finance_emails:
        return

    po_identifier = po.ref_number or po.name
    utr_display = doc.reference_no or doc.name

    try:
        frappe.sendmail(
            recipients=list(finance_emails),
            subject=f"Audit Alert: Payment Entry {doc.name} Posted to General Ledger",
            message=f"""
            <div style="font-family: Arial, sans-serif; color: #1e293b; max-width: 600px;">
                <h3 style="color: #0f766e; margin-bottom: 8px;">General Ledger Posting Audit Confirmation</h3>
                <p>Payment Entry <b>{doc.name}</b> has been approved and successfully submitted to the General Ledger.</p>
                <table style="border-collapse: collapse; width: 100%; margin: 14px 0; border: 1px solid #e2e8f0; font-size: 13px;">
                    <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Payment Entry:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{doc.name}</td></tr>
                    <tr><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Approved / Submitted By:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{frappe.session.user}</td></tr>
                    <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Beneficiary (Party):</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{doc.party_name or doc.party}</td></tr>
                    <tr><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Net Amount:</td><td style="padding: 6px 10px; font-weight: bold; color: #0f766e; border: 1px solid #e2e8f0;">{currency} {formatted_amount}</td></tr>
                    <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Bank Ref / UTR:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{utr_display}</td></tr>
                    <tr><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Posting Date:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{doc.posting_date}</td></tr>
                    <tr style="background: #f8fafc;"><td style="padding: 6px 10px; font-weight: bold; border: 1px solid #e2e8f0;">Linked PO:</td><td style="padding: 6px 10px; border: 1px solid #e2e8f0;">{po_identifier}</td></tr>
                </table>
                <p style="font-size: 11px; color: #64748b;"><i>Automated audit notification generated on General Ledger transaction completion.</i></p>
            </div>
            """,
            now=True,
        )
    except Exception as e:
        frappe.log_error(title="Failed to send finance audit email", message=str(e))
