# Copyright (c) 2026, Sarveksha Group and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestSarvekshaPurchaseOrder(FrappeTestCase):
	def test_purchase_order_calculation(self):
		doc = frappe.new_doc("Sarveksha Purchase Order")
		doc.company = "SRI"
		doc.vendor = "VND-RIGAKU"
		doc.equipment = "90221900"
		doc.quantity = 2.0
		doc.rate = 10000.0
		doc.discount = 1000.0
		doc.tax = 1800.0
		doc.freight = 500.0
		doc.packing = 200.0
		doc.insurance = 300.0
		doc.other_charges = 100.0
		
		# Execute validation to calculate totals
		doc.validate()
		
		# Expected grand_total = (2 * 10000) - 1000 + 1800 + 500 + 200 + 300 + 100 = 21900
		self.assertEqual(doc.grand_total, 21900.0)
