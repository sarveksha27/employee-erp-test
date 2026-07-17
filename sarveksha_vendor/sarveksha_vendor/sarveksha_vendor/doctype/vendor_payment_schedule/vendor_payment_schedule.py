import frappe
from frappe.model.document import Document

class VendorPaymentSchedule(Document):
	def validate(self):
		if self.paid_amount is None:
			self.paid_amount = 0
		
		# Compute outstanding amount
		self.outstanding_amount = self.amount - self.paid_amount
		
		# Auto-update status
		if self.outstanding_amount <= 0:
			self.status = "Paid"
		elif self.paid_amount > 0:
			self.status = "Partially Paid"
		else:
			self.status = "Unpaid"
