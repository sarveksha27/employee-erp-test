# Copyright (c) 2026, Umesh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Equipment(Document):
	def autoname(self):
		if not self.equipment_code:
			self.equipment_code = frappe.model.naming.make_autoname("EQ-.#####")
		self.name = self.equipment_code
