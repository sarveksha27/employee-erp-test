# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

"""
Unit tests for Member 2 (Manik) — Supplier Profile Linking and Automated PO Ingestion:
    - test_supplier_terms_auto_pull: Mock vendor with 30/70 terms; assert PO inherits template on vendor selection.
    - test_schedule_recalculation_on_rate_change: Set grand total to 100,000; assert milestones are 30,000 and 70,000.
    - test_paise_rounding_reconciliation: Set grand total to 10,000.33 with 30/70 split; assert Milestone 1 is 3,000.10 and Milestone 2 is 7,000.23 (sum exactly equals 10,000.33).
    - test_forwarding_guard_blocks_empty_schedule: Assert approving a PO without payment terms raises validation error.
"""

import datetime
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from sarveksha_erp.payment_tracking.vpo_payment_terms import (
    _safe_add_months,
    calculate_vpo_payment_schedule,
    get_supplier_default_payment_terms,
    validate_vpo_payment_schedule,
)


def _make_schedule_row(**kwargs):
    """Return a SimpleNamespace that behaves like a Payment Schedule row."""
    defaults = {
        "payment_term": "Advance",
        "description": "",
        "invoice_portion": 30.0,
        "credit_days": 0,
        "credit_months": 0,
        "due_date_based_on": "Day(s) after invoice date",
        "payment_amount": 0.0,
        "paid_amount": 0.0,
        "outstanding": 0.0,
        "due_date": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_doc(grand_total, schedule_rows, payment_terms_template=None, po_date=None, workflow_state="Draft"):
    """Return a minimal mock VPO document."""
    doc = MagicMock()
    doc.grand_total = grand_total
    doc.po_date = po_date or "2026-01-15"
    doc.payment_terms_template = payment_terms_template
    doc.payment_schedule = schedule_rows
    doc.workflow_state = workflow_state
    doc.get = lambda key, default=None: (
        schedule_rows if key == "payment_schedule" else default
    )
    return doc


class TestVPOPaymentTerms(unittest.TestCase):
    """Core acceptance test cases specified for Member 2 (Manik)."""

    @patch("frappe.db.get_value")
    @patch("frappe.db.exists")
    @patch("frappe.get_doc")
    def test_supplier_terms_auto_pull(self, mock_get_doc, mock_exists, mock_get_value):
        """
        Mock vendor with 30/70 terms; assert PO inherits template on vendor selection.
        """
        # Mock Supplier lookup returning payment_terms template
        mock_get_value.return_value = {
            "payment_terms": "Standard Vendor Terms - 30/70",
            "supplier_group": "All Supplier Groups",
        }
        mock_exists.return_value = True

        # Mock template document with 30/70 terms
        mock_template = MagicMock()
        mock_template.name = "Standard Vendor Terms - 30/70"
        mock_template.terms = [
            SimpleNamespace(
                payment_term="Advance 30%",
                description="30% Advance on Order",
                invoice_portion=30.0,
                credit_days=0,
                credit_months=0,
                due_date_based_on="Day(s) after invoice date",
            ),
            SimpleNamespace(
                payment_term="Balance 70%",
                description="70% Balance on Delivery",
                invoice_portion=70.0,
                credit_days=30,
                credit_months=0,
                due_date_based_on="Day(s) after invoice date",
            ),
        ]
        mock_get_doc.return_value = mock_template

        res = get_supplier_default_payment_terms("Mock Vendor 30-70")
        self.assertEqual(res.get("payment_terms_template"), "Standard Vendor Terms - 30/70")
        terms = res.get("terms", [])
        self.assertEqual(len(terms), 2)
        self.assertEqual(terms[0]["payment_term"], "Advance 30%")
        self.assertEqual(terms[0]["invoice_portion"], 30.0)
        self.assertEqual(terms[0]["credit_days"], 0)
        self.assertEqual(terms[1]["payment_term"], "Balance 70%")
        self.assertEqual(terms[1]["invoice_portion"], 70.0)
        self.assertEqual(terms[1]["credit_days"], 30)

    @patch("frappe.db.get_value")
    @patch("frappe.db.exists")
    @patch("frappe.get_doc")
    def test_supplier_group_fallback(self, mock_get_doc, mock_exists, mock_get_value):
        """
        When Supplier has no direct payment_terms, fallback to Supplier Group.
        """
        def db_get_value_side_effect(doctype, name, fieldname, as_dict=False):
            if doctype == "Supplier":
                return {"payment_terms": None, "supplier_group": "Machinery"}
            elif doctype == "Supplier Group":
                return "Net 60 Days"
            return None

        mock_get_value.side_effect = db_get_value_side_effect
        mock_exists.return_value = True

        mock_template = MagicMock()
        mock_template.name = "Net 60 Days"
        mock_template.terms = [
            SimpleNamespace(
                payment_term="Net 60 Days",
                description="Net 60 Days",
                invoice_portion=100.0,
                credit_days=60,
                credit_months=0,
                due_date_based_on="Day(s) after invoice date",
            )
        ]
        mock_get_doc.return_value = mock_template

        res = get_supplier_default_payment_terms("Supplier Without Direct Terms")
        self.assertEqual(res.get("payment_terms_template"), "Net 60 Days")
        self.assertEqual(len(res.get("terms", [])), 1)
        self.assertEqual(res["terms"][0]["credit_days"], 60)

    def test_schedule_recalculation_on_rate_change(self):
        """
        Set grand total to 100,000; assert milestones are 30,000 and 70,000.
        """
        row1 = _make_schedule_row(payment_term="Advance 30%", invoice_portion=30.0, credit_days=0)
        row2 = _make_schedule_row(payment_term="Balance 70%", invoice_portion=70.0, credit_days=30)
        doc = _make_doc(grand_total=100000.0, schedule_rows=[row1, row2], po_date="2026-03-01")

        calculate_vpo_payment_schedule(doc)

        self.assertEqual(row1.payment_amount, 30000.00)
        self.assertEqual(row2.payment_amount, 70000.00)
        self.assertEqual(row1.outstanding, 30000.00)
        self.assertEqual(row2.outstanding, 70000.00)
        self.assertEqual(row1.payment_amount + row2.payment_amount, 100000.00)

    def test_paise_rounding_reconciliation(self):
        """
        Set grand total to 10,000.33 with 30/70 split; assert Milestone 1 is 3,000.10
        and Milestone 2 is 7,000.23 (sum exactly equals 10,000.33).
        """
        row1 = _make_schedule_row(payment_term="Advance 30%", invoice_portion=30.0, credit_days=0)
        row2 = _make_schedule_row(payment_term="Balance 70%", invoice_portion=70.0, credit_days=30)
        doc = _make_doc(grand_total=10000.33, schedule_rows=[row1, row2], po_date="2026-03-01")

        calculate_vpo_payment_schedule(doc)

        self.assertEqual(row1.payment_amount, 3000.10)
        self.assertEqual(row2.payment_amount, 7000.23)
        self.assertEqual(round(row1.payment_amount + row2.payment_amount, 2), 10000.33)
        self.assertEqual(row1.outstanding, 3000.10)
        self.assertEqual(row2.outstanding, 7000.23)

    def test_forwarding_guard_blocks_empty_schedule(self):
        """
        Assert approving a PO without payment terms raises validation error.
        """
        # Case 1: missing payment_terms_template
        doc_no_template = _make_doc(
            grand_total=10000.0,
            schedule_rows=[],
            payment_terms_template=None,
            workflow_state="Approved",
        )
        with self.assertRaises(frappe.ValidationError):
            validate_vpo_payment_schedule(doc_no_template)

        # Case 2: has template but payment_schedule child table is empty
        doc_empty_schedule = _make_doc(
            grand_total=10000.0,
            schedule_rows=[],
            payment_terms_template="Standard Vendor Terms - 30/70",
            workflow_state="Approved",
        )
        with self.assertRaises(frappe.ValidationError):
            validate_vpo_payment_schedule(doc_empty_schedule)

        # Case 3: schedule total does not equal grand_total
        row1 = _make_schedule_row(payment_amount=3000.00)
        doc_unbalanced = _make_doc(
            grand_total=10000.0,
            schedule_rows=[row1],
            payment_terms_template="Standard Vendor Terms - 30/70",
            workflow_state="Approved",
        )
        with self.assertRaises(frappe.ValidationError):
            validate_vpo_payment_schedule(doc_unbalanced)

    def test_balanced_schedule_passes_validation(self):
        """Balanced schedule must pass validation cleanly."""
        row1 = _make_schedule_row(payment_amount=3000.10)
        row2 = _make_schedule_row(payment_amount=7000.23)
        doc = _make_doc(
            grand_total=10000.33,
            schedule_rows=[row1, row2],
            payment_terms_template="Standard Vendor Terms - 30/70",
            workflow_state="Approved",
        )
        # Should not raise
        validate_vpo_payment_schedule(doc)

    def test_paise_tolerance_passes_validation(self):
        """Difference within 0.01 tolerance must pass validation without error."""
        row = _make_schedule_row(payment_amount=9999.99)
        doc = _make_doc(
            grand_total=10000.00,
            schedule_rows=[row],
            payment_terms_template="Net 30 Days",
            workflow_state="Approved",
        )
        # 10000.00 - 9999.99 == 0.01 tolerance
        validate_vpo_payment_schedule(doc)

    def test_due_date_calculation(self):
        """Due dates are calculated based on credit_days and po_date."""
        row = _make_schedule_row(
            invoice_portion=100.0,
            credit_days=30,
            due_date_based_on="Day(s) after invoice date",
        )
        doc = _make_doc(grand_total=5000.0, schedule_rows=[row], po_date="2026-03-01")
        calculate_vpo_payment_schedule(doc)
        self.assertEqual(row.due_date, datetime.date(2026, 3, 31))

    def test_safe_add_months_month_end(self):
        """Jan 31 + 1 month clamps to Feb 28 in non-leap year."""
        res = _safe_add_months("2026-01-31", 1)
        self.assertEqual(res, datetime.date(2026, 2, 28))


if __name__ == "__main__":
    unittest.main()
