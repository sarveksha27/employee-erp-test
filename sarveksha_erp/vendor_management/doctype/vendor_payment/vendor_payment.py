# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class VendorPayment(Document):

    def validate(self):
        """Server-side validation on every save."""
        self.validate_amount()
        self.validate_dates()
        self.validate_status_transition()

    def before_submit(self):
        """Validation before the payment record is submitted."""
        if not self.reference_no:
            frappe.throw(
                _("Reference No / UTR is mandatory before submitting a payment.")
            )
        if self.status not in ("Approved", "Paid"):
            self.status = "Approved"

    def on_submit(self):
        """After submission, mark as Paid if not already."""
        if self.status != "Paid":
            self.db_set("status", "Paid")
        self.add_comment("Info",
            _("Payment of {0} {1} submitted by {2}").format(
                self.currency,
                frappe.utils.fmt_money(self.amount, currency=self.currency),
                frappe.session.user
            )
        )

    def on_cancel(self):
        """On cancellation, set status to Cancelled."""
        self.db_set("status", "Cancelled")
        self.add_comment("Info",
            _("Payment cancelled by {0}").format(frappe.session.user)
        )

    # ─── VALIDATION METHODS ───────────────────────────────

    def validate_amount(self):
        """Reject zero or negative payment amounts."""
        if flt(self.amount) <= 0:
            frappe.throw(
                _("Payment amount must be greater than zero. "
                  "Current value: {0}").format(self.amount)
            )

    def validate_dates(self):
        """Ensure payment date is not in the future."""
        if self.payment_date:
            if getdate(self.payment_date) > getdate(nowdate()):
                frappe.throw(
                    _("Payment Date cannot be in the future. "
                      "Current date: {0}, Payment date: {1}").format(
                        nowdate(), self.payment_date
                    )
                )
        if self.reference_date and self.payment_date:
            if getdate(self.reference_date) > getdate(self.payment_date):
                frappe.throw(
                    _("Reference Date cannot be after the Payment Date.")
                )

    def validate_status_transition(self):
        """Enforce valid status transitions to prevent status manipulation."""
        if self.is_new():
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        old_status = previous.status
        new_status = self.status

        if old_status == new_status:
            return

        # Define valid transitions
        valid_transitions = {
            "Draft": ["Pending Approval", "Cancelled"],
            "Pending Approval": ["Approved", "Draft", "Cancelled"],
            "Approved": ["Paid", "Cancelled"],
            "Paid": ["Cancelled"],
            "Cancelled": [],  # Cannot transition out of Cancelled
        }

        allowed_next = valid_transitions.get(old_status, [])
        if new_status not in allowed_next:
            frappe.throw(
                _("Invalid status transition: {0} → {1}. "
                  "Allowed transitions from '{0}': {2}").format(
                    old_status, new_status,
                    ", ".join(allowed_next) if allowed_next else "None"
                )
            )
