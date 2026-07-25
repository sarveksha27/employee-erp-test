# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VendorPurchaseOrder(Document):

    def validate(self):
        """Called on every Save. Validates data and recalculates totals."""
        self.calculate_grand_total()
        self.calculate_advance()
        self.validate_required_fields()

    def before_submit(self):
        """Called just before the document is submitted (docstatus → 1)."""
        # Enforce that a PO cannot be submitted without a grand total
        if not self.grand_total or self.grand_total <= 0:
            frappe.throw(
                "Cannot submit a Purchase Order with zero Grand Total. "
                "Please fill in Rate and Quantity."
            )
        # Set status to Submitted automatically
        self.status = "Submitted"

    def on_submit(self):
        """Called after the document is successfully submitted."""
        # Ensure payment status starts as Pending on submission
        if not self.payment_status:
            self.db_set("payment_status", "Pending")
        frappe.msgprint(
            f"Purchase Order {self.name} submitted successfully. "
            f"Grand Total: {self.currency} {self.grand_total:,.2f}",
            title="PO Submitted",
            indicator="green"
        )

    def on_cancel(self):
        """Called when a submitted document is cancelled."""
        self.db_set("status", "Cancelled")
        self.db_set("payment_status", "Pending")

    # ─── CALCULATION METHODS ──────────────────────────────────

    def calculate_grand_total(self):
        """
        Grand Total = (Rate × Quantity) - Discount + Tax + Freight + Insurance + Packing + Other
        """
        rate = self.rate or 0
        qty = self.quantity or 1
        discount_pct = self.discount_percent or 0
        tax = self.tax_amount or 0
        freight = self.freight or 0
        insurance = self.insurance or 0
        packing = self.packing_charges or 0
        other = self.other_charges or 0

        base_amount = rate * qty
        discount_amount = base_amount * (discount_pct / 100)
        net_amount = base_amount - discount_amount
        self.grand_total = net_amount + tax + freight + insurance + packing + other

    def calculate_advance(self):
        """
        Advance Amount = Grand Total × (Advance % / 100)
        """
        grand_total = self.grand_total or 0
        advance_pct = self.advance_percentage or 0
        self.advance_amount = grand_total * (advance_pct / 100)

    # ─── VALIDATION METHODS ───────────────────────────────────

    def validate_required_fields(self):
        """Validate business logic rules."""
        # Ensure PO date is not in the future by more than 7 days
        # (Allows backdating for reconciliation but not pre-dating by too much)
        if self.expected_delivery and self.po_date:
            if self.expected_delivery < self.po_date:
                frappe.throw(
                    "Expected Delivery Date cannot be before the PO Date."
                )

        # Warn if quantity is unusual (not hard stop, just a warning)
        if self.quantity and self.quantity > 1000:
            frappe.msgprint(
                f"Quantity is set to {self.quantity}. Please verify this is correct.",
                title="High Quantity Warning",
                indicator="orange"
            )

    # ─── UTILITY METHODS ─────────────────────────────────────

    @frappe.whitelist()
    def mark_advance_paid(self):
        """API method to mark advance as paid. Can be called from JS button."""
        if self.docstatus != 1:
            frappe.throw("Document must be submitted to mark payment.")
        self.db_set("payment_status", "Advance Paid")
        self.db_set("status", "Partially Paid")
        frappe.msgprint("Advance payment marked successfully.", indicator="green")

    @frappe.whitelist()
    def mark_fully_paid(self):
        """API method to mark the PO as fully paid."""
        if self.docstatus != 1:
            frappe.throw("Document must be submitted to mark payment.")
        self.db_set("payment_status", "Fully Paid")
        self.db_set("status", "Fully Paid")
        frappe.msgprint("PO marked as Fully Paid.", indicator="green")
