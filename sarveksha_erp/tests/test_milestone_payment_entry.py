import unittest
from unittest.mock import MagicMock, patch

import frappe

from sarveksha_erp.payment_tracking.milestone_payment_entry import (
    make_milestone_payment_entry,
    sync_milestone_payment_status,
    validate_milestone_payment_entry,
)
from sarveksha_erp.payment_tracking.payment_entry_workflow import validate_payment_entry_workflow
from sarveksha_erp.payment_tracking.report.vendor_milestone_aging.vendor_milestone_aging import (
    get_aging_bucket,
)


class FakeMeta:
    def __init__(self, fields):
        self.fields = [frappe._dict(fieldname=fieldname) for fieldname in fields]
        self.fieldnames = set(fields)

    def has_field(self, fieldname):
        return fieldname in self.fieldnames


class FakePaymentEntry:
    def __init__(self):
        self.meta = FakeMeta({"custom_vendor_purchase_order"})
        self.references = []

    def set(self, fieldname, value):
        setattr(self, fieldname, value)

    def append(self, fieldname, value):
        getattr(self, fieldname).append(frappe._dict(value))

    def insert(self):
        self.name = "ACC-PAY-TEST-001"


class TestMilestonePaymentEntry(unittest.TestCase):
    def test_make_milestone_payment_entry(self):
        invoice = frappe._dict(
            name="PINV-TEST-001",
            docstatus=1,
            supplier="Supplier A",
            grand_total=1000,
            vendor_purchase_order="VPO-TEST-001",
            payment_schedule=[
                frappe._dict(
                    name="PAY-SCHEDULE-001",
                    payment_term="30% Advance",
                    due_date="2026-03-01",
                    payment_amount=300,
                    outstanding=200,
                    paid_amount=100,
                )
            ],
        )
        invoice.check_permission = MagicMock()
        payment_entry = FakePaymentEntry()

        with (
            patch("frappe.get_doc", return_value=invoice),
            patch("frappe.get_roles", return_value=["Accounts Clerk"]),
            patch("frappe.has_permission"),
            patch("frappe.get_meta", return_value=FakeMeta({
                "custom_payment_term_milestone",
                "custom_milestone_row_id",
            })),
            patch("frappe.db.get_value", return_value=None),
            patch(
                "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry",
                return_value=payment_entry,
            ) as get_payment_entry,
        ):
            result = make_milestone_payment_entry(invoice.name, "PAY-SCHEDULE-001")

        get_payment_entry.assert_called_once_with(
            "Purchase Invoice", invoice.name, party_amount=200
        )
        self.assertEqual(result, "ACC-PAY-TEST-001")
        self.assertEqual(payment_entry.payment_type, "Pay")
        self.assertEqual(payment_entry.party_type, "Supplier")
        self.assertEqual(payment_entry.party, "Supplier A")
        self.assertEqual(payment_entry.paid_amount, 200)
        self.assertEqual(payment_entry.received_amount, 200)
        self.assertEqual(payment_entry.custom_payment_term_milestone, "30% Advance")
        self.assertEqual(payment_entry.custom_milestone_row_id, "PAY-SCHEDULE-001")
        self.assertEqual(payment_entry.workflow_state, "Draft")
        self.assertEqual(payment_entry.references[0].allocated_amount, 200)
        self.assertEqual(payment_entry.references[0].reference_name, invoice.name)

    def test_maker_checker_flow(self):
        doc = frappe._dict(name="ACC-PAY-TEST-002", workflow_state="Draft")
        with patch("frappe.get_roles", return_value=["Accounts Clerk"]):
            with self.assertRaises(frappe.PermissionError):
                validate_payment_entry_workflow(doc)

    def test_milestone_balance_reduction_on_submit(self):
        invoice = frappe._dict(
            name="PINV-TEST-002",
            vendor_purchase_order="VPO-TEST-002",
            payment_schedule=[
                frappe._dict(
                    name="PAY-SCHEDULE-002",
                    outstanding=0,
                    paid_amount=300,
                )
            ],
        )
        doc = frappe._dict(
            name="ACC-PAY-TEST-003",
            custom_milestone_row_id="PAY-SCHEDULE-002",
            references=[
                frappe._dict(
                    reference_doctype="Purchase Invoice",
                    reference_name=invoice.name,
                )
            ],
        )
        with (
            patch("frappe.get_doc", side_effect=[invoice, frappe._dict(notify_update=MagicMock())]),
            patch("frappe.get_meta", side_effect=[
                FakeMeta({"custom_milestone_status"}),
                FakeMeta({"vendor_purchase_order"}),
                FakeMeta({
                    "payment_tracking_status",
                    "payment_workflow_status",
                    "payment_status",
                    "billed_amount",
                    "outstanding_amount",
                    "balance_due",
                    "payment_pending",
                    "payment_partially_paid",
                    "payment_fully_paid",
                }),
            ]),
            patch("frappe.db.set_value") as set_value,
            patch("frappe.db.sql", return_value=[frappe._dict(billed_amount=300, outstanding_amount=0)]),
        ):
            sync_milestone_payment_status(doc, "on_submit")

        set_value.assert_any_call(
            "Payment Schedule",
            "PAY-SCHEDULE-002",
            "custom_milestone_status",
            "Paid",
            update_modified=False,
        )
        self.assertEqual(invoice.payment_schedule[0].paid_amount, 300)
        self.assertEqual(invoice.payment_schedule[0].outstanding, 0)

    def test_po_status_sync(self):
        for outstanding, expected_tracking_status, expected_payment_status in (
            (500, "Partially Paid", "Partially Paid"),
            (0, "Paid", "Fully Paid"),
        ):
            invoice = frappe._dict(
                name="PINV-TEST-003",
                vendor_purchase_order="VPO-TEST-003",
                payment_schedule=[
                    frappe._dict(
                        name="PAY-SCHEDULE-003",
                        outstanding=outstanding,
                        paid_amount=1000 - outstanding,
                    )
                ],
            )
            doc = frappe._dict(
                name="ACC-PAY-TEST-004",
                custom_milestone_row_id="PAY-SCHEDULE-003",
                references=[
                    frappe._dict(
                        reference_doctype="Purchase Invoice",
                        reference_name=invoice.name,
                    )
                ],
            )
            po = frappe._dict(notify_update=MagicMock())
            with (
                patch("frappe.get_doc", side_effect=[invoice, po]),
                patch("frappe.get_meta", side_effect=[
                    FakeMeta(set()),
                    FakeMeta({"vendor_purchase_order"}),
                    FakeMeta({
                        "payment_tracking_status",
                        "payment_workflow_status",
                        "payment_status",
                        "billed_amount",
                        "outstanding_amount",
                        "balance_due",
                        "payment_pending",
                        "payment_partially_paid",
                        "payment_fully_paid",
                    }),
                ]),
                patch("frappe.db.set_value") as set_value,
                patch(
                    "frappe.db.sql",
                    return_value=[
                        frappe._dict(billed_amount=1000, outstanding_amount=outstanding)
                    ],
                ),
            ):
                sync_milestone_payment_status(doc, "on_submit")

            po_update = set_value.call_args_list[-1].args[2]
            self.assertEqual(po_update["payment_tracking_status"], expected_tracking_status)
            self.assertEqual(po_update["payment_workflow_status"], expected_tracking_status)
            self.assertEqual(po_update["payment_status"], expected_payment_status)

    def test_aging_report_buckets(self):
        self.assertEqual(get_aging_bucket("2026-11-04", 100, "2026-11-04"), "Current")
        self.assertEqual(get_aging_bucket("2026-10-05", 100, "2026-11-04"), "1-30 Days")
        self.assertEqual(get_aging_bucket("2026-09-05", 100, "2026-11-04"), "31-60 Days")
        self.assertEqual(get_aging_bucket("2026-08-06", 100, "2026-11-04"), "61-90 Days")
        self.assertEqual(get_aging_bucket("2026-08-05", 100, "2026-11-04"), "90+ Days")
        self.assertEqual(get_aging_bucket("2026-08-04", 0, "2026-11-04"), "Current")

    def test_milestone_submission_validates_exact_schedule_row(self):
        invoice = frappe._dict(
            name="PINV-TEST-004",
            supplier="Supplier A",
            payment_schedule=[
                frappe._dict(name="PAY-SCHEDULE-004", payment_term="Net 30 Days", outstanding=100)
            ],
        )
        doc = frappe._dict(
            payment_type="Pay",
            party_type="Supplier",
            party="Supplier A",
            references=[
                frappe._dict(
                    reference_doctype="Purchase Invoice",
                    reference_name=invoice.name,
                    payment_term="Net 30 Days",
                    allocated_amount=100,
                )
            ],
            custom_milestone_row_id="PAY-SCHEDULE-004",
            custom_payment_term_milestone="Net 30 Days",
        )
        with patch("frappe.get_doc", return_value=invoice):
            validate_milestone_payment_entry(doc)
