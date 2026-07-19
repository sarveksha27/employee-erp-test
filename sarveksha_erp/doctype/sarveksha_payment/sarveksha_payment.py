# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SarvekshaPayment(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		if not self.naming_series:
			self.naming_series = "PAY-.company.-.YYYY.-.####"
		
		series = self.naming_series
		if ".company." in series:
			comp_code = self.company or "GEN"
			series = series.replace(".company.", comp_code)
			
		self.name = make_autoname(series)
		self.payment_number = self.name

	def validate(self):
		self.validate_amount()

	def validate_amount(self):
		if self.amount and self.amount <= 0:
			frappe.throw(_("Payment Amount must be greater than zero."))
