import frappe
import unittest
from frappe.utils import today, add_days
from sarveksha_vendor.api import make_payment_entry

class TestVendorPayment(unittest.TestCase):
	def setUp(self):
		# Setup standard supplier if it doesn't exist
		if not frappe.db.exists("Supplier", "Apex Logistics"):
			supplier = frappe.new_doc("Supplier")
			supplier.supplier_name = "Apex Logistics"
			supplier.supplier_group = "All Supplier Groups"
			supplier.insert(ignore_permissions=True)
			
		# Setup standard company
		if not frappe.db.exists("Company", "Sarveksha Realty and Inframine LLP"):
			company = frappe.new_doc("Company")
			company.company_name = "Sarveksha Realty and Inframine LLP"
			company.default_currency = "INR"
			company.country = "India"
			company.insert(ignore_permissions=True)

	def test_payment_request_creation(self):
		pr = frappe.new_doc("Vendor Payment Request")
		pr.vendor = "Apex Logistics"
		pr.company = "Sarveksha Realty and Inframine LLP"
		pr.requested_amount = 1500.00
		pr.request_date = today()
		pr.status = "Draft"
		pr.insert(ignore_permissions=True)
		
		self.assertEqual(pr.requested_amount, 1500.00)
		self.assertEqual(pr.status, "Draft")
		self.assertTrue(pr.name.startswith("PAY-"))

	def test_vendor_contract_date_validation(self):
		contract = frappe.new_doc("Vendor Contract")
		contract.vendor = "Apex Logistics"
		contract.company = "Sarveksha Realty and Inframine LLP"
		contract.start_date = today()
		contract.end_date = add_days(today(), -5) # Invalid: end date is before start date
		contract.contract_value = 10000.00
		contract.status = "Draft"
		
		self.assertRaises(frappe.ValidationError, contract.insert)

	def test_api_make_payment_entry(self):
		pr = frappe.new_doc("Vendor Payment Request")
		pr.vendor = "Apex Logistics"
		pr.company = "Sarveksha Realty and Inframine LLP"
		pr.requested_amount = 5000.00
		pr.request_date = today()
		pr.status = "Approved"
		pr.insert(ignore_permissions=True)
		pr.submit()
		
		pe = make_payment_entry(pr.name)
		self.assertEqual(pe.party, "Apex Logistics")
		self.assertEqual(pe.paid_amount, 5000.00)
		self.assertEqual(pe.company, "Sarveksha Realty and Inframine LLP")
