# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class SarvekshaCompany(Document):
	def validate(self):
		self.validate_fiscal_year()
		self.validate_email()

	def validate_fiscal_year(self):
		if self.fiscal_year_start and self.fiscal_year_end:
			if getdate(self.fiscal_year_end) <= getdate(self.fiscal_year_start):
				frappe.throw(_("Fiscal Year End date must be after Fiscal Year Start date."))

	def validate_email(self):
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)
