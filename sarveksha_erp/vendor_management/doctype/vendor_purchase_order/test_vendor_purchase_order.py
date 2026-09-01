import frappe
from unittest.mock import patch
from frappe.tests.utils import FrappeTestCase
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



class TestVendorPurchaseOrder(FrappeTestCase):
	"""
	Integration tests for VendorPurchaseOrder workflow, approval panel, and permissions.
	"""

	def test_internal_po_entity_policy(self):
		"""Internal POs may target SRI only and must originate from a child company."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.po_type = "Internal PO"
		po.company = "Sarveksha Realty and Inframine LLP"
		po.vendor = "SRI Supplier"

		with patch.object(frappe.db, "get_value", return_value="Sarveksha Realty and Inframine LLP"):
			with self.assertRaises(frappe.ValidationError):
				po.validate_entity_policy()

		po.company = "Sarveksha Child Entity"
		with patch.object(frappe.db, "get_value", return_value="External Supplier"):
			with self.assertRaises(frappe.ValidationError):
				po.validate_entity_policy()

	def test_external_po_allows_active_supplier(self):
		"""External POs remain available to every company when the supplier is active."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.po_type = "Vendor PO"
		po.company = "Sarveksha Realty and Inframine LLP"
		po.vendor = "Authorized Overseas Supplier"

		with patch.object(frappe.db, "get_value", return_value=0):
			po.validate_entity_policy()

	def test_external_po_requires_complete_distinct_quotations(self):
		"""Forwarding an External PO requires a comparison sheet and three different quotes."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.po_type = "Vendor PO"
		po.workflow_state = "Generated (Yet to be Verified)"
		po.get_doc_before_save = lambda: frappe._dict(workflow_state="Draft")

		with self.assertRaises(frappe.ValidationError):
			po.validate_quotation_governance()

		po.quotation_comparison_sheet = "/files/comparison.pdf"
		po.quotations = [
			frappe._dict(supplier="Supplier A"),
			frappe._dict(supplier="Supplier B"),
			frappe._dict(supplier="Supplier C"),
		]
		po.validate_quotation_governance()

		po.quotations[2].supplier = "Supplier A"
		with self.assertRaises(frappe.ValidationError):
			po.validate_quotation_governance()

	def test_quotation_evidence_is_immutable_after_draft(self):
		"""Reviewers can see quotation evidence but cannot modify it after Draft."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.get_doc_before_save = lambda: frappe._dict(workflow_state="Generated (Yet to be Verified)")
		po.has_value_changed = lambda fieldname: fieldname == "quotations"

		with self.assertRaises(frappe.PermissionError):
			po.validate_quotation_audit_integrity()

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

	def test_get_workflow_activity_history(self):
		"""Verify that get_workflow_activity_history returns correct workflow transitions."""
		from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order import get_workflow_activity_history

		po = frappe.new_doc("Vendor Purchase Order")
		po.company = "_Test Company"
		po.vendor = "_Test Supplier"
		po.quantity = 1.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)

		# Transition to Generated (Yet to be Verified)
		po.workflow_state = "Generated (Yet to be Verified)"
		po.save(ignore_permissions=True)

		# Add a manual comment
		comment = frappe.new_doc("Comment")
		comment.comment_type = "Comment"
		comment.reference_doctype = "Vendor Purchase Order"
		comment.reference_name = po.name
		comment.content = "Please verify the shipment container size."
		comment.insert(ignore_permissions=True)

		# Fetch history
		history = get_workflow_activity_history(po.name)
		
		# Assert at least two entries: Draft -> Generated and the manual comment
		self.assertTrue(len(history) >= 2)
		self.assertEqual(history[0]["state"], "Draft")
		
		comment_entry = next((item for item in history if "Please verify the shipment container" in item["remarks"]), None)
		self.assertIsNotNone(comment_entry)

		# Clean up
		frappe.delete_doc("Vendor Purchase Order", po.name, ignore_permissions=True)

	def approve_vpo(self, po):
		"""Helper to transition a PO to Approved state step by step."""
		po.workflow_state = "Generated (Yet to be Verified)"
		po.save(ignore_permissions=True)
		po.workflow_state = "Verified (Yet to be approved)"
		po.save(ignore_permissions=True)
		po.workflow_state = "Approved"
		po.docstatus = 1
		po.save(ignore_permissions=True)

	def test_ref_number_generation(self):
		"""Verify that a distinct, sequential reference number with REF substring is generated on approval."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.company = "_Test Company"
		po.vendor = "_Test Supplier"
		po.quantity = 1.0
		po.rate = 100.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)

		self.assertIsNone(po.ref_number)

		# Transition Draft -> Generated
		po.workflow_state = "Generated (Yet to be Verified)"
		po.save(ignore_permissions=True)
		self.assertIsNone(po.ref_number)

		# Transition Generated -> Verified
		po.workflow_state = "Verified (Yet to be approved)"
		po.save(ignore_permissions=True)
		self.assertIsNone(po.ref_number)

		# Transition Verified -> Approved
		po.workflow_state = "Approved"
		po.docstatus = 1
		po.save(ignore_permissions=True)

		self.assertIsNotNone(po.ref_number)
		self.assertTrue("REF" in po.ref_number)
		self.assertTrue(po.ref_number.startswith("SRIPOREF-"))

		# Clean up
		po.docstatus = 2
		po.save(ignore_permissions=True)
		frappe.delete_doc("Vendor Purchase Order", po.name, ignore_permissions=True)

	def test_ref_number_uniqueness(self):
		"""Verify uniqueness of reference numbers and that duplicates raise UniqueValidationError."""
		po1 = frappe.new_doc("Vendor Purchase Order")
		po1.company = "_Test Company"
		po1.vendor = "_Test Supplier"
		po1.quantity = 1.0
		po1.rate = 100.0
		po1.exchange_rate = 1.0
		po1.workflow_state = "Draft"
		po1.save(ignore_permissions=True)
		self.approve_vpo(po1)

		po2 = frappe.new_doc("Vendor Purchase Order")
		po2.company = "_Test Company"
		po2.vendor = "_Test Supplier"
		po2.quantity = 1.0
		po2.rate = 100.0
		po2.exchange_rate = 1.0
		po2.workflow_state = "Draft"
		po2.save(ignore_permissions=True)
		
		# Transition po2 to Approved but KEEP docstatus=0 (Draft) so it doesn't trigger UpdateAfterSubmitError on edit
		po2.workflow_state = "Generated (Yet to be Verified)"
		po2.save(ignore_permissions=True)
		po2.workflow_state = "Verified (Yet to be approved)"
		po2.save(ignore_permissions=True)
		po2.workflow_state = "Approved"
		po2.save(ignore_permissions=True)

		self.assertNotEqual(po1.ref_number, po2.ref_number)

		# Attempt to duplicate the reference number
		po2.ref_number = po1.ref_number
		self.assertRaises(frappe.UniqueValidationError, po2.save, ignore_permissions=True)

		# Clean up
		po1.docstatus = 2
		po1.save(ignore_permissions=True)
		frappe.delete_doc("Vendor Purchase Order", po1.name, ignore_permissions=True)
		frappe.delete_doc("Vendor Purchase Order", po2.name, ignore_permissions=True)

	def test_ref_number_amendment(self):
		"""Verify amendment handling correctly appends -1, -2 suffixes to the reference number."""
		po = frappe.new_doc("Vendor Purchase Order")
		po.company = "_Test Company"
		po.vendor = "_Test Supplier"
		po.quantity = 1.0
		po.rate = 100.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)
		self.approve_vpo(po)

		ref_original = po.ref_number
		self.assertIsNotNone(ref_original)

		# Cancel the original PO to allow amendment
		po.docstatus = 2
		po.save(ignore_permissions=True)

		# Create first amendment
		po_amended = frappe.copy_doc(po)
		po_amended.name = None
		po_amended.amended_from = po.name
		po_amended.docstatus = 0
		po_amended.workflow_state = "Draft"
		po_amended.ref_number = None
		po_amended.save(ignore_permissions=True)
		self.approve_vpo(po_amended)

		self.assertEqual(po_amended.ref_number, f"{ref_original}-1")

		# Cancel the first amendment to allow second amendment
		po_amended.docstatus = 2
		po_amended.save(ignore_permissions=True)

		# Create second amendment (amendment of the amendment)
		po_amended_2 = frappe.copy_doc(po_amended)
		po_amended_2.name = None
		po_amended_2.amended_from = po_amended.name
		po_amended_2.docstatus = 0
		po_amended_2.workflow_state = "Draft"
		po_amended_2.ref_number = None
		po_amended_2.save(ignore_permissions=True)
		self.approve_vpo(po_amended_2)

		self.assertEqual(po_amended_2.ref_number, f"{ref_original}-2")

		# Clean up (in reverse order to avoid LinkExistsError)
		po_amended_2.docstatus = 2
		po_amended_2.save(ignore_permissions=True)
		frappe.delete_doc("Vendor Purchase Order", po_amended_2.name, ignore_permissions=True)
		frappe.delete_doc("Vendor Purchase Order", po_amended.name, ignore_permissions=True)
		frappe.delete_doc("Vendor Purchase Order", po.name, ignore_permissions=True)

