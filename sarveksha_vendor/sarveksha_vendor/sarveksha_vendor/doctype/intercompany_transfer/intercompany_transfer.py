import frappe
from frappe.model.document import Document

class IntercompanyTransfer(Document):
	def validate(self):
		if self.source_company == self.destination_company:
			frappe.throw("Source Company and Destination Company cannot be the same.")
		if self.amount <= 0:
			frappe.throw("Transfer amount must be greater than zero.")
