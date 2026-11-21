from types import SimpleNamespace
from unittest.mock import Mock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order import (
	VendorPurchaseOrder,
	cancel_vendor_purchase_order,
)


MODULE = "sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order"


class TestInternalPurchaseOrderRequirements(FrappeTestCase):
	def test_internal_po_does_not_require_payment_schedule(self):
		doc = SimpleNamespace(po_type="Internal PO", workflow_state="Approved")

		VendorPurchaseOrder.validate_payment_terms_schedule(doc)

	def test_cancel_requires_a_reason(self):
		doc = SimpleNamespace(workflow_state="Approved", cancellation_reason="", name="VPO-TEST")

		with self.assertRaises(frappe.ValidationError):
			VendorPurchaseOrder.before_cancel(doc)

	def test_cancel_is_limited_to_approved_pos(self):
		doc = SimpleNamespace(
			workflow_state="Generated (Yet to be Verified)",
			cancellation_reason="No longer required",
			name="VPO-TEST",
		)

		with self.assertRaises(frappe.ValidationError):
			VendorPurchaseOrder.before_cancel(doc)

	def test_cancel_blocks_when_an_active_pi_exists(self):
		doc = SimpleNamespace(
			workflow_state="Approved",
			cancellation_reason="Order withdrawn",
			name="VPO-TEST",
		)
		with patch(f"{MODULE}.frappe.db.exists", return_value="PI-TEST"):
			with self.assertRaisesRegex(frappe.ValidationError, "Cancel Proforma Invoice"):
				VendorPurchaseOrder.before_cancel(doc)


class TestCancelVendorPurchaseOrder(FrappeTestCase):
	def _approved_po(self):
		return SimpleNamespace(
			name="VPO-TEST",
			docstatus=1,
			workflow_state="Approved",
			cancellation_reason="",
			flags=SimpleNamespace(),
			check_permission=Mock(),
			save=Mock(),
			cancel=Mock(),
		)

	def test_cancel_requires_a_reason_before_loading_po(self):
		with patch(f"{MODULE}.frappe.get_doc") as get_doc:
			with self.assertRaises(frappe.ValidationError):
				cancel_vendor_purchase_order("VPO-TEST", "  ")

		get_doc.assert_not_called()

	def test_cancel_checks_doctype_permission(self):
		with patch(f"{MODULE}.frappe.get_doc", return_value=self._approved_po()), patch(
			f"{MODULE}.frappe.has_permission", return_value=False
		):
			with self.assertRaises(frappe.PermissionError):
				cancel_vendor_purchase_order("VPO-TEST", "Order withdrawn")

	def test_successful_cancel_saves_reason_and_audit_comment(self):
		po = self._approved_po()
		comment = SimpleNamespace(insert=Mock())
		with patch(f"{MODULE}.frappe.get_doc", side_effect=[po, comment]), patch(
			f"{MODULE}.frappe.has_permission", return_value=True
		):
			result = cancel_vendor_purchase_order("VPO-TEST", "  Order withdrawn  ")

		self.assertEqual(result, {"status": "cancelled", "po_name": "VPO-TEST"})
		self.assertEqual(po.cancellation_reason, "Order withdrawn")
		po.save.assert_called_once_with(ignore_permissions=True)
		po.cancel.assert_called_once()
		comment.insert.assert_called_once_with(ignore_permissions=True)
