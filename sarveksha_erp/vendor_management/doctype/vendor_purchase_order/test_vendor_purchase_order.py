import frappe
from frappe.tests import IntegrationTestCase
from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order import has_permission


class IntegrationTestVendorPurchaseOrder(IntegrationTestCase):
	"""
	Integration tests for VendorPurchaseOrder workflow, approval panel, and permissions.
	"""

	def test_print_permission_restriction(self):
		"""Verify print permission is rejected for non-approved states."""
		doc = frappe.new_doc("Vendor Purchase Order")
		doc.workflow_state = "Draft"
		
		# Test for non-admin user role
		is_allowed = has_permission(doc, ptype="print", user="Administrator")
		self.assertTrue(is_allowed)

		# Non-admin user on Draft PO should return False
		doc.workflow_state = "Draft"
		is_allowed_draft = has_permission(doc, ptype="print", user="Guest")
		self.assertFalse(is_allowed_draft)

		# Approved state should allow print
		doc.workflow_state = "Approved"
		is_allowed_approved = has_permission(doc, ptype="print", user="Guest")
		self.assertTrue(is_allowed_approved)

	def test_audit_trail_tracking(self):
		"""Verify audit fields update correctly when workflow state changes."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)

		# Simulate transition to Pending Verification
		po.workflow_state = "Pending Verification"
		po.save(ignore_permissions=True)

		# Simulate Verifier verification -> Pending Approval
		po.workflow_state = "Pending Approval"
		po.verifier_comments = "Verified items & pricing"
		po.save(ignore_permissions=True)

		self.assertEqual(po.verifier_status, "Verified")
		self.assertIsNotNone(po.verified_on)

		# Simulate Approver returning to Verifier due to discrepancy
		po.workflow_state = "Pending Verification"
		po.approver_comments = "Rate discrepancy on line 1"
		po.save(ignore_permissions=True)

		self.assertEqual(po.approver_status, "Returned to Verifier")
		self.assertIsNotNone(po.approved_on)
