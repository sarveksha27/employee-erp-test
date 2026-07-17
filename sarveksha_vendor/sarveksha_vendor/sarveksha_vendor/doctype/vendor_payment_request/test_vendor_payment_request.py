import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

class TestVendorPaymentRequest(FrappeTestCase):
	def test_payment_request_validation(self):
		# Test that request with negative amount raises ValidationError
		req = frappe.new_doc("Vendor Payment Request")
		req.vendor = "Alpha Steel Industries"
		req.company = "Sarveksha Realty and Inframine LLP"
		req.amount = -500.00
		req.request_date = today()
		
		self.assertRaises(frappe.ValidationError, req.insert)

	def test_payment_request_auto_bank_assignment(self):
		# Test that default bank account is automatically assigned if not provided
		req = frappe.new_doc("Vendor Payment Request")
		req.vendor = "Alpha Steel Industries"
		req.company = "Sarveksha Realty and Inframine LLP"
		req.amount = 1000.00
		req.request_date = today()
		req.insert()
		
		# Confirm that default bank account was populated
		default_bank = frappe.db.get_value(
			"Vendor Bank",
			{"vendor": "Alpha Steel Industries", "company": "Sarveksha Realty and Inframine LLP", "is_default": 1},
			"name"
		)
		if default_bank:
			self.assertEqual(req.vendor_bank, default_bank)
