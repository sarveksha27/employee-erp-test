# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.utils import add_days, flt, getdate, nowdate
from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order import (
    get_po_generated_amount_summary,
)


class TestPONumberAndSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure test company exists
        if not frappe.db.exists("Company", "_Test Company PO Year"):
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company PO Year"
            comp.abbr = "_TCPY"
            comp.default_currency = "INR"
            comp.country = "India"
            comp.insert(ignore_permissions=True)

        # Ensure test supplier exists
        if not frappe.db.exists("Supplier", "_Test Supplier PO Year"):
            supp = frappe.new_doc("Supplier")
            supp.supplier_name = "_Test Supplier PO Year"
            supp.supplier_group = "All Supplier Groups"
            supp.insert(ignore_permissions=True)

        frappe.db.commit()

    def test_po_number_includes_current_year(self):
        """Verify that newly generated PO number automatically includes current year."""
        current_year = str(getdate(nowdate()).year)

        po = frappe.new_doc("Vendor Purchase Order")
        po.po_type = "Vendor PO"
        po.company = "_Test Company PO Year"
        po.vendor = "_Test Supplier PO Year"
        po.quantity = 1.0
        po.rate = 1000.0
        po.exchange_rate = 1.0
        po.currency = "INR"
        po.workflow_state = "Draft"
        po.flags.ignore_mandatory = True
        po.flags.ignore_validate = True
        po.insert(ignore_permissions=True)

        try:
            self.assertIsNotNone(po.name)
            self.assertIn(current_year, po.name)
            self.assertTrue(po.name.startswith(f"SRIPO-{current_year}-"))
        finally:
            frappe.db.rollback()

    def test_po_number_includes_specific_po_date_year(self):
        """Verify that PO with specific po_date derives year from po_date."""
        target_date = "2025-06-15"
        expected_year = "2025"

        po = frappe.new_doc("Vendor Purchase Order")
        po.po_type = "Vendor PO"
        po.company = "_Test Company PO Year"
        po.vendor = "_Test Supplier PO Year"
        po.po_date = target_date
        po.quantity = 2.0
        po.rate = 500.0
        po.exchange_rate = 1.0
        po.currency = "INR"
        po.workflow_state = "Draft"
        po.flags.ignore_mandatory = True
        po.flags.ignore_validate = True
        po.insert(ignore_permissions=True)

        try:
            self.assertIsNotNone(po.name)
            self.assertIn(expected_year, po.name)
            self.assertTrue(po.name.startswith(f"SRIPO-{expected_year}-"))
        finally:
            frappe.db.rollback()

    def test_get_po_generated_amount_summary_aggregated_metrics(self):
        """Verify get_po_generated_amount_summary aggregates totals, currency, and status accurately."""
        # Query summary for 2026
        res = get_po_generated_amount_summary(from_date="2026-01-01", to_date="2026-12-31")

        self.assertIn("period", res)
        self.assertEqual(res["period"]["from_date"], "2026-01-01")
        self.assertEqual(res["period"]["to_date"], "2026-12-31")
        self.assertIn("total_pos", res)
        self.assertIn("total_amount", res)
        self.assertIn("by_currency", res)
        self.assertIn("by_status", res)
        self.assertIn("by_vendor", res)
        self.assertIn("by_company", res)
        self.assertIn("pos", res)

        # Totals in by_currency should match total_amount
        currency_sum = sum(data["total_amount"] for data in res["by_currency"].values())
        self.assertAlmostEqual(currency_sum, res["total_amount"], places=2)

    def test_get_po_generated_amount_summary_empty_period(self):
        """Verify summary returns 0 totals for periods with no POs without error."""
        res = get_po_generated_amount_summary(from_date="2010-01-01", to_date="2010-01-31")
        self.assertEqual(res["total_pos"], 0)
        self.assertEqual(res["total_amount"], 0.0)
        self.assertEqual(len(res["pos"]), 0)
        self.assertEqual(len(res["by_currency"]), 0)
        self.assertEqual(len(res["by_status"]), 0)

    def test_get_po_generated_amount_summary_invalid_date_range(self):
        """Verify exception is raised if from_date is after to_date."""
        with self.assertRaises(frappe.ValidationError):
            get_po_generated_amount_summary(from_date="2026-12-31", to_date="2026-01-01")
