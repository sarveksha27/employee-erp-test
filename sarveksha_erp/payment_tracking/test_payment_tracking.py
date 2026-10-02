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
def mock_get_fiscal_years(date=None, company=None, boolean=False):
    fys = frappe.db.get_all(
        "Fiscal Year",
        fields=["name", "year_start_date", "year_end_date"],
        filters={"disabled": 0},
        order_by="year_start_date desc",
    )
    if boolean:
        return bool(fys)
    return fys
erpnext.accounts.utils.get_fiscal_years = mock_get_fiscal_years
erpnext.accounts.utils._get_fiscal_years = mock_get_fiscal_years

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
        cls.test_company = frappe.db.get_value("Company", {}, "name") or "Sarveksha BSTP SAS"
        cls.test_vendor = frappe.db.get_value("Supplier", {}, "name") or "Action Construction Equipment"

    def _create_test_po(self):
        po = frappe.new_doc("Vendor Purchase Order")
        po.company = self.test_company
        po.vendor = self.test_vendor
        po.quantity = 1.0
        po.rate = 1000.0
        po.exchange_rate = 1.0
        po.workflow_state = "Draft"
        po.prepared_by = "Administrator"
        po.save(ignore_permissions=True)
        po.workflow_state = "Approved"
        po.status = "Approved"
        po.docstatus = 1
        po.payment_workflow_status = "Forwarded for Payment"
        po.payment_forwarded_on = frappe.utils.now_datetime()
        po.db_update()
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
                "file_name": f"Payment_Proof_{pe_doc.name}.pdf",
            },
            fields=["name", "file_name"]
        )
        self.assertTrue(len(files) > 0)
        self.assertEqual(files[0].file_name, f"Payment_Proof_{pe_doc.name}.pdf")

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
                "file_name": f"Payment_Proof_{pe_doc.name}.pdf",
            }
        )
        self.assertEqual(len(files), 1)

    def test_payment_tracking_icon_role_visibility(self):
        """Verify that Payment Tracking desktop icon & workspace sidebar are restricted to finance roles in bootinfo"""
        from sarveksha_erp.boot import extend_bootinfo

        # Create or fetch test users
        if not frappe.db.exists("User", "finance_user_test@example.com"):
            u1 = frappe.get_doc({
                "doctype": "User",
                "email": "finance_user_test@example.com",
                "first_name": "Finance",
                "last_name": "User",
                "send_welcome_email": 0,
            }).insert(ignore_permissions=True)
            u1.add_roles("Accounts Manager")
        
        if not frappe.db.exists("User", "procurement_user_test@example.com"):
            u2 = frappe.get_doc({
                "doctype": "User",
                "email": "procurement_user_test@example.com",
                "first_name": "Procurement",
                "last_name": "User",
                "send_welcome_email": 0,
            }).insert(ignore_permissions=True)
            u2.add_roles("PO Generator")

        # Test as Finance User (Accounts Manager)
        frappe.set_user("finance_user_test@example.com")
        bootinfo_finance = frappe._dict({
            "desktop_icons": [{"label": "Payment Tracking", "module": "Payment Tracking"}],
            "workspace_sidebar_item": [{"title": "Payment Tracking"}],
            "allowed_workspaces": [{"title": "Payment Tracking"}],
        })
        extend_bootinfo(bootinfo_finance)
        self.assertTrue(any(i.get("label") == "Payment Tracking" for i in bootinfo_finance.desktop_icons))
        self.assertTrue(any(i.get("title") == "Payment Tracking" for i in bootinfo_finance.workspace_sidebar_item))

        # Test as Procurement User (PO Generator only)
        frappe.set_user("procurement_user_test@example.com")
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


def run_test_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPaymentTracking)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        raise Exception(f"Tests failed: {len(res.failures)} failures, {len(res.errors)} errors")
    print("\n--- ALL TESTS PASSED SUCCESSFULLY ---")

