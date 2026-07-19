# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SarvekshaTaxConfiguration(Document):
	def validate(self):
		self.validate_percentages()

	def validate_percentages(self):
		for field in ["gst_percentage", "tds_percentage", "vat_percentage", "withholding_tax"]:
			val = getattr(self, field, 0.0)
			if val and (val < 0.0 or val > 100.0):
				frappe.throw(_("{0} must be between 0% and 100%.").format(self.meta.get_label(field)))
