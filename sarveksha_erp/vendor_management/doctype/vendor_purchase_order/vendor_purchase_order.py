# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class VendorPurchaseOrder(Document):

    def validate(self):
        """Called on every Save. Validates data and recalculates totals."""
        self.set_company_details()
        self.set_default_letter_head()
        self.set_default_terms()
        self.validate_uom()
        self.validate_creation_roles()
        self.validate_generator_edit_rights()
        self.validate_payment_permissions()
        self.validate_audit_comments_edit_rights()
        self.track_workflow_audit_trail()
        self.sanitize_text_fields()
        self.validate_non_negative_values()
        self.calculate_grand_total()
        self.calculate_advance()
        self.validate_required_fields()
        self.sync_payment_check_fields()

    def set_company_details(self):
        """Auto-set company address, PAN, GSTIN, default port, currency from Company Master."""
        if not self.company:
            return

        comp_doc = frappe.get_doc("Company", self.company)
        if not self.currency and comp_doc.default_currency:
            self.currency = comp_doc.default_currency

        if not self.default_port and comp_doc.custom_default_port:
            self.default_port = comp_doc.custom_default_port
            if not self.port:
                first_port = comp_doc.custom_default_port.split(',')[0].strip()
                if frappe.db.exists("Port", first_port):
                    self.port = first_port

        if comp_doc.tax_id:
            self.company_gstin = comp_doc.tax_id
        if comp_doc.custom_pan:
            self.company_pan = comp_doc.custom_pan

        # Fetch physical address of the Company from linked Address doctype
        address_text = ""
        addr_name = frappe.db.get_value(
            "Dynamic Link",
            {"link_doctype": "Company", "link_name": self.company, "parenttype": "Address"},
            "parent"
        )
        if addr_name:
            from frappe.contacts.doctype.address.address import get_address_display
            address_text = get_address_display(addr_name)
            if address_text:
                address_text = address_text.replace("<br>", "\n").strip()

        details_arr = []
        if address_text:
            details_arr.append(address_text)
        if comp_doc.registration_details:
            details_arr.append(comp_doc.registration_details)
        if comp_doc.tax_id:
            details_arr.append(f"Tax ID / GSTIN: {comp_doc.tax_id}")
        if comp_doc.custom_pan:
            details_arr.append(f"PAN: {comp_doc.custom_pan}")

        if details_arr:
            self.company_address = "\n".join([d for d in details_arr if d])

    def set_default_letter_head(self):
        """Auto-detect and set default letter head based on Company."""
        if not self.company:
            return

        comp_lh = frappe.db.get_value("Company", self.company, "default_letter_head")
        if comp_lh and frappe.db.exists("Letter Head", comp_lh):
            self.letter_head = comp_lh
            return

        comp_name = (self.company or "").lower()
        if "botswana" in comp_name and frappe.db.exists("Letter Head", "Botswana (Sarveksha Botswana)"):
            self.letter_head = "Botswana (Sarveksha Botswana)"
        elif "baani" in comp_name and frappe.db.exists("Letter Head", "Cameroon (Baani Minerals)"):
            self.letter_head = "Cameroon (Baani Minerals)"
        elif "mining" in comp_name and frappe.db.exists("Letter Head", "Cameroon (Sarveksha Mining SARL)"):
            self.letter_head = "Cameroon (Sarveksha Mining SARL)"
        elif "bstp" in comp_name and frappe.db.exists("Letter Head", "Guinea (Sarveksha BSTP SAS)"):
            self.letter_head = "Guinea (Sarveksha BSTP SAS)"
        elif "sl limited" in comp_name and frappe.db.exists("Letter Head", "Sierra Leone (Sarveksha SL Limited)"):
            self.letter_head = "Sierra Leone (Sarveksha SL Limited)"
        elif frappe.db.exists("Letter Head", "India (Sarveksha Realty)"):
            self.letter_head = "India (Sarveksha Realty)"

    def set_default_terms(self):
        """Auto-set default Terms and Conditions if not explicitly selected."""
        if self.standard_terms:
            return

        terms_to_add = []

        if self.is_lut_applicable and frappe.db.exists("Terms and Conditions", "LUT Certificate Terms"):
            terms_to_add.append("LUT Certificate Terms")

        if self.company:
            comp_name = (self.company or "").lower()
            if "bstp" in comp_name and frappe.db.exists("Terms and Conditions", "Guinea BSTP SAS Procurement Terms"):
                terms_to_add.append("Guinea BSTP SAS Procurement Terms")
            elif ("mining" in comp_name or "baani" in comp_name) and frappe.db.exists("Terms and Conditions", "Cameroon Mining & Minerals Terms"):
                terms_to_add.append("Cameroon Mining & Minerals Terms")
            elif "sl limited" in comp_name and frappe.db.exists("Terms and Conditions", "Sierra Leone Procurement Terms"):
                terms_to_add.append("Sierra Leone Procurement Terms")
            elif "botswana" in comp_name and frappe.db.exists("Terms and Conditions", "Botswana Mining & Equipment Terms"):
                terms_to_add.append("Botswana Mining & Equipment Terms")

        # Always append general export terms as a default as well if not already added
        if frappe.db.exists("Terms and Conditions", "Standard Export PO Terms"):
            if "Standard Export PO Terms" not in terms_to_add:
                terms_to_add.append("Standard Export PO Terms")

        for term in terms_to_add:
            self.append("standard_terms", {"standard_term": term})

    def validate_uom(self):
        """Ensure all UOMs in parent and child items exist in the database to prevent Link Validation errors."""
        # Collect all unique UOMs present on the document
        uoms = set()
        if self.unit:
            uoms.add(self.unit)
        
        if hasattr(self, "items") and self.items:
            for item in self.items:
                if getattr(item, "unit", None):
                    uoms.add(item.unit)

        # For each UOM, ensure it exists or dynamically create it
        validated_uoms = {}
        for uom_name in uoms:
            if not uom_name:
                continue
            if frappe.db.exists("UOM", uom_name):
                validated_uoms[uom_name] = uom_name
            else:
                try:
                    # Create the UOM record dynamically
                    uom_doc = frappe.new_doc("UOM")
                    uom_doc.name = uom_name
                    uom_doc.uom_name = uom_name
                    uom_doc.insert(ignore_permissions=True)
                    validated_uoms[uom_name] = uom_name
                except Exception:
                    # Fallback to an existing UOM
                    fallback_found = None
                    for fallback in ["Nos", "Unit"]:
                        if frappe.db.exists("UOM", fallback):
                            fallback_found = fallback
                            break
                    if fallback_found:
                        validated_uoms[uom_name] = fallback_found
                    else:
                        validated_uoms[uom_name] = uom_name

        # Apply validated/fallback UOMs back to parent and items
        if self.unit and self.unit in validated_uoms:
            self.unit = validated_uoms[self.unit]
        else:
            self.unit = "Nos"

        if hasattr(self, "items") and self.items:
            for item in self.items:
                if getattr(item, "unit", None) and item.unit in validated_uoms:
                    item.unit = validated_uoms[item.unit]
                else:
                    item.unit = "Nos"

    def validate_creation_roles(self):
        """Ensure PO Verifier and PO Approver cannot create new POs."""
        if self.is_new():
            if frappe.session.user == "Administrator":
                return

            user_roles = set(frappe.get_roles(frappe.session.user))
            
            # If the user has PO Verifier role and is not a PO Generator
            if "PO Verifier" in user_roles and "PO Generator" not in user_roles:
                frappe.throw(
                    _("PO Verifiers cannot create new Purchase Orders."),
                    frappe.PermissionError
                )

            # If the user has PO Approver role and is not a PO Generator
            if "PO Approver" in user_roles and "PO Generator" not in user_roles:
                frappe.throw(
                    _("PO Approvers cannot create new Purchase Orders. "
                      "As an Approver, your role is strictly to review, verify, "
                      "and approve or reject/return purchase orders forwarded by PO Generators and Verifiers. "
                      "If you need to generate a purchase order, please request a user with the PO Generator role to initiate the draft."),
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
            previous = self.get_doc_before_save()
            old_state = (previous.workflow_state if previous else None) or "Draft"
            if old_state in ["Generated (Yet to be Verified)", "Verified (Yet to be approved)", "Approved"]:
                frappe.throw(
                    _("PO Generator cannot modify a Purchase Order once generated and submitted for verification."),
                    frappe.PermissionError
                )

    def validate_payment_permissions(self):
        """Ensure only authorized roles can modify payment fields on save."""
        if self.is_new():
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        payment_fields = ["payment_status", "payment_pending", "payment_partially_paid", "payment_fully_paid"]
        changed = any(previous.get(f) != self.get(f) for f in payment_fields)
        if changed:
            self._check_payment_role()

    def validate_audit_comments_edit_rights(self):
        """Ensure verifier_comments cannot be modified outside Generated (Yet to be Verified) stage,
        and approver_comments cannot be modified outside Verified (Yet to be approved) stage."""
        if self.is_new():
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        old_state = previous.workflow_state or "Draft"

        # Check verifier_comments modification
        if self.has_value_changed("verifier_comments"):
            if old_state != "Generated (Yet to be Verified)":
                frappe.throw(
                    _("Verifier comments can only be edited during the 'Generated (Yet to be Verified)' stage."),
                    frappe.PermissionError
                )

        # Check approver_comments modification
        if self.has_value_changed("approver_comments"):
            if old_state != "Verified (Yet to be approved)":
                frappe.throw(
                    _("Approver comments can only be edited during the 'Verified (Yet to be approved)' stage."),
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

            # Transition to Verified (Yet to be approved) (Verifier verified)
            if new_state == "Verified (Yet to be approved)" and old_state == "Generated (Yet to be Verified)":
                self.verified_by = frappe.session.user
                self.verified_on = now
                self.verifier_status = "Verified"

            # Transition to Draft (Verifier returned to Generator)
            elif new_state == "Draft" and old_state == "Generated (Yet to be Verified)":
                self.verified_by = frappe.session.user
                self.verified_on = now
                self.verifier_status = "Returned to Generator"

            # Transition to Approved (Approver approved)
            elif new_state == "Approved":
                self.approved_by = frappe.session.user
                self.approved_on = now
                self.approver_status = "Approved"
                self.status = "Approved"

            # Transition from Verified (Yet to be approved) back to Generated (Yet to be Verified) (Approver returned to Verifier)
            elif new_state == "Generated (Yet to be Verified)" and old_state == "Verified (Yet to be approved)":
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
        self.db_set("payment_pending", 1)
        self.db_set("payment_partially_paid", 0)
        self.db_set("payment_fully_paid", 0)
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
        self.db_set("payment_pending", 1)
        self.db_set("payment_partially_paid", 0)
        self.db_set("payment_fully_paid", 0)

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

    def sync_payment_check_fields(self):
        """Sync boolean Check fields with payment_status Select field value."""
        status = self.payment_status or "Pending"
        self.payment_pending = 1 if status == "Pending" else 0
        self.payment_partially_paid = 1 if status in ["Advance Paid", "Partially Paid"] else 0
        self.payment_fully_paid = 1 if status == "Fully Paid" else 0

    def _validate_immutable_fields_after_submit(self):
        """Prevent critical fields and child tables from being changed after submission."""
        if getattr(self.flags, 'ignore_immutable_validation', False):
            return
        if self.docstatus != 1:
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        # 1. Parent level financial/tax fields
        immutable_fields = [
            ("vendor", "Vendor"),
            ("company", "Company"),
            ("grand_total", "Grand Total"),
            ("cgst_amount", "CGST Amount"),
            ("sgst_amount", "SGST Amount"),
            ("igst_amount", "IGST Amount"),
            ("freight", "Freight Charges"),
            ("insurance", "Insurance"),
            ("packing_charges", "Packing Charges"),
            ("other_charges", "Other Charges"),
            ("is_lut_applicable", "LUT Applicable"),
            ("vendor_gstin", "Vendor GSTIN"),
            ("company_gstin", "Company GSTIN"),
        ]
        for field, label in immutable_fields:
            if previous.get(field) != self.get(field):
                frappe.throw(
                    _("Critical field {0} cannot be changed after submission.").format(label),
                    frappe.PermissionError
                )

        # 2. Child table 'items' verification
        prev_items = previous.get("items") or []
        curr_items = self.get("items") or []

        if len(prev_items) != len(curr_items):
            frappe.throw(
                _("Items table cannot be modified after submission (cannot add/remove rows)."),
                frappe.PermissionError
            )

        # Compare row by row
        critical_item_fields = ["equipment", "quantity", "rate", "gst_percentage", "amount", "cgst_amount", "sgst_amount", "igst_amount"]
        for idx, prev_item in enumerate(prev_items):
            curr_item = curr_items[idx]
            for field in critical_item_fields:
                if prev_item.get(field) != curr_item.get(field):
                    frappe.throw(
                        _("Item details at row {0} ({1}) cannot be changed after submission.").format(idx + 1, field),
                        frappe.PermissionError
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
                # Override GST percentage to 0.1% if LUT is applicable
                if self.is_lut_applicable:
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
            self.hsn_code = getattr(first, 'hsn_code', None)
            self.brand = getattr(first, 'brand', None)
            self.manufacturer = getattr(first, 'manufacturer', None)
            self.quantity = first.quantity
            self.unit = getattr(first, 'unit', None)
            self.rate = first.rate
            self.gst_percentage = first.gst_percentage
            self.specification = getattr(first, 'specification', None)
        else:
            # Fallback for single item legacy POs
            if getattr(self, "is_lut_applicable", False):
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
        
        if self.is_lut_applicable:
            gst_type = "IGST"
        else:
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
        self.db_set("payment_pending", 0)
        self.db_set("payment_partially_paid", 1)
        self.db_set("payment_fully_paid", 0)
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
        self.db_set("payment_pending", 0)
        self.db_set("payment_partially_paid", 0)
        self.db_set("payment_fully_paid", 1)
        self.add_comment("Info",
            _("Marked as Fully Paid by {0}").format(frappe.session.user)
        )
        frappe.msgprint(
            _("PO marked as Fully Paid."),
            indicator="green"
        )

    def _check_payment_role(self):
        """Ensure only authorized roles can modify payment status."""
        allowed_roles = {"System Manager", "Administrator", "Procurement Manager"}
        user_roles = set(frappe.get_roles(frappe.session.user))
        if not allowed_roles.intersection(user_roles):
            frappe.throw(
                _("You do not have permission to modify payment status. "
                  "Required role: Procurement Manager."),
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
        if state != "Approved":
            return False

        # Only the PO Generator (or managers/administrators) can print.
        # Verifiers and Approvers cannot print.
        allowed_roles = {"PO Generator", "Procurement Manager", "System Manager", "Administrator"}
        if allowed_roles.intersection(user_roles):
            return True
        return False

    return True


def get_permission_query_conditions(user=None):
    """Apply automatic filtering to the purchase order list view for Verifiers and Approvers."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    user_roles = set(frappe.get_roles(user))

    # If user is a PO Approver and not a PO Generator, restrict view
    if "PO Approver" in user_roles and "PO Generator" not in user_roles:
        return "(`tabVendor Purchase Order`.workflow_state in ('Verified (Yet to be approved)', 'Approved'))"

    # If user is a PO Verifier and not a PO Generator, restrict view
    if "PO Verifier" in user_roles and "PO Generator" not in user_roles:
        return "(`tabVendor Purchase Order`.workflow_state in ('Generated (Yet to be Verified)', 'Verified (Yet to be approved)', 'Approved'))"

    return ""



@frappe.whitelist()
def get_company_details(company):
    if not company:
        return {}

    comp_doc = frappe.get_doc("Company", company)

    # Fetch physical address of the Company from linked Address doctype
    address_text = ""
    addr_name = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
        "parent"
    )
    if addr_name:
        from frappe.contacts.doctype.address.address import get_address_display
        address_text = get_address_display(addr_name)
        if address_text:
            address_text = address_text.replace("<br>", "\n").strip()

    details_arr = []
    if address_text:
        details_arr.append(address_text)
    if comp_doc.registration_details:
        details_arr.append(comp_doc.registration_details)
    if comp_doc.tax_id:
        details_arr.append(f"Tax ID / GSTIN: {comp_doc.tax_id}")
    if comp_doc.custom_pan:
        details_arr.append(f"PAN: {comp_doc.custom_pan}")

    company_address = "\n".join([d for d in details_arr if d])

    # Auto-detect letter head
    letter_head = comp_doc.default_letter_head
    if not letter_head:
        company_name = company.lower()
        country = (comp_doc.country or "").lower()
        letter_head = "India (Sarveksha Realty)"
        if "botswana" in company_name or "botswana" in country:
            letter_head = "Botswana (Sarveksha Botswana)"
        elif "baani" in company_name:
            letter_head = "Cameroon (Baani Minerals)"
        elif "mining" in company_name or "cameroon" in country:
            letter_head = "Cameroon (Sarveksha Mining SARL)"
        elif "bstp" in company_name or "guinea" in country:
            letter_head = "Guinea (Sarveksha BSTP SAS)"
        elif "sl limited" in company_name or "sierra" in country:
            letter_head = "Sierra Leone (Sarveksha SL Limited)"
        elif "india" in country:
            letter_head = "India (Sarveksha Realty)"

    return {
        "default_port": comp_doc.custom_default_port or "",
        "currency": comp_doc.default_currency or "",
        "company_gstin": comp_doc.tax_id or "",
        "company_pan": comp_doc.custom_pan or "",
        "company_address": company_address,
        "letter_head": letter_head
    }


