# Copyright (c) 2026, Sarveksha and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, money_in_words


class ProformaInvoice(Document):

	def validate(self):
		self.validate_internal_po_reference()
		self.validate_margin()
		self.validate_non_negative()
		self.set_parties_and_metadata()
		self.calculate_totals()

	def validate_internal_po_reference(self):
		"""Enforce: PI can ONLY be raised from a referenced Internal PO, never from External PO."""
		if not self.internal_po:
			frappe.throw(_("A referenced Internal Purchase Order is required to generate a Proforma Invoice."))

		po = frappe.get_doc("Vendor Purchase Order", self.internal_po)
		if (po.po_type or "") != "Internal PO":
			frappe.throw(
				_("Proforma Invoices can only be raised for referenced Internal POs. "
				  "Purchase Order {0} is an External PO and cannot have a Proforma Invoice.").format(self.internal_po),
				frappe.ValidationError
			)

		# Enforce: Only 1 active Proforma Invoice can be generated per Internal PO
		filters = {
			"internal_po": self.internal_po,
			"docstatus": ["!=", 2],
		}
		if not self.is_new() and self.name:
			filters["name"] = ["!=", self.name]

		existing_pi = frappe.db.get_value("Proforma Invoice", filters, "name")
		if existing_pi:
			frappe.throw(
				_("A Proforma Invoice ({0}) has already been generated from Internal PO {1}. Another PI cannot be generated.").format(
					existing_pi, self.internal_po
				),
				frappe.ValidationError,
			)

		# Auto-fill reference fields if not already populated
		self.po_reference_no = po.ref_number or po.name
		self.po_date = po.po_date
		self.buyer = po.company
		self.buyer_address = po.company_address or ""

	def validate_margin(self):
		"""Enforce margin percentage must be strictly between 5% and 30%."""
		margin = flt(self.margin_percentage)
		if margin < 5.0 or margin > 30.0:
			frappe.throw(
				_("SRI Margin percentage must be between 5% and 30%. Current value: {0}%").format(margin),
				frappe.ValidationError
			)

	def validate_non_negative(self):
		"""Ensure monetary and quantity values are non-negative."""
		numeric_fields = [
			("freight", "Freight Charges"),
			("insurance", "Insurance Charges"),
			("packing_charges", "Packing Charges"),
			("other_charges", "Other Charges"),
			("margin_percentage", "Margin Percentage"),
		]
		for field, label in numeric_fields:
			val = flt(self.get(field))
			if val < 0:
				frappe.throw(_("{0} cannot be negative.").format(label))

		if hasattr(self, "items") and self.items:
			for i, item in enumerate(self.items, 1):
				if flt(item.quantity) <= 0:
					frappe.throw(_("Row #{0}: Quantity must be greater than zero.").format(i))
				if flt(item.base_rate) < 0:
					frappe.throw(_("Row #{0}: Rate cannot be negative.").format(i))

	def set_parties_and_metadata(self):
		"""Set default parties, bank details, and metadata."""
		self.seller = "Sarveksha Realty and Inframine LLP"
		if not self.seller_address:
			self.seller_address = (
				"No 303, Sparsh CHS, Plot no 101,102\n"
				"Sect 44, Sea woods, Nerul\n"
				"Navi Mumbai: 400706"
			)
		if not self.seller_gstin:
			self.seller_gstin = "27AAAFS2557J1ZB"
		if not self.seller_pan:
			self.seller_pan = "AAAFS2557J"
		if not self.seller_iec:
			self.seller_iec = "AFTFS2557J"

		if not self.notify_party:
			self.notify_party = (
				"Globe Multitrade & Service LLC\n"
				"Office No. 112, AL Jabri Building,\n"
				"Industrial Area, Sharjah (UAE)"
			)

		if not self.pi_number and not self.is_new():
			self.pi_number = self.name

		if self.is_new() or not self.prepared_by:
			self.prepared_by = frappe.session.user

		# Default SRI banking credentials as per standard contract datasets
		if not self.beneficiary_name:
			self.beneficiary_name = "SARVEKSHA REALTY AND INFRAMINE LLP"
		if not self.beneficiary_acc_no:
			self.beneficiary_acc_no = "409002556124"
		if not self.beneficiary_bank:
			self.beneficiary_bank = "RBL Bank Ltd"
		if not self.beneficiary_swift:
			self.beneficiary_swift = "RATNINBBXXX"
		if not self.nostro_bank:
			self.nostro_bank = "STANDARD CHARTERED BANK"
		if not self.nostro_swift:
			self.nostro_swift = "SCBLUS33XXX"

	def calculate_totals(self):
		"""
		Calculates item totals, adds manual logistics, applies 5-30% margin,
		and computes grand total payable.
		"""
		total_items = 0.0
		if hasattr(self, "items") and self.items:
			for item in self.items:
				qty = flt(item.quantity) or 1.0
				rate = flt(item.base_rate) or 0.0
				item.amount = flt(qty * rate, 2)
				total_items += item.amount

		self.total_item_amount = flt(total_items, 2)

		# Logistics costs are entered manually (never auto-fetched from PO)
		freight = flt(self.freight)
		insurance = flt(self.insurance)
		packing = flt(self.packing_charges)
		other = flt(self.other_charges)
		self.total_logistics = flt(freight + insurance + packing + other, 2)

		# SRI Margin (5% - 30%) applied on total items + logistics
		margin_pct = flt(self.margin_percentage) or 5.0
		base_for_margin = self.total_item_amount + self.total_logistics
		self.margin_amount = flt(base_for_margin * (margin_pct / 100.0), 2)

		# Grand Total = Base Goods + Logistics + Margin
		self.grand_total = flt(self.total_item_amount + self.total_logistics + self.margin_amount, 2)

		# Advance calculations
		adv_pct = flt(self.advance_percentage) if self.advance_percentage is not None else 100.0
		self.advance_amount = flt(self.grand_total * (adv_pct / 100.0), 2)

		# Amount in words
		try:
			self.amount_in_words = money_in_words(self.grand_total, self.currency or "USD")
		except Exception:
			self.amount_in_words = f"{self.currency or 'USD'} {self.grand_total:,.2f}"

	def on_submit(self):
		self.db_set("status", "Issued")
		self.db_set("pi_number", self.name)

	def on_cancel(self):
		self.db_set("status", "Cancelled")


@frappe.whitelist()
def get_internal_po_details(internal_po):
	"""
	Fetches details from referenced Internal PO to populate the Proforma Invoice.
	Note: Logistics charges are intentionally NOT fetched automatically from the PO
	as per business requirement; they must be entered manually.
	"""
	if not internal_po:
		return {}

	po = frappe.get_doc("Vendor Purchase Order", internal_po)
	if po.po_type != "Internal PO":
		frappe.throw(
			_("Proforma Invoice can only reference an Internal PO (Child Company -> SRI). "
			  "{0} is a Vendor PO and is not permitted.").format(internal_po),
			frappe.ValidationError
		)

	# Fetch company destination/ports
	company_doc = frappe.get_doc("Company", po.company) if po.company else None
	country = (company_doc.country if company_doc else "") or "Botswana"

	items_data = []
	if hasattr(po, "items") and po.items:
		for item in po.items:
			items_data.append({
				"equipment": item.equipment or "",
				"item_description": item.equipment_name or item.equipment or "",
				"make_model": item.brand or item.manufacturer or "",
				"hsn_code": item.hsn_code or "",
				"unit": item.unit or "Nos",
				"quantity": item.quantity or 1,
				"base_rate": item.rate or 0,
				"amount": flt(item.quantity * item.rate, 2),
			})

	return {
		"po_reference_no": po.ref_number or po.name,
		"po_date": po.po_date,
		"buyer": po.company,
		"buyer_address": po.company_address or "",
		"notify_party": "Globe Multitrade & Service LLC\nOffice No. 112, AL Jabri Building,\nIndustrial Area, Sharjah (UAE)",
		"currency": po.currency or "USD",
		"port_of_loading": "Mundra",
		"port_of_discharge": po.port or (company_doc.custom_default_port if company_doc else "") or "Durban",
		"final_destination": f"{country}",
		"margin_percentage": flt(po.internal_margin_percentage) if flt(po.internal_margin_percentage) >= 5.0 else 5.0,
		# Logistics intentionally defaulted to 0.0 — manual entry required
		"freight": 0.0,
		"insurance": 0.0,
		"packing_charges": 0.0,
		"other_charges": 0.0,
		"advance_percentage": flt(po.advance_percentage) if po.advance_percentage else 100.0,
		"items": items_data,
	}


@frappe.whitelist()
def create_proforma_invoice_from_internal_po(internal_po_name):
	"""
	Factory function to instantiate and save a Proforma Invoice directly from an Internal PO.
	Used by Python workflows, API endpoints, and form action buttons.
	If an active PI already exists for this Internal PO, returns the existing document.
	"""
	existing = frappe.db.get_value(
		"Proforma Invoice",
		{"internal_po": internal_po_name, "docstatus": ["!=", 2]},
		"name",
	)
	if existing:
		return frappe.get_doc("Proforma Invoice", existing)

	details = get_internal_po_details(internal_po_name)
	pi = frappe.new_doc("Proforma Invoice")
	pi.internal_po = internal_po_name
	for k, v in details.items():
		if k != "items":
			setattr(pi, k, v)
	if details.get("items"):
		for itm in details["items"]:
			pi.append("items", itm)
	pi.insert()
	return pi


@frappe.whitelist()
def cancel_proforma_invoice(pi_name, reason=""):
	"""
	Cancel a submitted Proforma Invoice (docstatus 1 → 2).

	Steps:
	  1. Permission check — only authorized roles can cancel.
	  2. Validate the PI is submitted (docstatus == 1).
	  3. Set docstatus = 2 (Cancelled) and status = 'Cancelled'.
	  4. Clear the linked Internal PO's proforma_invoice reference.
	  5. Record an audit comment with the cancellation reason.
	"""
	if not frappe.has_permission("Proforma Invoice", "cancel"):
		frappe.throw(
			_("You do not have permission to cancel a Proforma Invoice."),
			frappe.PermissionError,
		)

	pi = frappe.get_doc("Proforma Invoice", pi_name)

	if pi.docstatus != 1:
		frappe.throw(
			_("Only submitted Proforma Invoices (docstatus = 1) can be cancelled. "
			  "Current docstatus: {0}").format(pi.docstatus),
			frappe.ValidationError,
		)

	# Cancel via frappe's built-in cancel (increments modified, sets docstatus = 2)
	pi.flags.ignore_permissions = True
	pi.cancel()

	# Explicitly set status field so form displays correctly
	frappe.db.set_value("Proforma Invoice", pi_name, "status", "Cancelled")

	# ── Clear linked Internal PO reference ──────────────────────────────────
	if pi.internal_po:
		try:
			po = frappe.get_doc("Vendor Purchase Order", pi.internal_po)
			if hasattr(po, "linked_proforma_invoice") and po.linked_proforma_invoice == pi_name:
				po.linked_proforma_invoice = None
				po.flags.ignore_permissions = True
				po.flags.ignore_immutable_validation = True
				po.save(ignore_permissions=True)
		except Exception:
			# PO may not have the field — safe to ignore
			pass

	# ── Audit log ────────────────────────────────────────────────────────────
	reason_text = reason or "No reason provided"
	frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Info",
		"reference_doctype": "Proforma Invoice",
		"reference_name": pi_name,
		"content": _("Proforma Invoice cancelled by {0}. Reason: {1}").format(
			frappe.session.user, reason_text
		),
	}).insert(ignore_permissions=True)

	frappe.msgprint(
		_("Proforma Invoice {0} has been cancelled successfully.").format(pi_name),
		title=_("PI Cancelled"),
		indicator="orange",
	)

	return {"status": "cancelled", "pi_name": pi_name}
