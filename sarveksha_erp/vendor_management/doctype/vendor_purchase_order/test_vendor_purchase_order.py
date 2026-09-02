import frappe
from frappe.utils import flt
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

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.test_company = frappe.db.get_value("Company", {}, "name") or "_Test Company"
		cls.test_vendor = frappe.db.get_value("Supplier", {}, "name") or "_Test Supplier"
		suppliers = [s.name for s in frappe.get_all("Supplier", limit=3)]
		cls.test_suppliers = suppliers if len(suppliers) >= 3 else [cls.test_vendor, cls.test_vendor, cls.test_vendor]

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
		po.po_type = "Internal PO"
		po.company = "Child Company India"
		po.vendor = "Sarveksha Realty and Inframine LLP"
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
		po.company = self.test_company
		po.vendor = self.test_vendor
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
			po.company = self.test_company
			po.vendor = self.test_vendor
			po.quantity = 1.0
			po.exchange_rate = 1.0
			po.workflow_state = "Draft"
			self.assertRaises(frappe.PermissionError, po.insert)

			# Test as PO Approver
			frappe.set_user("po_approver@sarveksha.com")
			po_app = frappe.new_doc("Vendor Purchase Order")
			po_app.company = self.test_company
			po_app.vendor = self.test_vendor
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
		po.company = self.test_company
		po.vendor = self.test_vendor
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
		po.company = self.test_company
		po.vendor = self.test_vendor
		po.po_type = "Vendor PO"
		po.quotation_comparison_sheet = "/files/sheet.pdf"
		po.append("quotations", {
			"supplier": self.test_suppliers[0],
			"quotation_reference": "Q-001",
			"quotation_date": "2026-08-30",
			"quotation_amount": 1000.0,
			"quotation_pdf": "/files/q1.pdf"
		})
		po.append("quotations", {
			"supplier": self.test_suppliers[1],
			"quotation_reference": "Q-002",
			"quotation_date": "2026-08-30",
			"quotation_amount": 1100.0,
			"quotation_pdf": "/files/q2.pdf"
		})
		po.append("quotations", {
			"supplier": self.test_suppliers[2],
			"quotation_reference": "Q-003",
			"quotation_date": "2026-08-30",
			"quotation_amount": 1200.0,
			"quotation_pdf": "/files/q3.pdf"
		})
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
		po.po_type = "Internal PO"
		po.company = "Child Company India"
		po.vendor = "Sarveksha Realty and Inframine LLP"
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
		po.po_type = "Internal PO"
		po.company = "Child Company India"
		po.vendor = "Sarveksha Realty and Inframine LLP"
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
		po1.po_type = "Internal PO"
		po1.company = "Child Company India"
		po1.vendor = "Sarveksha Realty and Inframine LLP"
		po1.quantity = 1.0
		po1.rate = 100.0
		po1.exchange_rate = 1.0
		po1.workflow_state = "Draft"
		po1.save(ignore_permissions=True)
		self.approve_vpo(po1)

		po2 = frappe.new_doc("Vendor Purchase Order")
		po2.po_type = "Internal PO"
		po2.company = "Child Company India"
		po2.vendor = "Sarveksha Realty and Inframine LLP"
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
		po.company = self.test_company
		po.vendor = self.test_vendor
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

	def test_pdf_merging_multi_file_concatenation(self):
		"""
		Multi-File Concatenation Test:
		Attach a multi-page PDF, PNG image, and JPEG image to a PO.
		Verify that merge_po_attachments successfully stitches them into a combined PDF.
		"""
		from io import BytesIO
		from PIL import Image
		from pypdf import PdfReader, PdfWriter
		from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.pdf_handler import merge_po_attachments

		test_company = frappe.db.get_value("Company", {}, "name") or "_Test Company"
		test_vendor = frappe.db.get_value("Supplier", {}, "name") or "_Test Supplier"

		# Create a dummy base PO PDF
		base_writer = PdfWriter()
		base_writer.add_blank_page(width=612, height=792)
		base_pdf_io = BytesIO()
		base_writer.write(base_pdf_io)
		base_pdf_bytes = base_pdf_io.getvalue()

		# Create a dummy PO record
		po = frappe.new_doc("Vendor Purchase Order")
		po.company = test_company
		po.vendor = test_vendor
		po.quantity = 1.0
		po.rate = 100.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)

		try:
			# 1. Attach a 2-page PDF document
			attach_pdf_writer = PdfWriter()
			attach_pdf_writer.add_blank_page(width=612, height=792)
			attach_pdf_writer.add_blank_page(width=612, height=792)
			attach_pdf_io = BytesIO()
			attach_pdf_writer.write(attach_pdf_io)

			file_pdf = frappe.get_doc({
				"doctype": "File",
				"file_name": "tech_spec.pdf",
				"attached_to_doctype": "Vendor Purchase Order",
				"attached_to_name": po.name,
				"content": attach_pdf_io.getvalue(),
				"is_private": 1
			})
			file_pdf.insert(ignore_permissions=True)

			# 2. Attach a PNG image
			png_img = Image.new("RGB", (300, 300), color="blue")
			png_io = BytesIO()
			png_img.save(png_io, format="PNG")

			file_png = frappe.get_doc({
				"doctype": "File",
				"file_name": "site_diagram.png",
				"attached_to_doctype": "Vendor Purchase Order",
				"attached_to_name": po.name,
				"content": png_io.getvalue(),
				"is_private": 1
			})
			file_png.insert(ignore_permissions=True)

			# 3. Attach a JPEG image
			jpg_img = Image.new("RGB", (300, 300), color="red")
			jpg_io = BytesIO()
			jpg_img.save(jpg_io, format="JPEG")

			file_jpg = frappe.get_doc({
				"doctype": "File",
				"file_name": "quotation_scan.jpg",
				"attached_to_doctype": "Vendor Purchase Order",
				"attached_to_name": po.name,
				"content": jpg_io.getvalue(),
				"is_private": 1
			})
			file_jpg.insert(ignore_permissions=True)

			# Merge attachments
			merged_bytes = merge_po_attachments(po, base_pdf_bytes)

			# Verify total page count: 1 base page + 2 PDF pages + 1 PNG page + 1 JPG page = 5 pages
			merged_reader = PdfReader(BytesIO(merged_bytes))
			self.assertEqual(len(merged_reader.pages), 5)
		finally:
			frappe.delete_doc("Vendor Purchase Order", po.name, ignore_permissions=True)

	def test_pdf_merging_corrupted_file_defensive_handling(self):
		"""
		Corrupted / Invalid File Handling Test:
		Attach an intentionally damaged PDF and an unsupported .txt file to a PO.
		Verify that the system logs the issue and generates the rest of the PO bundle without crashing.
		"""
		from io import BytesIO
		from pypdf import PdfReader, PdfWriter
		from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.pdf_handler import merge_po_attachments

		test_company = frappe.db.get_value("Company", {}, "name") or "_Test Company"
		test_vendor = frappe.db.get_value("Supplier", {}, "name") or "_Test Supplier"

		# Create a dummy base PO PDF
		base_writer = PdfWriter()
		base_writer.add_blank_page(width=612, height=792)
		base_pdf_io = BytesIO()
		base_writer.write(base_pdf_io)
		base_pdf_bytes = base_pdf_io.getvalue()

		po = frappe.new_doc("Vendor Purchase Order")
		po.company = test_company
		po.vendor = test_vendor
		po.quantity = 1.0
		po.rate = 100.0
		po.exchange_rate = 1.0
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)

		try:
			# Attach corrupted image (unsupported image bytes)
			file_corrupt = frappe.get_doc({
				"doctype": "File",
				"file_name": "corrupted_scan.png",
				"attached_to_doctype": "Vendor Purchase Order",
				"attached_to_name": po.name,
				"content": b"NOT_A_REAL_PNG_HEADER_CORRUPTED_BYTES",
				"is_private": 1
			})
			file_corrupt.insert(ignore_permissions=True)

			# Attach unsupported .txt file
			file_txt = frappe.get_doc({
				"doctype": "File",
				"file_name": "notes.txt",
				"attached_to_doctype": "Vendor Purchase Order",
				"attached_to_name": po.name,
				"content": b"Plain text content that should be skipped during PDF merge.",
				"is_private": 1
			})
			file_txt.insert(ignore_permissions=True)

			# Merge attachments - should NOT raise an unhandled exception
			merged_bytes = merge_po_attachments(po, base_pdf_bytes)

			# Base PDF page remains intact
			merged_reader = PdfReader(BytesIO(merged_bytes))
			self.assertEqual(len(merged_reader.pages), 1)

			# Verify Error Logs were created in Frappe
			logs = frappe.get_all(
				"Error Log",
				filters={
					"reference_doctype": "Vendor Purchase Order",
					"reference_name": po.name
				}
			)
			self.assertTrue(len(logs) >= 2)
		finally:
			frappe.delete_doc("Vendor Purchase Order", po.name, ignore_permissions=True)

	def test_logistics_expense_zero_and_negative_values(self):
		"""
		Phase 2 Task 1: Negative & Boundary Scenario Testing
		- Test zero values in logistics fields (freight=0, insurance=0, packing_charges=0, other_charges=0):
		  Verify document saves cleanly and calculates grand total correctly.
		- Test negative values in logistics fields (freight=-50, insurance=-20, packing_charges=-10, other_charges=-5):
		  Verify frappe.ValidationError is raised for each field.
		"""
		test_company = frappe.db.get_value("Company", {}, "name") or "_Test Company"
		test_vendor = frappe.db.get_value("Supplier", {}, "name") or "_Test Supplier"

		# 1. Zero values in logistics expense fields
		po = frappe.new_doc("Vendor Purchase Order")
		po.company = test_company
		po.vendor = test_vendor
		po.quantity = 2.0
		po.rate = 500.0
		po.exchange_rate = 1.0
		po.freight = 0.0
		po.insurance = 0.0
		po.packing_charges = 0.0
		po.other_charges = 0.0
		po.workflow_state = "Draft"
		po.save(ignore_permissions=True)

		self.assertEqual(flt(po.freight), 0.0)
		self.assertEqual(flt(po.insurance), 0.0)
		self.assertEqual(flt(po.packing_charges), 0.0)
		self.assertEqual(flt(po.other_charges), 0.0)
		self.assertTrue(flt(po.grand_total) > 0)

		# 2. Negative values in freight
		po.freight = -100.0
		self.assertRaises(frappe.ValidationError, po.save, ignore_permissions=True)
		po.freight = 0.0

		# Negative values in insurance
		po.insurance = -50.0
		self.assertRaises(frappe.ValidationError, po.save, ignore_permissions=True)
		po.insurance = 0.0

		# Negative values in packing_charges
		po.packing_charges = -25.0
		self.assertRaises(frappe.ValidationError, po.save, ignore_permissions=True)
		po.packing_charges = 0.0

		# Negative values in other_charges
		po.other_charges = -10.0
		self.assertRaises(frappe.ValidationError, po.save, ignore_permissions=True)
		po.other_charges = 0.0

		frappe.delete_doc("Vendor Purchase Order", po.name, ignore_permissions=True)



