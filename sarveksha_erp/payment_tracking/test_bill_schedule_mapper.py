import unittest
import frappe
from frappe.utils import add_days, flt, getdate, nowdate
from sarveksha_erp.payment_tracking.bill_schedule_mapper import (
    calculate_due_date_from_term,
    make_purchase_invoice_from_po,
    reallocate_invoice_milestone_schedule,
    validate_invoice_milestone_schedule_before_submit,
)


class TestBillScheduleMapper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure test company exists
        if not frappe.db.exists("Company", "_Test Company PO"):
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company PO"
            comp.abbr = "_TCPO"
            comp.default_currency = "INR"
            comp.country = "India"
            comp.insert(ignore_permissions=True)

        # Ensure test supplier exists
        if not frappe.db.exists("Supplier", "_Test Supplier PO"):
            supp = frappe.new_doc("Supplier")
            supp.supplier_name = "_Test Supplier PO"
            supp.supplier_group = "All Supplier Groups"
            supp.insert(ignore_permissions=True)

        # Ensure test item exists
        if not frappe.db.exists("Item", "_Test Item PO"):
            item = frappe.new_doc("Item")
            item.item_code = "_Test Item PO"
            item.item_name = "_Test Item PO"
            item.item_group = "All Item Groups"
            item.stock_uom = "Nos"
            item.is_stock_item = 0
            item.insert(ignore_permissions=True)

    def test_due_date_derivation(self):
        """Test calculation of due dates with credit days and month end logic."""
        base_date = getdate("2026-10-15")

        # Mock term with 30 credit days
        term_mock = frappe._dict({
            "due_date_based_on": "Day(s) after invoice date",
            "credit_days": 30,
            "credit_months": 0,
        })
        res = calculate_due_date_from_term(term_mock, base_date)
        self.assertEqual(res, getdate("2026-11-14"))

        # Mock term after end of invoice month
        term_mock_month_end = frappe._dict({
            "due_date_based_on": "Day(s) after end of the invoice month",
            "credit_days": 15,
            "credit_months": 0,
        })
        res_me = calculate_due_date_from_term(term_mock_month_end, base_date)
        # October ends on 31, + 15 days = 2026-11-15
        self.assertEqual(res_me, getdate("2026-11-15"))

    def test_milestone_transfer_from_po(self):
        """Test creating draft Purchase Invoice from Vendor Purchase Order with milestone schedule."""
        po = frappe.get_doc("Vendor Purchase Order", "SRIPO-0006")

        # Set milestone schedule on PO object
        po.payment_schedule = [
            frappe._dict({
                "payment_term": "30% Advance",
                "description": "30% Advance Payment",
                "invoice_portion": 30.0,
                "payment_amount": 3000.0,
                "due_date": nowdate()
            }),
            frappe._dict({
                "payment_term": "70% Against BL",
                "description": "70% Balance on Delivery",
                "invoice_portion": 70.0,
                "payment_amount": 7000.0,
                "due_date": add_days(nowdate(), 30)
            })
        ]

        # Attach to get_doc so mapper receives schedule
        orig_get_doc = frappe.get_doc
        def patched_get_doc(*args, **kwargs):
            doc = orig_get_doc(*args, **kwargs)
            if len(args) >= 2 and args[0] == "Vendor Purchase Order" and args[1] == po.name:
                doc.payment_schedule = po.payment_schedule
            return doc

        frappe.get_doc = patched_get_doc
        try:
            # Map to Purchase Invoice
            inv = make_purchase_invoice_from_po(po.name)
            self.assertEqual(inv.custom_vendor_purchase_order, po.name)
            self.assertEqual(inv.supplier, po.get("supplier") or po.get("vendor"))
            self.assertEqual(len(inv.payment_schedule), 2)
            expected_30 = flt(inv.grand_total * 0.3, 2)
            expected_70 = flt(inv.grand_total - expected_30, 2)
            self.assertEqual(inv.payment_schedule[0].payment_amount, expected_30)
            self.assertEqual(inv.payment_schedule[1].payment_amount, expected_70)
            self.assertEqual(inv.payment_schedule[0].outstanding, expected_30)
            self.assertEqual(inv.payment_schedule[0].paid_amount, 0.0)
        finally:
            frappe.get_doc = orig_get_doc

    def test_tax_reallocation(self):
        """Test reallocation of schedule when invoice grand_total includes taxes or charges."""
        inv = frappe._dict({
            "grand_total": 11800.0,
            "rounded_total": 11800.0,
            "payment_schedule": [
                frappe._dict({"invoice_portion": 33.3333, "payment_amount": 0.0, "paid_amount": 0.0, "outstanding": 0.0}),
                frappe._dict({"invoice_portion": 33.3333, "payment_amount": 0.0, "paid_amount": 0.0, "outstanding": 0.0}),
                frappe._dict({"invoice_portion": 33.3334, "payment_amount": 0.0, "paid_amount": 0.0, "outstanding": 0.0}),
            ]
        })
        reallocate_invoice_milestone_schedule(inv)
        total_allocated = sum(r.payment_amount for r in inv.payment_schedule)
        self.assertEqual(round(total_allocated, 2), 11800.0)
        # Verify 3rd row absorbs any 1-paisa rounding difference exactly
        self.assertEqual(round(sum(r.outstanding for r in inv.payment_schedule), 2), 11800.0)

    def test_block_submission_on_schedule_mismatch(self):
        """Test that invoice submission is blocked if schedule total does not equal grand total."""
        inv = frappe._dict({
            "grand_total": 10000.0,
            "rounded_total": 10000.0,
            "payment_schedule": [
                frappe._dict({"payment_amount": 5000.0}),
                frappe._dict({"payment_amount": 4000.0}), # total is 9000 != 10000
            ]
        })
        with self.assertRaises(frappe.ValidationError):
            validate_invoice_milestone_schedule_before_submit(inv)
