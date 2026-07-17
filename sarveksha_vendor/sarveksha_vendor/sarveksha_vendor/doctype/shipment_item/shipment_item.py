import frappe
from frappe.model.document import Document

class ShipmentItem(Document):
	def validate(self):
		if self.quantity and self.unit_value:
			self.total_value = self.quantity * self.unit_value
		else:
			self.total_value = 0
