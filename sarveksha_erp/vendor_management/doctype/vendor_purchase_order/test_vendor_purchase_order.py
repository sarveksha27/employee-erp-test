import frappe
from frappe.tests import IntegrationTestCase
from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order import has_permission

# Mock _get_fiscal_years to ignore company constraints in test runs
import erpnext.accounts.utils
def mock_get_fiscal_years(company=None):
    return frappe.db.get_all(
        "Fiscal Year",
        fields=["name", "year_start_date", "year_end_date"],
        filters={"disabled": 0},
        order_by="year_start_date desc"
    )
erpnext.accounts.utils._get_fiscal_years = mock_get_fiscal_years



class IntegrationTestVendorPurchaseOrder(IntegrationTestCase):
	"""
	Integration tests for VendorPurchaseOrder workflow, approval panel, and permissions.
	"""

	def test_print_permission_restriction(self):
		"""Verify print permission is rejected for non-approved states and restricted by role."""
		original_get_roles = frappe.get_roles
		def mock_get_roles(username):
			if username == "Administrator":
				return ["Administrator", "System Manager"]
			elif username == "po_generator@sarveksha.com":
				return ["PO Generator", "Desk User"]
			elif username == "po_verifier@sarveksha.com":
				return ["PO Verifier", "Desk User"]
			elif username == "po_approver@sarveksha.com":
				return ["PO Approver", "Desk User"]
			return original_get_roles(username)

		frappe.get_roles = mock_get_roles
		try:
			doc = frappe.new_doc("Vendor Purchase Order")
			doc.workflow_state = "Draft"
			
			# Test for admin user role
			is_allowed = has_permission(doc, ptype="print", user="Administrator")
			self.assertTrue(is_allowed)

			# Non-admin / unauthorized user on Draft PO should return False
			is_allowed_draft = has_permission(doc, ptype="print", user="po_generator@sarveksha.com")
			self.assertFalse(is_allowed_draft)

			# Approved state should allow print for PO Generator
			doc.workflow_state = "Approved"
			is_allowed_approved = has_permission(doc, ptype="print", user="po_generator@sarveksha.com")
			self.assertTrue(is_allowed_approved)

			# Approved state should reject print for PO Verifier
			is_allowed_verifier = has_permission(doc, ptype="print", user="po_verifier@sarveksha.com")
			self.assertFalse(is_allowed_verifier)
		finally:
			frappe.get_roles = original_get_roles

	def test_audit_trail_tracking(self):
		"""Verify audit fields update correctly when workflow state changes."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.company = "_Test Company"
		po.vendor = "_Test Supplier"
		po.quantity = 1.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)

		# Simulate transition to Generated (Yet to be Verified)
		po.workflow_state = "Generated (Yet to be Verified)"
		po.save(ignore_permissions=True)

		# Simulate Verifier verification -> Verified (Yet to be approved)
		po.workflow_state = "Verified (Yet to be approved)"
		po.verifier_comments = "Verified items & pricing"
		po.save(ignore_permissions=True)

		self.assertEqual(po.verifier_status, "Verified")
		self.assertIsNotNone(po.verified_on)

		# Simulate Approver returning to Verifier due to discrepancy
		po.workflow_state = "Generated (Yet to be Verified)"
		po.approver_comments = "Rate discrepancy on line 1"
		po.save(ignore_permissions=True)

		self.assertEqual(po.approver_status, "Returned to Verifier")
		self.assertIsNotNone(po.approved_on)

	def test_payment_status_modification_restriction(self):
		"""Verify only Procurement Manager (and admins) can modify payment status fields."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.company = "_Test Company"
		po.vendor = "_Test Supplier"
		po.quantity = 1.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		po.payment_status = "Pending"
		po.save(ignore_permissions=True)

		# Mock roles to PO Generator (non-authorized role)
		original_get_roles = frappe.get_roles
		try:
			frappe.get_roles = lambda username: ["PO Generator"]
			po.payment_status = "Advance Paid"
			self.assertRaises(frappe.PermissionError, po.save, ignore_permissions=True)
		finally:
			frappe.get_roles = original_get_roles

		# Mock roles to Procurement Manager (authorized role)
		try:
			frappe.get_roles = lambda username: ["Procurement Manager"]
			po.reload()
			po.payment_status = "Advance Paid"
			po.save(ignore_permissions=True)
			self.assertEqual(po.payment_status, "Advance Paid")
		finally:
			frappe.get_roles = original_get_roles

	def test_creation_restrictions_for_verifiers_and_approvers(self):
		"""Verify that PO Verifiers and PO Approvers cannot create a new Purchase Order."""
		original_user = frappe.session.user
		try:
			# Test as PO Verifier
			frappe.set_user("po_verifier@sarveksha.com")
			po = frappe.new_doc("Vendor Purchase Order")
			po.company = "_Test Company"
			po.vendor = "_Test Supplier"
			po.quantity = 1.0
			po.exchange_rate = 1.0
			po.workflow_state = "Draft"
			self.assertRaises(frappe.PermissionError, po.insert)

			# Test as PO Approver
			frappe.set_user("po_approver@sarveksha.com")
			po_app = frappe.new_doc("Vendor Purchase Order")
			po_app.company = "_Test Company"
			po_app.vendor = "_Test Supplier"
			po_app.quantity = 1.0
			po_app.exchange_rate = 1.0
			po_app.workflow_state = "Draft"
			
			with self.assertRaises(frappe.PermissionError) as context:
				po_app.insert()
			
			# Check that additional guidelines are present in the error message
			self.assertIn("As an Approver, your role is strictly to review, verify", str(context.exception))
		finally:
			frappe.set_user(original_user)

	def test_dynamic_uom_creation(self):
		"""Verify that UOMs used in child items or parent are dynamically created or handled gracefully."""
		# Choose a non-existent UOM name
		test_uom = "SuperSpecialUOM"
		
		# Ensure it doesn't exist
		if frappe.db.exists("UOM", test_uom):
			frappe.delete_doc("UOM", test_uom, ignore_permissions=True)
		
		po = frappe.new_doc("Vendor Purchase Order")
		po.company = "_Test Company"
		po.vendor = "_Test Supplier"
		po.quantity = 1.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		
		# Append child item with this special UOM
		po.append("items", {
			"equipment": "_Test Equipment 1" if frappe.db.exists("Equipment", "_Test Equipment 1") else "EQ-03281",
			"equipment_name": "Cone Crusher Assembly Model HP400",
			"hsn_code": "84742010",
			"quantity": 1.0,
			"rate": 100000.0,
			"discount_percent": 0.0,
			"gst_percentage": 18.0,
			"unit": test_uom
		})
		
		# Saving should dynamically create the UOM and not throw a LinkValidationError
		po.save(ignore_permissions=True)
		
		# Assert UOM now exists
		self.assertTrue(frappe.db.exists("UOM", test_uom))
		
		# Clean up
		frappe.delete_doc("Vendor Purchase Order", po.name, ignore_permissions=True)
		frappe.delete_doc("UOM", test_uom, ignore_permissions=True)
