from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from sarveksha_erp.vendor_management.doctype.proforma_invoice.proforma_invoice import (
	ProformaInvoice,
	_get_approved_internal_po,
	_get_pi_naming_series,
)


MODULE = "sarveksha_erp.vendor_management.doctype.proforma_invoice.proforma_invoice"


class TestInternalProformaInvoice(FrappeTestCase):
	def _po(self, po_type="Internal PO", workflow_state="Approved", docstatus=1):
		return SimpleNamespace(
			po_type=po_type,
			workflow_state=workflow_state,
			docstatus=docstatus,
			check_permission=lambda permission: None,
		)

	def test_proforma_invoice_requires_an_internal_po(self):
		with self.assertRaises(frappe.ValidationError):
			_get_approved_internal_po(None)

	def test_external_po_cannot_be_invoiced(self):
		with patch(f"{MODULE}.frappe.get_doc", return_value=self._po(po_type="Vendor PO")):
			with self.assertRaisesRegex(frappe.ValidationError, "only be generated from an Internal PO"):
				_get_approved_internal_po("VPO-TEST")

	def test_internal_po_must_be_approved_and_submitted(self):
		po = self._po(workflow_state="Verified (Yet to be approved)", docstatus=0)
		with patch(f"{MODULE}.frappe.get_doc", return_value=po):
			with self.assertRaisesRegex(frappe.ValidationError, "must be approved and submitted"):
				_get_approved_internal_po("VPO-TEST")

	def test_approved_submitted_internal_po_is_accepted(self):
		po = self._po()
		with patch(f"{MODULE}.frappe.get_doc", return_value=po):
			self.assertIs(_get_approved_internal_po("VPO-TEST"), po)

	def test_botswana_pi_uses_the_company_fiscal_year_series(self):
		with patch(f"{MODULE}.frappe.db.get_value", return_value="Botswana"):
			series = _get_pi_naming_series("Sarveksha Botswana", "2026-10-09")

		self.assertEqual(series, "SRI/BOT/26-27/.###")

	def test_pi_grand_total_includes_margin_once(self):
		pi = SimpleNamespace(
			items=[SimpleNamespace(quantity=1, base_rate=1000, amount=0)],
			freight=0,
			insurance=0,
			packing_charges=0,
			other_charges=0,
			margin_percentage=5,
			advance_percentage=100,
			currency="USD",
		)

		ProformaInvoice.calculate_totals(pi)

		self.assertEqual(pi.total_item_amount, 1000)
		self.assertEqual(pi.margin_amount, 50)
		self.assertEqual(pi.grand_total, 1050)
