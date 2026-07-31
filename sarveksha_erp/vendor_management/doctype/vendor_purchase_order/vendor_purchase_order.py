# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class VendorPurchaseOrder(Document):

    def validate(self):
        """Called on every Save. Validates data and recalculates totals."""
        self.validate_creation_roles()
        self.validate_generator_edit_rights()
        self.track_workflow_audit_trail()
        self.sanitize_text_fields()
        self.validate_non_negative_values()
        self.calculate_grand_total()
        self.calculate_advance()
        self.validate_required_fields()

    def validate_creation_roles(self):
        """Ensure PO Verifier and PO Approver cannot create new POs."""
        if self.is_new():
            user_roles = set(frappe.get_roles(frappe.session.user))
            allowed_creator_roles = {"PO Generator", "Procurement Manager", "System Manager", "Administrator"}
            if not user_roles.intersection(allowed_creator_roles):
                if "PO Verifier" in user_roles or "PO Approver" in user_roles:
                    frappe.throw(
                        _("PO Verifiers and Approvers cannot create new Purchase Orders."),
                        frappe.PermissionError
                    )

    def validate_generator_edit_rights(self):
        """Prevent PO Generator from modifying PO once generated / submitted for verification."""
        if self.is_new():
            return
            
        user_roles = set(frappe.get_roles(frappe.session.user))
        admin_or_higher = {"PO Verifier", "PO Approver", "Procurement Manager", "System Manager", "Administrator"}
        
        # If user is PO Generator and does not have higher roles
        if "PO Generator" in user_roles and not user_roles.intersection(admin_or_higher):
            state = self.workflow_state or "Draft"
            if state in ["Pending Verification", "Pending Approval", "Approved", "Printed"]:
                frappe.throw(
                    _("PO Generator cannot modify a Purchase Order once generated and submitted for verification."),
                    frappe.PermissionError
                )

    def track_workflow_audit_trail(self):
        """Update audit fields (verified_by, verified_on, approved_by, approved_on) on workflow transition."""
        if self.is_new():
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        old_state = previous.workflow_state
        new_state = self.workflow_state

        if old_state != new_state:
            now = frappe.utils.now_datetime()

            # Transition to Pending Approval (Verifier verified)
            if new_state == "Pending Approval" and old_state == "Pending Verification":
                self.verified_by = frappe.session.user
                self.verified_on = now
                self.verifier_status = "Verified"

            # Transition to Verification Returned (Verifier returned to Generator)
            elif new_state == "Verification Returned":
                self.verified_by = frappe.session.user
                self.verified_on = now
                self.verifier_status = "Returned to Generator"

            # Transition to Approved (Approver approved)
            elif new_state == "Approved":
                self.approved_by = frappe.session.user
                self.approved_on = now
                self.approver_status = "Approved"
                self.status = "Approved"

            # Transition from Pending Approval back to Pending Verification (Approver returned to Verifier)
            elif new_state == "Pending Verification" and old_state == "Pending Approval":
                self.approved_by = frappe.session.user
                self.approved_on = now
                self.approver_status = "Returned to Verifier"

    def before_submit(self):
        """Called just before the document is submitted (docstatus → 1)."""
        # Enforce that a PO cannot be submitted without a grand total
        if not self.grand_total or self.grand_total <= 0:
            frappe.throw(
                _("Cannot submit a Purchase Order with zero Grand Total. "
                  "Please fill in Rate and Quantity.")
            )
        # Set status to Submitted automatically
        self.status = "Submitted"

    def on_submit(self):
        """Called after the document is successfully submitted."""
        # Ensure payment status starts as Pending on submission
        if not self.payment_status:
            self.db_set("payment_status", "Pending")
        frappe.msgprint(
            _("Purchase Order {0} submitted successfully. "
              "Grand Total: {1} {2}").format(
                self.name,
                self.currency,
                frappe.utils.fmt_money(self.grand_total, currency=self.currency)
            ),
            title=_("PO Submitted"),
            indicator="green"
        )

    def on_cancel(self):
        """Called when a submitted document is cancelled."""
        self.db_set("status", "Cancelled")
        self.db_set("payment_status", "Pending")

    def on_update_after_submit(self):
        """Validate that critical fields are not tampered with after submission."""
        self._validate_immutable_fields_after_submit()

    # ─── SANITIZATION METHODS ─────────────────────────────

    def sanitize_text_fields(self):
        """Strip potentially dangerous content from free-text fields."""
        text_fields = ["remarks", "payment_terms", "delivery_location",
                       "container_number", "quotation_ref", "pi_number",
                       "signatory"]
        for field in text_fields:
            value = self.get(field)
            if value and isinstance(value, str):
                # Remove script tags and event handlers (XSS prevention)
                import re
                cleaned = re.sub(r'<script[^>]*>.*?</script>', '', value,
                                 flags=re.IGNORECASE | re.DOTALL)
                cleaned = re.sub(r'\bon\w+\s*=', '', cleaned,
                                 flags=re.IGNORECASE)
                if cleaned != value:
                    self.set(field, cleaned)

    # ─── VALIDATION METHODS ───────────────────────────────

    def validate_non_negative_values(self):
        """Reject any negative monetary or quantity values."""
        currency_fields = [
            ("rate", "Unit Rate"),
            ("freight", "Freight Charges"),
            ("insurance", "Insurance"),
            ("packing_charges", "Packing Charges"),
            ("other_charges", "Other Charges"),
            ("second_payment", "Second Payment Amount"),
            ("final_payment", "Final Payment Amount"),
        ]
        for field, label in currency_fields:
            val = flt(self.get(field))
            if val < 0:
                frappe.throw(
                    _("{0} cannot be negative. Current value: {1}").format(
                        label, val
                    )
                )

        if flt(self.quantity) <= 0:
            frappe.throw(_("Quantity must be greater than zero."))

        if flt(self.discount_percent) < 0 or flt(self.discount_percent) > 100:
            frappe.throw(_("Discount % must be between 0 and 100."))

        if flt(self.advance_percentage) < 0 or flt(self.advance_percentage) > 100:
            frappe.throw(_("Advance % must be between 0 and 100."))

        if flt(self.exchange_rate) <= 0:
            frappe.throw(_("Exchange Rate must be greater than zero."))

    def validate_required_fields(self):
        """Validate business logic rules."""
        # Ensure PO date is not in the future by more than 7 days
        # (Allows backdating for reconciliation but not pre-dating by too much)
        if self.expected_delivery and self.po_date:
            if getdate(self.expected_delivery) < getdate(self.po_date):
                frappe.throw(
                    _("Expected Delivery Date cannot be before the PO Date.")
                )

        # Warn if quantity is unusual (not hard stop, just a warning)
        if self.quantity and self.quantity > 1000:
            frappe.msgprint(
                _("Quantity is set to {0}. Please verify this is correct.").format(
                    self.quantity
                ),
                title=_("High Quantity Warning"),
                indicator="orange"
            )

    def _validate_immutable_fields_after_submit(self):
        """Prevent critical fields from being changed after submission."""
        if self.docstatus != 1:
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        immutable_fields = [
            ("vendor", "Vendor"),
            ("company", "Company"),
            ("equipment", "Equipment"),
            ("rate", "Unit Rate"),
            ("quantity", "Quantity"),
            ("grand_total", "Grand Total"),
        ]
        for field, label in immutable_fields:
            old_val = previous.get(field)
            new_val = self.get(field)
            if old_val and new_val and str(old_val) != str(new_val):
                frappe.throw(
                    _("{0} cannot be changed after submission. "
                      "Please amend this Purchase Order instead.").format(label)
                )

    # ─── CALCULATION METHODS ──────────────────────────────

    def calculate_grand_total(self):
        """
        Grand Total = Sum(Item Taxable Values + Item Taxes) + Freight + Insurance + Packing + Other
        """
        freight = flt(self.freight)
        insurance = flt(self.insurance)
        packing = flt(self.packing_charges)
        other = flt(self.other_charges)

        total_taxable_value = 0.0
        total_item_tax = 0.0

        if self.items:
            for item in self.items:
                # Override GST percentage to 0.1% if LUT is applicable and company is "Sarveksha Realty"
                if self.is_lut_applicable and self.company and "Sarveksha Realty" in self.company:
                    item.gst_percentage = 0.1

                rate = flt(item.rate)
                qty = flt(item.quantity) or 1
                discount_pct = flt(item.discount_percent)
                gst_pct = flt(item.gst_percentage)

                base_amount = rate * qty
                discount_amount = base_amount * (discount_pct / 100.0)
                taxable_amount = base_amount - discount_amount
                
                item.taxable_amount = flt(taxable_amount, 2)
                item.tax_amount = flt(taxable_amount * (gst_pct / 100.0), 2)
                item.total_amount = flt(item.taxable_amount + item.tax_amount, 2)

                total_taxable_value += item.taxable_amount
                total_item_tax += item.tax_amount

            # Keep legacy single-equipment fields synced with first item for backwards compatibility
            first = self.items[0]
            self.equipment = first.equipment
            self.equipment_name = first.equipment_name
            self.quantity = first.quantity
            self.rate = first.rate
            self.gst_percentage = first.gst_percentage
        else:
            # Fallback for single item legacy POs
            if getattr(self, "is_lut_applicable", False) and self.company and "Sarveksha Realty" in self.company:
                self.gst_percentage = 0.1

            rate = flt(self.rate)
            qty = flt(self.quantity) or 1
            discount_pct = flt(self.discount_percent)
            gst_pct = flt(self.gst_percentage)

            base_amount = rate * qty
            discount_amount = base_amount * (discount_pct / 100.0)
            total_taxable_value = base_amount - discount_amount
            total_item_tax = total_taxable_value * (gst_pct / 100.0)

        self.taxable_value = flt(total_taxable_value, 2)

        # Determine GST Type (Intra-state vs Inter-state)
        vendor_gstin = self.vendor_gstin or ""
        company_gstin = self.company_gstin or ""
        
        gst_type = "IGST"
        if len(vendor_gstin) >= 2 and len(company_gstin) >= 2:
            if vendor_gstin[:2] == company_gstin[:2]:
                gst_type = "CGST + SGST"
        
        self.gst_type = gst_type

        # Calculate GST amounts
        if gst_type == "CGST + SGST":
            self.cgst_amount = flt(total_item_tax / 2.0, 2)
            self.sgst_amount = flt(total_item_tax / 2.0, 2)
            self.igst_amount = 0.0
            self.tax_amount = flt(self.cgst_amount + self.sgst_amount, 2)
        else:
            self.cgst_amount = 0.0
            self.sgst_amount = 0.0
            self.igst_amount = flt(total_item_tax, 2)
            self.tax_amount = flt(self.igst_amount, 2)

        # Grand Total
        self.grand_total = flt(self.taxable_value + self.tax_amount + freight + insurance + packing + other, 2)

    def calculate_advance(self):
        """
        Advance Amount = Grand Total × (Advance % / 100)
        """
        grand_total = flt(self.grand_total)
        advance_pct = flt(self.advance_percentage)
        self.advance_amount = flt(grand_total * (advance_pct / 100), 2)
        self.balance_due = flt(grand_total - self.advance_amount, 2)

    # ─── UTILITY METHODS ─────────────────────────────────

    @frappe.whitelist()
    def mark_advance_paid(self):
        """API method to mark advance as paid. Can be called from JS button."""
        self._check_payment_role()
        if self.docstatus != 1:
            frappe.throw(_("Document must be submitted to mark payment."))
        if self.payment_status == "Fully Paid":
            frappe.throw(_("This PO is already fully paid."))

        self.db_set("payment_status", "Advance Paid")
        self.db_set("status", "Partially Paid")
        self.add_comment("Info",
            _("Advance payment marked by {0}").format(frappe.session.user)
        )
        frappe.msgprint(
            _("Advance payment marked successfully."),
            indicator="green"
        )

    @frappe.whitelist()
    def mark_fully_paid(self):
        """API method to mark the PO as fully paid."""
        self._check_payment_role()
        if self.docstatus != 1:
            frappe.throw(_("Document must be submitted to mark payment."))

        self.db_set("payment_status", "Fully Paid")
        self.db_set("status", "Fully Paid")
        self.add_comment("Info",
            _("Marked as Fully Paid by {0}").format(frappe.session.user)
        )
        frappe.msgprint(
            _("PO marked as Fully Paid."),
            indicator="green"
        )

    def _check_payment_role(self):
        """Ensure only authorized roles can modify payment status."""
        allowed_roles = {"System Manager", "Accounts Manager", "Purchase Manager"}
        user_roles = set(frappe.get_roles(frappe.session.user))
        if not allowed_roles.intersection(user_roles):
            frappe.throw(
                _("You do not have permission to modify payment status. "
                  "Required role: Accounts Manager or Purchase Manager."),
                frappe.PermissionError
            )


def has_permission(doc, ptype="read", user=None):
    """Custom permission check for Vendor Purchase Order."""
    if not user:
        user = frappe.session.user

    user_roles = set(frappe.get_roles(user))

    # Print Permission Guard
    if ptype == "print":
        admin_roles = {"Procurement Manager", "System Manager", "Administrator"}
        if admin_roles.intersection(user_roles):
            return True
        state = (doc.workflow_state if doc else None) or "Draft"
        if state not in ["Approved", "Printed"]:
            return False

    return True
