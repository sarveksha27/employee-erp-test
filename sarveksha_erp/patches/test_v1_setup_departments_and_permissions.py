import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch
from types import SimpleNamespace

from sarveksha_erp.patches import v1_setup_departments_and_permissions as security_setup
from sarveksha_erp.payment_tracking.payment_entry_workflow import validate_payment_entry_workflow


class TestDepartmentAndPermissionSetup(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		security_setup.execute()

	def test_departments_have_cost_centers_and_default_approval_roles(self):
		company_abbr = frappe.db.get_value("Company", security_setup.PRIMARY_COMPANY, "abbr")
		for department, approval_role in (
			("Procurement", "PO Approver"),
			("Accounts", "Accounts Manager"),
		):
			department_doc = frappe.get_doc("Department", f"{department} - {company_abbr}")
			self.assertEqual(department_doc.company, security_setup.PRIMARY_COMPANY)
			self.assertEqual(department_doc.parent_department, "All Departments")
			self.assertEqual(department_doc.custom_default_approval_role, approval_role)
			self.assertTrue(frappe.db.exists("Cost Center", department_doc.custom_default_cost_center))

	def test_setup_is_idempotent(self):
		security_setup.execute()
		self.assertEqual(
			frappe.db.count("Department", {"company": security_setup.PRIMARY_COMPANY, "department_name": "Procurement"}),
			1,
		)
		self.assertEqual(
			frappe.db.count("Department", {"company": security_setup.PRIMARY_COMPANY, "department_name": "Accounts"}),
			1,
		)

	def test_supplier_and_bank_fields_require_permission_level_one(self):
		for fieldname in security_setup.BANKING_SUPPLIER_FIELDS:
			self.assertEqual(frappe.get_meta("Supplier").get_field(fieldname).permlevel, 1)
		for fieldname in ("bank_account_no", "iban"):
			self.assertEqual(frappe.get_meta("Bank Account").get_field(fieldname).permlevel, 1)
		for fieldname in security_setup.SENSITIVE_FIELDS["Vendor Purchase Order"]:
			self.assertEqual(frappe.get_meta("Vendor Purchase Order").get_field(fieldname).permlevel, 1)

	def test_permission_rows_are_isolated_by_role(self):
		for doctype in ("Payment Entry", "Journal Entry"):
			for role in security_setup.PROCUREMENT_ROLES:
				row = frappe.db.get_value(
					"Custom DocPerm",
					{"parent": doctype, "role": role, "permlevel": 0},
					["read", "write", "create"],
					as_dict=True,
				)
				self.assertEqual((row.read, row.write, row.create), (0, 0, 0))

		for doctype in ("Supplier", "Bank Account", "Vendor Purchase Order"):
			for role in ("Accounts Manager", "System Manager"):
				row = frappe.db.get_value(
					"Custom DocPerm",
					{"parent": doctype, "role": role, "permlevel": 1},
					["read", "write"],
					as_dict=True,
				)
				self.assertEqual((row.read, row.write), (1, 1))

		clerk_permission = frappe.db.get_value(
			"Custom DocPerm", {"parent": "Payment Entry", "role": "Accounts Clerk", "permlevel": 0}, "submit"
		)
		self.assertEqual(clerk_permission, 0)
		system_manager_supplier = frappe.db.get_value(
			"Custom DocPerm",
			{"parent": "Supplier", "role": "System Manager", "permlevel": 0},
			["create", "delete"],
			as_dict=True,
		)
		self.assertEqual((system_manager_supplier.create, system_manager_supplier.delete), (1, 1))
		self.assertEqual(
			frappe.db.count(
				"Custom DocPerm",
				{"parent": "Payment Entry", "role": "PO Generator", "permlevel": 0},
			),
			1,
		)

	def test_payment_entry_is_blocked_for_procurement_roles(self):
		for role in security_setup.PROCUREMENT_ROLES:
			with patch.object(frappe, "get_roles", return_value=[role]):
				self.assertFalse(
					security_setup.payment_entry_has_permission(None, "read", user="procurement@example.com")
				)
				with self.assertRaises(frappe.PermissionError):
					security_setup.payment_entry_permission_query_conditions(user="procurement@example.com")

		with patch.object(frappe, "get_roles", return_value=["Accounts Clerk"]):
			self.assertIsNone(
				security_setup.payment_entry_has_permission(None, "read", user="clerk@example.com")
			)
			self.assertEqual(
				security_setup.payment_entry_permission_query_conditions(user="clerk@example.com"),
				"",
			)

	def test_seeded_procurement_user_is_denied_payment_entry_list(self):
		user = "po_generator@sarveksha.com"
		if not frappe.db.exists("User", user):
			self.skipTest("Seeded PO Generator user is unavailable")
		self.assertIn("PO Generator", frappe.get_roles(user))
		with self.assertRaises(frappe.PermissionError):
			security_setup.payment_entry_permission_query_conditions(user=user)

	def test_seeded_accounts_clerk_cannot_submit_payment_entry(self):
		user = "finance_clerk1@sarveksha.com"
		if not frappe.db.exists("User", user):
			self.skipTest("Seeded Accounts Clerk user is unavailable")
		original_user = frappe.session.user if frappe.session else "Administrator"
		try:
			frappe.set_user(user)
			self.assertIn("Accounts Clerk", frappe.get_roles(user))
			self.assertIn("Accounts User", frappe.get_roles(user))
			with self.assertRaises(frappe.PermissionError):
				validate_payment_entry_workflow(
					SimpleNamespace(get=lambda fieldname: "Draft" if fieldname == "workflow_state" else None),
					"before_submit",
				)
		finally:
			frappe.set_user(original_user)

	def test_supplier_banking_rpc_redacts_non_finance_roles(self):
		response = {
			"custom_bank_name": "Bank",
			"custom_account_number": "123456",
			"custom_ifsc": "IFSC123",
			"vendor_address": "Address",
		}
		method = (
			"sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order"
			".get_supplier_payment_details"
		)
		original_user = frappe.session.user if frappe.session else "Administrator"
		try:
			frappe.set_user("po_generator@example.com")
			with patch.object(frappe, "get_roles", return_value=["PO Generator"]), patch(
				method, side_effect=lambda supplier: dict(response)
			):
				result = security_setup.get_supplier_payment_details("SUPPLIER-1")
			self.assertEqual(result["custom_account_number"], "")
			self.assertEqual(result["custom_ifsc"], "")
			self.assertEqual(result["vendor_address"], "Address")

			frappe.set_user("accounts_manager@example.com")
			with patch.object(frappe, "get_roles", return_value=["Accounts Manager"]), patch(
				method, side_effect=lambda supplier: dict(response)
			):
				result = security_setup.get_supplier_payment_details("SUPPLIER-1")
			self.assertEqual(result["custom_account_number"], "123456")
		finally:
			frappe.set_user(original_user)