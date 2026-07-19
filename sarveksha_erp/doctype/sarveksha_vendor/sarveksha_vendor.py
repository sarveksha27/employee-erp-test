# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SarvekshaVendor(Document):
	def validate(self):
		self.validate_email()
		self.validate_rating()

	def validate_email(self):
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)

	def validate_rating(self):
		if self.vendor_rating:
			if self.vendor_rating < 1.0 or self.vendor_rating > 5.0:
				frappe.throw(_("Vendor Rating must be between 1.0 and 5.0."))
