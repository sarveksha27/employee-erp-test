# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class VendorPurchaseOrder(Document):

    def validate(self):
        """Called on every Save. Validates data and recalculates totals."""
        self.set_default_letter_head()
        self.validate_creation_roles()
        self.validate_generator_edit_rights()
        self.validate_audit_comments_edit_rights()
        self.track_workflow_audit_trail()
        self.sanitize_text_fields()
        self.validate_non_negative_values()
        self.calculate_grand_total()
        self.calculate_advance()
        self.validate_required_fields()

    def set_default_letter_head(self):
        """Auto-detect and set default letter head if not selected."""
        if self.letter_head:
            return

        if self.company:
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

    def validate_audit_comments_edit_rights(self):
        """Ensure verifier_comments cannot be modified outside Pending Verification stage,
        and approver_comments cannot be modified outside Pending Approval stage."""
        if self.is_new():
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        old_state = previous.workflow_state or "Draft"

        # Check verifier_comments modification
        if self.has_value_changed("verifier_comments"):
            if old_state != "Pending Verification":
                frappe.throw(
                    _("Verifier comments can only be edited during the 'Pending Verification' stage."),
                    frappe.PermissionError
                )

        # Check approver_comments modification
        if self.has_value_changed("approver_comments"):
            if old_state != "Pending Approval":
                frappe.throw(
                    _("Approver comments can only be edited during the 'Pending Approval' stage."),
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
        if getattr(self.flags, 'ignore_immutable_validation', False):
            return
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


def seed_10_equipment_items():
    """Ensure at least 10 fully populated Equipment master items exist and that
    all pre-generated Vendor Purchase Orders contain at least 10 complete equipment line items."""

    sample_equipments = [
        {
            "equipment_name": "Cone Crusher Assembly Model HP400",
            "hsn_code": "84742010",
            "brand": "Metso Outotec",
            "manufacturer": "Metso Outotec Oyj Finland",
            "unit": "Set",
            "approx_cost_inr": 1250000.0,
            "gst_percentage": 18.0,
            "specification": "High-capacity secondary cone crusher with hydraulic adjustment, anti-spin mechanism, and integrated lubrication skid."
        },
        {
            "equipment_name": "Vibrating Screen Triple Deck 2400x6000",
            "hsn_code": "84741000",
            "brand": "Sandvik Mining",
            "manufacturer": "Sandvik AB Sweden",
            "unit": "Set",
            "approx_cost_inr": 850000.0,
            "gst_percentage": 18.0,
            "specification": "Heavy-duty inclined vibrating screen with polyurethane screen media, eccentric shaft drive, and vibration dampers."
        },
        {
            "equipment_name": "Slurry Pump High Head 150kW",
            "hsn_code": "84137099",
            "brand": "Warman Slurry",
            "manufacturer": "Weir Minerals Australia",
            "unit": "Nos",
            "approx_cost_inr": 450000.0,
            "gst_percentage": 18.0,
            "specification": "Heavy-duty rubber-lined centrifugal slurry pump with mechanical seal and variable frequency drive motor."
        },
        {
            "equipment_name": "Heavy Duty Belt Conveyor Drive 45kW",
            "hsn_code": "84283300",
            "brand": "FLSmidth",
            "manufacturer": "FLSmidth A/S Denmark",
            "unit": "Set",
            "approx_cost_inr": 680000.0,
            "gst_percentage": 18.0,
            "specification": "1200mm belt conveyor drive head unit with shaft-mounted gearbox, holdback backstop, and motorized pulley."
        },
        {
            "equipment_name": "Magnetic Separator High Intensity",
            "hsn_code": "84749000",
            "brand": "Eriez Magnetics",
            "manufacturer": "Eriez Manufacturing Co. USA",
            "unit": "Nos",
            "approx_cost_inr": 520000.0,
            "gst_percentage": 18.0,
            "specification": "Cross-belt self-cleaning permanent magnetic separator with stainless steel armor belt and dust-proof motor."
        },
        {
            "equipment_name": "Heavy Duty Hydraulic Excavator Bucket 2.5m3",
            "hsn_code": "84314990",
            "brand": "Caterpillar Inc",
            "manufacturer": "Caterpillar Inc. USA",
            "unit": "Nos",
            "approx_cost_inr": 380000.0,
            "gst_percentage": 18.0,
            "specification": "Severe-duty rock bucket forged with Hardox 500 wear plates, side cutters, and GET adapter tooth system."
        },
        {
            "equipment_name": "Industrial Variable Frequency Drive 250kW",
            "hsn_code": "85044090",
            "brand": "ABB Industrial",
            "manufacturer": "ABB Ltd. Switzerland",
            "unit": "Nos",
            "approx_cost_inr": 950000.0,
            "gst_percentage": 18.0,
            "specification": "ACS880 cabinet-built VFD drive with direct torque control (DTC), IP54 enclosure, and Modbus TCP communication card."
        },
        {
            "equipment_name": "High Pressure Multi-Stage Water Pump",
            "hsn_code": "84137010",
            "brand": "Grundfos Pumps",
            "manufacturer": "Grundfos A/S Denmark",
            "unit": "Nos",
            "approx_cost_inr": 290000.0,
            "gst_percentage": 18.0,
            "specification": "Vertical multistage centrifugal pump CR 95 in AISI 316 stainless steel with cartridge shaft seal and IE3 motor."
        },
        {
            "equipment_name": "Spherical Roller Bearing Assembly 22234",
            "hsn_code": "84832000",
            "brand": "SKF Bearings",
            "manufacturer": "SKF Group Sweden",
            "unit": "Set",
            "approx_cost_inr": 180000.0,
            "gst_percentage": 18.0,
            "specification": "Heavy-duty spherical roller bearing set with adapter sleeve, labyrinth seals, and cast iron plummer block housing."
        },
        {
            "equipment_name": "Electromagnetic Flow Meter DN200",
            "hsn_code": "90261010",
            "brand": "Endress+Hauser",
            "manufacturer": "Endress+Hauser AG Switzerland",
            "unit": "Nos",
            "approx_cost_inr": 310000.0,
            "gst_percentage": 18.0,
            "specification": "Promag W 400 electromagnetic flowmeter with hard rubber lining, Hastelloy electrodes, and HART transmitter."
        }
    ]

    created_eq_docs = []
    for i, data in enumerate(sample_equipments, 1):
        name_key = f"EQ-{3280 + i:05d}"
        if frappe.db.exists("Equipment", name_key):
            doc = frappe.get_doc("Equipment", name_key)
            doc.update(data)
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "Equipment",
                "name": name_key,
                **data
            })
            doc.insert(ignore_permissions=True)
        created_eq_docs.append(doc)

    frappe.db.commit()

    # Now update all existing Vendor Purchase Orders so each has AT LEAST 10 line items
    vpos = frappe.get_all("Vendor Purchase Order", fields=["name"])
    for vpo_dict in vpos:
        vpo = frappe.get_doc("Vendor Purchase Order", vpo_dict.name)

        vpo.items = []
        for eq_doc in created_eq_docs:
            rate = flt(eq_doc.approx_cost_inr) or 100000.0
            gst_pct = flt(eq_doc.gst_percentage) or 18.0
            qty = 1.0
            taxable = rate * qty
            tax = taxable * (gst_pct / 100.0)
            total = taxable + tax

            vpo.append("items", {
                "equipment": eq_doc.name,
                "equipment_name": eq_doc.equipment_name,
                "hsn_code": eq_doc.hsn_code,
                "brand": eq_doc.brand,
                "manufacturer": eq_doc.manufacturer,
                "unit": eq_doc.unit or "Nos",
                "quantity": qty,
                "rate": rate,
                "discount_percent": 0.0,
                "gst_percentage": gst_pct,
                "taxable_amount": taxable,
                "tax_amount": tax,
                "total_amount": total,
                "specification": eq_doc.specification
            })

        # Sync top level item fields for backward compatibility
        vpo.equipment = created_eq_docs[0].name
        vpo.equipment_name = created_eq_docs[0].equipment_name
        vpo.hsn_code = created_eq_docs[0].hsn_code
        vpo.brand = created_eq_docs[0].brand
        vpo.manufacturer = created_eq_docs[0].manufacturer
        vpo.unit = created_eq_docs[0].unit
        vpo.quantity = 1.0
        vpo.rate = created_eq_docs[0].approx_cost_inr
        vpo.specification = created_eq_docs[0].specification

        vpo.calculate_grand_total()
        vpo.calculate_advance()
        vpo.flags.ignore_validate_update_after_submit = True
        vpo.flags.ignore_immutable_validation = True
        vpo.flags.ignore_permissions = True
        vpo.save(ignore_permissions=True)

    frappe.db.commit()
    print("Successfully seeded 10 equipment items across all Vendor Purchase Orders!")


def verify_10_equipment_items():
    pos = frappe.get_all("Vendor Purchase Order", fields=["name", "company", "workflow_state"])
    print(f"Total POs in system: {len(pos)}")
    for po in pos:
        doc = frappe.get_doc("Vendor Purchase Order", po.name)
        print(f"\n--- PO: {doc.name} (State: {doc.workflow_state}, Items: {len(doc.items)}) ---")
        for i, item in enumerate(doc.items, 1):
            print(f"  Item {i:2d}: Code: {item.equipment} | Name: {item.equipment_name} | HSN: {item.hsn_code} | Brand: {item.brand} | Qty: {item.quantity} | Rate: {item.rate} | Total: {item.total_amount}")


