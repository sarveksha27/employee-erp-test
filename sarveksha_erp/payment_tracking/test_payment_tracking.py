# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import MagicMock, patch
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, nowdate
from frappe.utils.pdf import get_pdf

if not hasattr(frappe, "get_pdf"):
    frappe.get_pdf = get_pdf

import erpnext.accounts.utils
_orig_get_fiscal_years = getattr(erpnext.accounts.utils, "get_fiscal_years", None)
def mock_get_fiscal_years(*args, **kwargs):
    if _orig_get_fiscal_years:
        try:
            res = _orig_get_fiscal_years(*args, **kwargs)
            if res:
                return res
        except Exception:
            pass
    fys = frappe.db.get_all(
        "Fiscal Year",
        fields=["name", "year_start_date", "year_end_date"],
        filters={"disabled": 0},
        order_by="year_start_date desc",
        limit=1,
    )
    if kwargs.get("boolean"):
        return bool(fys)
    if kwargs.get("as_dict"):
        return [{"name": f["name"], "year_start_date": f["year_start_date"], "year_end_date": f["year_end_date"]} for f in fys]
    return [(f["name"], f["year_start_date"], f["year_end_date"]) for f in fys]

erpnext.accounts.utils.get_fiscal_years = mock_get_fiscal_years
erpnext.accounts.utils._get_fiscal_years = mock_get_fiscal_years
import erpnext.controllers.accounts_controller
erpnext.controllers.accounts_controller.get_fiscal_years = mock_get_fiscal_years

from sarveksha_erp.payment_tracking.events.payment_entry_events import (
    attach_payment_proof_to_po,
    dispatch_finance_audit_notification,
    dispatch_procurement_notification,
    generate_payment_receipt_proof_pdf,
    get_linked_vendor_purchase_orders,
    on_payment_entry_submit,
    recalculate_po_payment_status,
)


class TestPaymentTracking(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_company = "Sarveksha BSTP SAS"
        if not frappe.db.exists("Company", cls.test_company):
            cls.test_company = frappe.db.get_value("Company", {}, "name")
        cls.test_vendor = "Action Construction Equipment"
        if not frappe.db.exists("Supplier", cls.test_vendor):
            cls.test_vendor = frappe.db.get_value("Supplier", {}, "name")

    def setUp(self):
        super().setUp()
        self.created_pos = []
        self.created_invoices = []
        self.created_pes = []
        self.created_files = []

    def tearDown(self):
        super().tearDown()
        for f in getattr(self, "created_files", []):
            try:
                frappe.db.delete("File", {"name": f})
            except Exception:
                pass
        for pe in getattr(self, "created_pes", []):
            try:
                frappe.db.delete("Payment Entry Reference", {"parent": pe})
                frappe.db.delete("Payment Entry", {"name": pe})
            except Exception:
                pass
        for inv in getattr(self, "created_invoices", []):
            try:
                frappe.db.delete("Purchase Invoice", {"name": inv})
            except Exception:
                pass
        for po in getattr(self, "created_pos", []):
            try:
                frappe.db.delete("Vendor Purchase Order Item", {"parent": po})
                frappe.db.delete("Vendor Purchase Order", {"name": po})
            except Exception:
                pass
        frappe.db.commit()

    def _create_test_po(self):
        po = frappe.new_doc("Vendor Purchase Order")
        po.company = self.test_company
        po.vendor = self.test_vendor
        po.quantity = 1.0
        po.rate = 1000.0
        po.exchange_rate = 1.0
        po.expected_delivery = frappe.utils.add_days(nowdate(), 7)
        po.delivery_location = "Conakry Port"
        po.workflow_state = "Draft"
        po.prepared_by = "Administrator"
        po.flags.ignore_mandatory = True
        po.save(ignore_permissions=True)
        po.workflow_state = "Approved"
        po.status = "Approved"
        po.docstatus = 1
        po.payment_workflow_status = "Forwarded for Payment"
        po.payment_forwarded_on = frappe.utils.now_datetime()
        po.db_update()
        if hasattr(self, "created_pos"):
            self.created_pos.append(po.name)
        return po

    def test_get_linked_vendor_purchase_orders_from_invoice(self):
        po = self._create_test_po()
        invoice = frappe.new_doc("Purchase Invoice")
        invoice.company = self.test_company
        invoice.supplier = self.test_vendor
        invoice.vendor_purchase_order = po.name
        invoice.bill_no = f"INV-{frappe.generate_hash(length=6)}"
        invoice.bill_date = nowdate()
        invoice.flags.ignore_mandatory = True
        invoice.flags.ignore_validate = True
        invoice.flags.ignore_links = True
        invoice.db_insert()
        if hasattr(self, "created_invoices"):
            self.created_invoices.append(invoice.name)

        payment_entry = frappe._dict({
            "name": "ACC-PAY-TEST-001",
            "references": [
                frappe._dict({
                    "reference_doctype": "Purchase Invoice",
                    "reference_name": invoice.name,
                })
            ]
        })

        linked_pos = get_linked_vendor_purchase_orders(payment_entry)
        self.assertIn(po.name, linked_pos)

    def test_get_linked_vendor_purchase_orders_direct(self):
        po = self._create_test_po()
        payment_entry = frappe._dict({
            "name": "ACC-PAY-TEST-002",
            "custom_vendor_purchase_order": po.name,
            "references": []
        })

        linked_pos = get_linked_vendor_purchase_orders(payment_entry)
        self.assertIn(po.name, linked_pos)

    def test_attach_payment_proof_to_po(self):
        po = self._create_test_po()
        pe_doc = frappe._dict({"name": "ACC-PAY-TEST-ATTACH"})
        valid_pdf = frappe.get_pdf("<html><body><h1>Test Payment Proof</h1></body></html>")

        attach_payment_proof_to_po(po, pe_doc, valid_pdf)

        files = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Vendor Purchase Order",
                "attached_to_name": po.name,
                "file_name": ["like", f"Payment_Proof_{pe_doc.name}%"],
            },
            fields=["name", "file_name"]
        )
        self.assertTrue(len(files) > 0)
        self.assertTrue(files[0].file_name.startswith(f"Payment_Proof_{pe_doc.name}"))
        if hasattr(self, "created_files"):
            self.created_files.extend([f.name for f in files])

    def test_recalculate_po_payment_status_fully_paid(self):
        po = self._create_test_po()
        # Create paid purchase invoice record in database
        invoice = frappe.new_doc("Purchase Invoice")
        invoice.company = self.test_company
        invoice.supplier = self.test_vendor
        invoice.vendor_purchase_order = po.name
        invoice.bill_no = f"INV-{frappe.generate_hash(length=6)}"
        invoice.bill_date = nowdate()
        invoice.grand_total = 1000.0
        invoice.outstanding_amount = 0.0
        invoice.docstatus = 1
        invoice.flags.ignore_mandatory = True
        invoice.flags.ignore_validate = True
        invoice.db_insert()
        if hasattr(self, "created_invoices"):
            self.created_invoices.append(invoice.name)

        recalculate_po_payment_status(po.name)

        po.reload()
        self.assertEqual(po.payment_workflow_status, "Paid")
        self.assertEqual(po.payment_status, "Fully Paid")
        self.assertEqual(po.payment_fully_paid, 1)
        self.assertEqual(po.payment_pending, 0)
        self.assertEqual(flt(po.balance_due), 0.0)

    def test_dispatch_procurement_notification(self):
        po = self._create_test_po()
        pe_doc = frappe._dict({
            "name": "ACC-PAY-TEST-NOTIF",
            "reference_no": "UTR12345678",
            "posting_date": nowdate(),
            "party": self.test_vendor,
            "party_name": "Action Construction Equipment",
        })

        with patch("frappe.publish_realtime") as mock_realtime, patch("frappe.sendmail") as mock_sendmail:
            dispatch_procurement_notification(po, pe_doc, "USD", "1,000.00", b"%PDF-dummy")
            self.assertTrue(mock_realtime.called)
            self.assertTrue(mock_sendmail.called)

        # Confirm Notification Log was created
        notifs = frappe.get_all(
            "Notification Log",
            filters={
                "document_type": "Vendor Purchase Order",
                "document_name": po.name,
            },
            fields=["name", "subject", "for_user"]
        )
        self.assertTrue(len(notifs) > 0)
        self.assertIn("Payment Executed", notifs[0].subject)

    def test_dispatch_finance_audit_notification(self):
        po = self._create_test_po()
        pe_doc = frappe._dict({
            "name": "ACC-PAY-TEST-AUDIT",
            "reference_no": "UTR87654321",
            "posting_date": nowdate(),
            "party": self.test_vendor,
            "party_name": "Action Construction Equipment",
        })

        with patch("frappe.sendmail") as mock_sendmail:
            dispatch_finance_audit_notification(po, pe_doc, "USD", "1,000.00")
            self.assertTrue(mock_sendmail.called)
            args, kwargs = mock_sendmail.call_args
            self.assertIn("Audit Alert", kwargs.get("subject", ""))

    def test_end_to_end_on_payment_entry_submit(self):
        po = self._create_test_po()

        invoice = frappe.new_doc("Purchase Invoice")
        invoice.company = self.test_company
        invoice.supplier = self.test_vendor
        invoice.vendor_purchase_order = po.name
        invoice.bill_no = f"INV-{frappe.generate_hash(length=6)}"
        invoice.bill_date = nowdate()
        invoice.grand_total = 1000.0
        invoice.outstanding_amount = 0.0
        invoice.docstatus = 1
        invoice.flags.ignore_mandatory = True
        invoice.flags.ignore_validate = True
        invoice.db_insert()
        if hasattr(self, "created_invoices"):
            self.created_invoices.append(invoice.name)

        pe_doc = frappe._dict({
            "doctype": "Payment Entry",
            "name": "ACC-PAY-E2E-001",
            "posting_date": nowdate(),
            "reference_no": "UTR-E2E-999",
            "party_type": "Supplier",
            "party": self.test_vendor,
            "party_name": "Action Construction Equipment",
            "paid_amount": 1000.0,
            "paid_to_account_currency": "USD",
            "company": self.test_company,
            "references": [
                frappe._dict({
                    "reference_doctype": "Purchase Invoice",
                    "reference_name": invoice.name,
                    "total_amount": 1000.0,
                    "allocated_amount": 1000.0,
                    "outstanding_amount": 0.0,
                })
            ]
        })

        with patch("frappe.sendmail"), patch("frappe.publish_realtime"):
            on_payment_entry_submit(pe_doc)

        po.reload()
        # Verify PO metrics updated
        self.assertEqual(po.payment_workflow_status, "Paid")
        self.assertEqual(po.payment_status, "Fully Paid")
        self.assertEqual(po.payment_fully_paid, 1)

        # Verify PDF attachment
        files = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Vendor Purchase Order",
                "attached_to_name": po.name,
                "file_name": ["like", f"Payment_Proof_{pe_doc.name}%"],
            }
        )
        self.assertEqual(len(files), 1)
        if hasattr(self, "created_files"):
            self.created_files.extend([f.name for f in files])

    def test_payment_tracking_icon_role_visibility(self):
        """Verify that Payment Tracking desktop icon & workspace sidebar are restricted to finance roles in bootinfo"""
        from sarveksha_erp.boot import extend_bootinfo

        # Use standard provisioned Sarveksha users
        finance_user = "finance_manager1@sarveksha.com"
        procurement_user = "vendor_manager@sarveksha.com"

        # Test as Finance User (Accounts Manager)
        frappe.set_user(finance_user)
        bootinfo_finance = frappe._dict({
            "desktop_icons": [{"label": "Payment Tracking", "module": "Payment Tracking"}],
            "workspace_sidebar_item": [{"title": "Payment Tracking"}],
            "allowed_workspaces": [{"title": "Payment Tracking"}],
        })
        extend_bootinfo(bootinfo_finance)
        self.assertTrue(any(i.get("label") == "Payment Tracking" for i in bootinfo_finance.desktop_icons))
        self.assertTrue(any(i.get("title") == "Payment Tracking" for i in bootinfo_finance.workspace_sidebar_item))

        # Test as Procurement User (PO Generator only)
        frappe.set_user(procurement_user)
        bootinfo_proc = frappe._dict({
            "desktop_icons": [{"label": "Payment Tracking", "module": "Payment Tracking"}],
            "workspace_sidebar_item": [{"title": "Payment Tracking"}],
            "allowed_workspaces": [{"title": "Payment Tracking"}],
        })
        extend_bootinfo(bootinfo_proc)
        self.assertFalse(any(i.get("label") == "Payment Tracking" for i in bootinfo_proc.desktop_icons))
        self.assertFalse(any(i.get("title") == "Payment Tracking" for i in bootinfo_proc.workspace_sidebar_item))
        self.assertFalse(any(i.get("title") == "Payment Tracking" for i in bootinfo_proc.allowed_workspaces))

        # Reset user
        frappe.set_user("Administrator")

    def test_payment_entry_defaults_and_mode_accounts(self):
        """Verify Mode of Payment accounts and default print format are properly configured."""
        from sarveksha_erp.payment_tracking.events.payment_entry_events import get_mode_of_payment_account

        # Verify Credit Card mode has default account for Sarveksha company
        cc_account = get_mode_of_payment_account("Credit Card", "Sarveksha Realty and Inframine LLP")
        self.assertTrue(bool(cc_account))
        self.assertTrue(frappe.db.exists("Account", cc_account))

        # Verify Wire Transfer mode
        wire_account = get_mode_of_payment_account("Wire Transfer", "Sarveksha Realty and Inframine LLP")
        self.assertTrue(bool(wire_account))

        # Verify Cash mode
        cash_account = get_mode_of_payment_account("Cash", "Sarveksha Realty and Inframine LLP")
        self.assertTrue(bool(cash_account))

        # Verify Default Print Format is Payment Receipt Proof
        print_fmt = frappe.db.get_value("Property Setter", {"doc_type": "Payment Entry", "property": "default_print_format"}, "value")
        self.assertEqual(print_fmt, "Payment Receipt Proof")

    def test_payment_entry_workflow_maker_checker(self):
        """Acceptance Criteria 1 & 2:
        - Accounts Clerks see 'Send for Approval', cannot directly submit.
        - Accounts Managers can review payments and choose 'Approve & Submit' or 'Reject'.
        """
        from frappe.model.workflow import apply_workflow

        clerk_user = "finance_clerk1@sarveksha.com"
        manager_user = "finance_manager1@sarveksha.com"
        company = "Sarveksha Realty and Inframine LLP"
        supplier = self.test_vendor

        frappe.set_user(clerk_user)
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.company = company
        pe.party_type = "Supplier"
        pe.party = supplier
        pe.paid_amount = 500
        pe.received_amount = 500
        pe.paid_from = frappe.db.get_value("Company", company, "default_bank_account")
        pe.paid_to = frappe.db.get_value("Account", {"company": company, "account_type": "Payable"}, "name")
        pe.reference_no = f"UTR-MC-{frappe.generate_hash(length=6)}"
        pe.reference_date = nowdate()
        pe.flags.ignore_mandatory = True
        pe.flags.ignore_validate = True
        pe.insert()
        if hasattr(self, "created_pes"):
            self.created_pes.append(pe.name)

        self.assertEqual(pe.workflow_state, "Draft")
        self.assertEqual(pe.docstatus, 0)

        # 1. Accounts Clerk CANNOT submit directly
        with self.assertRaises((frappe.PermissionError, frappe.ValidationError)):
            pe.submit()

        # 2. Accounts Clerk applies 'Send for Approval' -> Pending Approval
        apply_workflow(pe, "Send for Approval")
        pe.reload()
        self.assertEqual(pe.workflow_state, "Pending Approval")
        self.assertEqual(pe.docstatus, 0)

        # 3. Accounts Manager rejects -> moves back to Draft
        frappe.set_user(manager_user)
        apply_workflow(pe, "Reject")
        pe.reload()
        self.assertEqual(pe.workflow_state, "Draft")

        # 4. Accounts Clerk resubmits for approval
        frappe.set_user(clerk_user)
        apply_workflow(pe, "Send for Approval")
        pe.reload()
        self.assertEqual(pe.workflow_state, "Pending Approval")

        # 5. Accounts Manager approves & submits -> moves to Completed and docstatus = 1
        frappe.set_user(manager_user)
        with patch("frappe.sendmail"), patch("frappe.publish_realtime"), patch("erpnext.accounts.doctype.payment_entry.payment_entry.PaymentEntry.make_gl_entries"):
            apply_workflow(pe, "Approve & Submit")
        pe.reload()
        self.assertEqual(pe.workflow_state, "Completed")
        self.assertEqual(pe.docstatus, 1)

        frappe.set_user("Administrator")

    def test_server_side_api_guard_blocks_direct_submit(self):
        """Requirement: Server-side API guard prevents users without Accounts Manager
        from making direct REST API calls to submit payment records, and prevents bypassing workflow.
        """
        clerk_user = "finance_clerk1@sarveksha.com"
        manager_user = "finance_manager1@sarveksha.com"
        company = "Sarveksha Realty and Inframine LLP"
        supplier = self.test_vendor

        # Clerk attempting direct submit
        frappe.set_user(clerk_user)
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.company = company
        pe.party_type = "Supplier"
        pe.party = supplier
        pe.paid_amount = 200
        pe.received_amount = 200
        pe.paid_from = frappe.db.get_value("Company", company, "default_bank_account")
        pe.paid_to = frappe.db.get_value("Account", {"company": company, "account_type": "Payable"}, "name")
        pe.reference_no = f"UTR-GUARD-{frappe.generate_hash(length=6)}"
        pe.reference_date = nowdate()
        pe.flags.ignore_mandatory = True
        pe.flags.ignore_validate = True
        pe.insert()
        if hasattr(self, "created_pes"):
            self.created_pes.append(pe.name)

        with self.assertRaises(frappe.PermissionError):
            pe.submit()

        # Manager attempting direct submit of a Draft payment (bypassing workflow)
        frappe.set_user(manager_user)
        with self.assertRaises(frappe.ValidationError):
            pe.submit()

        frappe.set_user("Administrator")

    def test_standard_payment_terms_templates_configured(self):
        """Requirement: Verify standard payment terms templates exist and are valid."""
        required_templates = ["100% Advance", "30% Advance - 70% Against BL", "Net 30 Days"]
        for tmpl_name in required_templates:
            self.assertTrue(frappe.db.exists("Payment Terms Template", tmpl_name), f"Missing template: {tmpl_name}")
            tmpl = frappe.get_doc("Payment Terms Template", tmpl_name)
            total_portion = sum(flt(row.invoice_portion) for row in tmpl.terms)
            self.assertAlmostEqual(total_portion, 100.0, places=1, msg=f"{tmpl_name} portions must sum to 100%")

    def test_automatic_po_payment_status_sync(self):
        """Acceptance Criteria 3:
        Submitting a payment immediately marks the linked Purchase Order as Paid or Partially Paid and notifies PO creator.
        """
        from sarveksha_erp.payment_tracking.events.payment_entry_events import on_payment_submit

        po = self._create_test_po()
        po.grand_total = 1000.0
        po.db_update()

        # 1. Partial payment: $400 out of $1000
        invoice = frappe.new_doc("Purchase Invoice")
        invoice.company = self.test_company
        invoice.supplier = self.test_vendor
        invoice.vendor_purchase_order = po.name
        invoice.bill_no = f"INV-PARTIAL-{frappe.generate_hash(length=4)}"
        invoice.bill_date = nowdate()
        invoice.grand_total = 1000.0
        invoice.outstanding_amount = 600.0
        invoice.docstatus = 1
        invoice.flags.ignore_mandatory = True
        invoice.flags.ignore_validate = True
        invoice.db_insert()
        if hasattr(self, "created_invoices"):
            self.created_invoices.append(invoice.name)

        pe_doc = frappe._dict({
            "doctype": "Payment Entry",
            "name": f"ACC-PAY-PARTIAL-{frappe.generate_hash(length=4)}",
            "posting_date": nowdate(),
            "reference_no": "UTR-PARTIAL-1",
            "party_type": "Supplier",
            "party": self.test_vendor,
            "party_name": "Action Construction Equipment",
            "paid_amount": 400.0,
            "paid_to_account_currency": "USD",
            "company": self.test_company,
            "references": [
                frappe._dict({
                    "reference_doctype": "Purchase Invoice",
                    "reference_name": invoice.name,
                    "total_amount": 1000.0,
                    "allocated_amount": 400.0,
                    "outstanding_amount": 600.0,
                })
            ]
        })

        with patch("frappe.sendmail") as mock_mail, patch("frappe.publish_realtime") as mock_alert:
            on_payment_submit(pe_doc)
            self.assertTrue(mock_mail.called)
            self.assertTrue(mock_alert.called)

        po.reload()
        self.assertEqual(po.payment_tracking_status, "Partially Paid")
        self.assertEqual(po.payment_workflow_status, "Partially Paid")

        # 2. Full payment: remaining $600 paid (outstanding = 0)
        invoice.outstanding_amount = 0.0
        invoice.db_update()

        pe_doc_full = frappe._dict({
            "doctype": "Payment Entry",
            "name": f"ACC-PAY-FULL-{frappe.generate_hash(length=4)}",
            "posting_date": nowdate(),
            "reference_no": "UTR-FULL-2",
            "party_type": "Supplier",
            "party": self.test_vendor,
            "party_name": "Action Construction Equipment",
            "paid_amount": 600.0,
            "paid_to_account_currency": "USD",
            "company": self.test_company,
            "references": [
                frappe._dict({
                    "reference_doctype": "Purchase Invoice",
                    "reference_name": invoice.name,
                    "total_amount": 1000.0,
                    "allocated_amount": 600.0,
                    "outstanding_amount": 0.0,
                })
            ]
        })

        with patch("frappe.sendmail") as mock_mail, patch("frappe.publish_realtime") as mock_alert:
            on_payment_submit(pe_doc_full)
            self.assertTrue(mock_mail.called)
            self.assertTrue(mock_alert.called)

        po.reload()
        self.assertEqual(po.payment_tracking_status, "Paid")
        self.assertEqual(po.payment_workflow_status, "Paid")
        self.assertEqual(po.payment_fully_paid, 1)



def run_test_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPaymentTracking)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise Exception(f"Tests failed: {len(res.failures)} failures, {len(res.errors)} errors")
    print("\n--- ALL TESTS PASSED SUCCESSFULLY ---")

