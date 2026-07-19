# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class SarvekshaPIContainer(Document):
	def validate(self):
		self.validate_dates()

	def validate_dates(self):
		if self.etd and self.eta:
			if getdate(self.eta) < getdate(self.etd):
				frappe.throw(_("ETA (Estimated Arrival) cannot be before ETD (Estimated Departure)."))
