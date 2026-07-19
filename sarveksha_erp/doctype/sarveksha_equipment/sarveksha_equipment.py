# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SarvekshaEquipment(Document):
	def validate(self):
		self.validate_costs()

	def validate_costs(self):
		if self.approximate_cost and self.approximate_cost < 0:
			frappe.throw(_("Approximate Cost cannot be negative."))
		if self.latest_purchase_cost and self.latest_purchase_cost < 0:
			frappe.throw(_("Latest Purchase Cost cannot be negative."))
