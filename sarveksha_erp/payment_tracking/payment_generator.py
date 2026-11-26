# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import re
import frappe
from frappe import _
from frappe.utils import flt, fmt_money, getdate, nowdate


@frappe.whitelist()
def get_po_payment_summary_for_generator(po_name):
    """
    Grasps every detail of an individual Vendor Purchase Order for the Payment Entry Generator:
      - PO identity, reference number, workflow and payment status
      - Vendor details and company context
      - Financial breakdown: Grand Total, Already Paid Amount, Balance Due / Outstanding
      - Terms breakdown: Advance portion, Milestone schedule items with individual amounts & due dates
      - Execution choices: Company bank/cash accounts, Supplier payable accounts, Modes of Payment
      - History of existing payment entries linked to this PO
    """
    if not po_name:
        frappe.throw(_("Purchase Order name is required."), frappe.ValidationError)

    po = frappe.get_doc("Vendor Purchase Order", po_name)
    po.check_permission("read")

    grand_total = flt(getattr(po, "grand_total", 0.0), 2)
    currency = po.currency or "INR"

    # 1. Accurately calculate already paid amount from active Payment Entries (both submitted and draft pending)
    # Draft payment entries represent initiated payments waiting for cheque/UTR clearance!
    cleared_pe = 0.0
    draft_pe = 0.0

    # From direct column links if they exist
    if frappe.db.has_column("Payment Entry", "vendor_purchase_order"):
        pe_rows = frappe.db.sql(
            "SELECT docstatus, paid_amount FROM `tabPayment Entry` WHERE docstatus != 2 AND vendor_purchase_order = %s",
            (po_name,),
            as_dict=True,
        )
        for r in pe_rows:
            if r.docstatus == 1:
                cleared_pe += flt(r.paid_amount)
            elif r.docstatus == 0:
                draft_pe += flt(r.paid_amount)

    if frappe.db.has_column("Payment Entry", "custom_vendor_purchase_order"):
        pe_rows = frappe.db.sql(
            "SELECT docstatus, paid_amount FROM `tabPayment Entry` WHERE docstatus != 2 AND custom_vendor_purchase_order = %s",
            (po_name,),
            as_dict=True,
        )
        for r in pe_rows:
            if r.docstatus == 1:
                cleared_pe += flt(r.paid_amount)
            elif r.docstatus == 0:
                draft_pe += flt(r.paid_amount)

    # From Payment Entry Reference child table (linked direct PO or linked invoices)
    ref_rows = frappe.db.sql(
        """
        SELECT pe.docstatus, per.allocated_amount
        FROM `tabPayment Entry Reference` per
        JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE pe.docstatus != 2
        AND per.reference_doctype = 'Vendor Purchase Order'
        AND per.reference_name = %s
        """,
        (po_name,),
        as_dict=True,
    )
    for r in ref_rows:
        if r.docstatus == 1:
            cleared_pe += flt(r.allocated_amount)
        elif r.docstatus == 0:
            draft_pe += flt(r.allocated_amount)

    # From remarks reference
    remarks_pattern = f"%{po_name}%"
    ref_parent_query = "SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %s"
    rem_rows = frappe.db.sql(
        f"""
        SELECT docstatus, paid_amount
        FROM `tabPayment Entry`
        WHERE docstatus != 2
        AND (remarks LIKE %s OR custom_remarks LIKE %s)
        AND name NOT IN ({ref_parent_query})
        """,
        (remarks_pattern, remarks_pattern, po_name),
        as_dict=True,
    )
    for r in rem_rows:
        if r.docstatus == 1:
            cleared_pe += flt(r.paid_amount)
        elif r.docstatus == 0:
            draft_pe += flt(r.paid_amount)

    # From linked submitted Purchase Invoices
    invoices = frappe.get_all(
        "Purchase Invoice",
        filters={"vendor_purchase_order": po_name, "docstatus": 1},
        fields=["name", "grand_total", "outstanding_amount"],
    )
    paid_from_invoices = sum(
        max(flt(inv.grand_total) - flt(inv.outstanding_amount), 0.0) for inv in invoices
    )

    stored_advance = flt(getattr(po, "advance_amount", 0.0) if po.payment_status in ["Advance Paid", "Partially Paid", "Fully Paid"] else 0.0)
    cleared_total = max(flt(cleared_pe), flt(paid_from_invoices), stored_advance)
    cleared_total = min(cleared_total, grand_total)

    # Total paid includes all cleared payments plus drafted/in-progress payments waiting for cheque/UTR
    total_paid = min(cleared_total + flt(draft_pe), grand_total)
    balance_due = max(flt(grand_total - total_paid, 2), 0.0)

    # 2. Advance portion analysis
    adv_pct = flt(getattr(po, "advance_percentage", 0.0))
    adv_amt = flt(getattr(po, "advance_amount", 0.0))
    if adv_amt <= 0.0 and adv_pct > 0.0:
        adv_amt = flt(grand_total * adv_pct / 100.0, 2)
    elif adv_amt > 0.0 and adv_pct <= 0.0 and grand_total > 0.0:
        adv_pct = flt(adv_amt / grand_total * 100.0, 2)

    # 3. Milestone schedule items
    schedule_rows = []
    for idx, s in enumerate(po.get("payment_schedule") or [], 1):
        s_amt = flt(s.payment_amount, 2)
        schedule_rows.append({
            "idx": idx,
            "row_name": s.name,
            "payment_term": s.payment_term or f"Milestone {idx}",
            "portion": flt(s.invoice_portion, 2),
            "amount": s_amt,
            "formatted_amount": fmt_money(s_amt, currency=currency),
            "due_date": str(s.due_date) if s.due_date else "",
            "mode_of_payment": getattr(s, "mode_of_payment", "") or "",
        })

    # If no child rows in payment_schedule, construct from standard terms if advance exists
    if not schedule_rows and adv_amt > 0.0:
        schedule_rows.append({
            "idx": 1,
            "row_name": "advance",
            "payment_term": f"Advance ({adv_pct}%)" if adv_pct else "Advance Payment",
            "portion": adv_pct,
            "amount": adv_amt,
            "formatted_amount": fmt_money(adv_amt, currency=currency),
            "due_date": str(po.po_date) if getattr(po, "po_date", None) else str(nowdate()),
            "mode_of_payment": "",
        })
        bal_milestone = flt(grand_total - adv_amt, 2)
        if bal_milestone > 0:
            schedule_rows.append({
                "idx": 2,
                "row_name": "balance",
                "payment_term": f"Balance ({100.0 - adv_pct}%)",
                "portion": flt(100.0 - adv_pct, 2),
                "amount": bal_milestone,
                "formatted_amount": fmt_money(bal_milestone, currency=currency),
                "due_date": str(po.expected_delivery) if getattr(po, "expected_delivery", None) else "",
                "mode_of_payment": "",
            })

    # 4. Bank / Cash Accounts for Paid From (Company perspective)
    bank_accounts = frappe.get_all(
        "Account",
        filters={
            "company": po.company,
            "account_type": ["in", ["Bank", "Cash"]],
            "is_group": 0,
        },
        fields=["name", "account_type", "account_currency"],
        order_by="account_type asc, name asc",
    )
    default_bank_account = ""
    company_doc = frappe.get_doc("Company", po.company)
    if company_doc.default_bank_account:
        default_bank_account = company_doc.default_bank_account
    elif bank_accounts:
        default_bank_account = bank_accounts[0]["name"]

    # 5. Supplier Default Payable Account (Paid To)
    vendor_payable_account = frappe.db.get_value(
        "Party Account",
        {"parent": po.vendor, "parenttype": "Supplier", "company": po.company},
        "account",
    )
    if not vendor_payable_account:
        vendor_payable_account = company_doc.default_payable_account
    if not vendor_payable_account:
        vendor_payable_account = frappe.db.get_value(
            "Account",
            {"company": po.company, "account_type": "Payable", "is_group": 0},
            "name",
        )

    # 6. Active Modes of Payment
    modes_of_payment = frappe.get_all(
        "Mode of Payment",
        filters={"enabled": 1},
        pluck="name",
        order_by="name asc",
    )
    if not modes_of_payment:
        modes_of_payment = ["Bank Transfer", "Cheque", "Cash", "Wire Transfer"]

    # 7. Existing Payment Entries list
    existing_pes = []
    link_conds = ["remarks LIKE %(pat)s"]
    sql_params = {"party": po.vendor, "pat": f"%{po_name}%", "po_name": po_name}
    if getattr(po, "ref_number", None) and po.ref_number != po_name:
        link_conds.append("remarks LIKE %(ref_pat)s")
        sql_params["ref_pat"] = f"%{po.ref_number}%"

    if frappe.db.has_column("Payment Entry", "custom_vendor_purchase_order"):
        link_conds.append("custom_vendor_purchase_order = %(po_name)s")
    if frappe.db.has_column("Payment Entry", "vendor_purchase_order"):
        link_conds.append("vendor_purchase_order = %(po_name)s")
    link_conds.append("name IN (SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %(po_name)s)")

    pe_records = frappe.db.sql(
        f"""
        SELECT name, posting_date, mode_of_payment, paid_amount, docstatus, reference_no
        FROM `tabPayment Entry`
        WHERE party = %(party)s AND ({' OR '.join(link_conds)})
        ORDER BY creation DESC
        LIMIT 10
        """,
        sql_params,
        as_dict=True,
    )
    for r in pe_records:
        status_label = "Draft" if r.docstatus == 0 else "Submitted" if r.docstatus == 1 else "Cancelled"
        existing_pes.append({
            "name": r.name,
            "posting_date": str(r.posting_date),
            "mode_of_payment": r.mode_of_payment,
            "paid_amount": flt(r.paid_amount, 2),
            "formatted_amount": fmt_money(r.paid_amount, currency=currency),
            "status": status_label,
            "reference_no": r.reference_no or "",
        })

    # 8. Linked Purchase Invoice (if any)
    linked_invoice = po.purchase_invoice or frappe.db.get_value(
        "Purchase Invoice",
        {"vendor_purchase_order": po.name, "docstatus": ["!=", 2]},
        "name",
    )

    return {
        "po_name": po.name,
        "ref_number": po.ref_number or po.name,
        "workflow_state": po.workflow_state or "Draft",
        "po_status": po.status or "Draft",
        "payment_status": po.payment_status or "Pending",
        "company": po.company,
        "vendor": po.vendor,
        "currency": currency,
        "exchange_rate": flt(po.exchange_rate) or 1.0,
        "grand_total": grand_total,
        "formatted_grand_total": fmt_money(grand_total, currency=currency),
        "total_paid": total_paid,
        "formatted_total_paid": fmt_money(total_paid, currency=currency),
        "cleared_paid": cleared_total,
        "formatted_cleared_paid": fmt_money(cleared_total, currency=currency),
        "draft_paid": draft_pe,
        "formatted_draft_paid": fmt_money(draft_pe, currency=currency),
        "balance_due": balance_due,
        "formatted_balance_due": fmt_money(balance_due, currency=currency),
        "advance_percentage": adv_pct,
        "advance_amount": adv_amt,
        "formatted_advance_amount": fmt_money(adv_amt, currency=currency),
        "payment_terms": po.payment_terms or "",
        "payment_terms_template": getattr(po, "payment_terms_template", "") or "",
        "schedule": schedule_rows,
        "bank_accounts": bank_accounts,
        "default_bank_account": default_bank_account,
        "vendor_payable_account": vendor_payable_account,
        "modes_of_payment": modes_of_payment,
        "existing_payments": existing_pes,
        "linked_invoice": linked_invoice or "",
        "supplier_bank_details": {
            "bank_name": po.vendor_bank_name or "",
            "account_number": po.vendor_account_number or "",
            "ifsc": po.vendor_ifsc or "",
        },
    }


@frappe.whitelist()
def generate_payment_entry_against_po(
    po_name,
    payment_target_type,
    amount,
    mode_of_payment=None,
    paid_from=None,
    paid_to=None,
    reference_no=None,
    reference_date=None,
    payment_term=None,
    milestone_row_id=None,
    user_remarks=None,
):
    """
    Creates an official ERPNext Payment Entry directly linked to an individual Vendor Purchase Order.
    Grasps every detail (Vendor, Company, Accounts, Terms, Mode) and handles both:
      - Advance payments (pre-bill/deposit)
      - Milestone payments (against specific payment schedule terms)
      - Balance settlements
    """
    frappe.has_permission("Payment Entry", "create", throw=True)

    if not po_name:
        frappe.throw(_("Vendor Purchase Order name is mandatory."), frappe.ValidationError)

    po = frappe.get_doc("Vendor Purchase Order", po_name)
    po.check_permission("read")

    amount = flt(amount, 2)
    if amount <= 0:
        frappe.throw(_("Payment amount must be greater than zero."), frappe.ValidationError)

    currency = po.currency or "INR"
    now_d = getdate(nowdate())
    ref_d = getdate(reference_date) if reference_date else now_d

    # Fetch accounts if not passed
    company_doc = frappe.get_doc("Company", po.company)
    if not paid_from:
        paid_from = company_doc.default_bank_account or frappe.db.get_value(
            "Account",
            {"company": po.company, "account_type": ["in", ["Bank", "Cash"]], "is_group": 0},
            "name",
        )
    if not paid_from:
        frappe.throw(_("Please select a Paid From Bank/Cash account for {0}.").format(po.company))

    if not paid_to:
        paid_to = frappe.db.get_value(
            "Party Account",
            {"parent": po.vendor, "parenttype": "Supplier", "company": po.company},
            "account",
        ) or company_doc.default_payable_account or frappe.db.get_value(
            "Account",
            {"company": po.company, "account_type": "Payable", "is_group": 0},
            "name",
        )

    # Determine Payment Term descriptor
    term_label = payment_term or payment_target_type or "Vendor Payment"
    if payment_target_type == "Advance" and not payment_term:
        term_label = f"Advance Payment ({po.advance_percentage}% - {fmt_money(amount, currency=currency)})"

    # Construct clean, comprehensive remarks
    po_display = po.ref_number or po.name
    po_ref_tag = f"{po.name} ({po_display})" if getattr(po, "ref_number", None) and po.ref_number != po.name else po.name
    constructed_remarks = (
        f"Payment of {currency} {fmt_money(amount, currency=currency)} against Vendor Purchase Order {po_ref_tag} "
        f"({term_label}) to {po.vendor}."
    )
    if user_remarks:
        constructed_remarks += f" Note: {user_remarks.strip()}"

    # Auto-generate reference number if blank
    if not reference_no:
        reference_no = f"TXN-{po.name}-{now_d.strftime('%d%m%Y')}"

    # Create Payment Entry
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"
    pe.party_type = "Supplier"
    pe.party = po.vendor
    pe.party_name = po.vendor
    pe.company = po.company
    pe.paid_amount = amount
    pe.received_amount = amount
    pe.target_exchange_rate = flt(po.exchange_rate) or 1.0
    pe.paid_from = paid_from
    pe.paid_to = paid_to
    if not mode_of_payment or not frappe.db.exists("Mode of Payment", mode_of_payment):
        mode_of_payment = frappe.db.get_value("Mode of Payment", {"enabled": 1}, "name") or "Wire Transfer"
    pe.mode_of_payment = mode_of_payment
    pe.reference_no = reference_no
    pe.reference_date = ref_d
    pe.posting_date = ref_d
    # Set custom_remarks to 1 so ERPNext's set_remarks() does not overwrite our PO linkage remarks
    pe_meta = frappe.get_meta("Payment Entry")
    if pe_meta.has_field("custom_remarks"):
        pe.custom_remarks = 1
    pe.remarks = constructed_remarks
    if pe_meta.has_field("custom_vendor_purchase_order"):
        pe.custom_vendor_purchase_order = po.name
    if pe_meta.has_field("vendor_purchase_order"):
        pe.vendor_purchase_order = po.name
    if pe_meta.has_field("custom_payment_term_milestone") and payment_term and frappe.db.exists("Payment Term", payment_term):
        pe.custom_payment_term_milestone = payment_term
    if pe_meta.has_field("custom_milestone_row_id") and milestone_row_id:
        pe.custom_milestone_row_id = milestone_row_id

    # Check for linked submitted or draft Purchase Invoice
    linked_inv = po.purchase_invoice or frappe.db.get_value(
        "Purchase Invoice",
        {"vendor_purchase_order": po.name, "docstatus": 1},
        "name",
    )
    if linked_inv:
        inv_doc = frappe.get_doc("Purchase Invoice", linked_inv)
        pe.append("references", {
            "reference_doctype": "Purchase Invoice",
            "reference_name": linked_inv,
            "total_amount": flt(inv_doc.grand_total, 2),
            "outstanding_amount": flt(inv_doc.outstanding_amount, 2),
            "allocated_amount": min(amount, flt(inv_doc.outstanding_amount, 2)),
            "payment_term": payment_term or "",
        })

    pe.insert(ignore_permissions=True)

    # If this was an advance payment, immediately sync advance_amount on the PO
    if payment_target_type == "Advance" or "advance" in term_label.lower():
        current_advance = flt(po.advance_amount)
        new_advance = current_advance + amount
        frappe.db.set_value(
            "Vendor Purchase Order",
            po.name,
            {
                "advance_amount": new_advance,
                "payment_status": "Advance Paid" if new_advance < flt(po.grand_total) else "Fully Paid",
                "payment_partially_paid": 1 if new_advance < flt(po.grand_total) else 0,
                "payment_fully_paid": 1 if new_advance >= flt(po.grand_total) else 0,
                "payment_pending": 0,
            },
            update_modified=True,
        )

    return {
        "success": True,
        "payment_entry": pe.name,
        "amount": amount,
        "formatted_amount": fmt_money(amount, currency=currency),
        "po_name": po.name,
        "po_ref": po_display,
        "vendor": po.vendor,
        "term": term_label,
    }


@frappe.whitelist()
def get_pending_pos_for_vendor(vendor=None, company=None):
    """
    Returns all approved Purchase Orders with pending balance for selection inside Payment Entry.
    """
    conditions = ["docstatus != 2", "workflow_state IN ('Approved', 'Forwarded for Payment', 'Submitted', 'Partially Paid')"]
    values = {}

    if vendor:
        conditions.append("vendor = %(vendor)s")
        values["vendor"] = vendor
    if company:
        conditions.append("company = %(company)s")
        values["company"] = company

    where_clause = " AND ".join(conditions)

    pos = frappe.db.sql(
        f"""
        SELECT
            name,
            ref_number,
            po_date,
            vendor,
            company,
            currency,
            workflow_state,
            payment_status,
            COALESCE(grand_total, 0.0) as grand_total,
            COALESCE(advance_amount, 0.0) as advance_amount,
            COALESCE(advance_percentage, 0.0) as advance_percentage,
            COALESCE(balance_due, grand_total) as balance_due,
            payment_terms
        FROM `tabVendor Purchase Order`
        WHERE {where_clause}
        ORDER BY creation DESC
        LIMIT 50
        """,
        values,
        as_dict=True,
    )

    for p in pos:
        p["display_name"] = f"{p.ref_number or p.name} — {p.vendor} ({p.currency} {fmt_money(p.grand_total, currency=p.currency)})"
        p["formatted_grand_total"] = fmt_money(p.grand_total, currency=p.currency)
        p["formatted_balance_due"] = fmt_money(p.balance_due, currency=p.currency)

    return pos
