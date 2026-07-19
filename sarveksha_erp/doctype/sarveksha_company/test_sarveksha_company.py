# Copyright (c) 2026, Sarveksha Group and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestSarvekshaCompany(FrappeTestCase):
	def test_fiscal_year_validation(self):
		# Test that fiscal_year_end cannot be before fiscal_year_start
		doc = frappe.new_doc("Sarveksha Company")
		doc.company_code = "TEST"
		doc.company_name = "Test Company"
		doc.country = "India"
		doc.currency = "INR"
		doc.fiscal_year_start = "2026-04-01"
		doc.fiscal_year_end = "2025-03-31" # Invalid
		
		self.assertRaises(frappe.ValidationError, doc.insert)
