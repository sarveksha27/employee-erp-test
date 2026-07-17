import frappe
from frappe.model.document import Document

class PaymentBatchEntry(Document):
	def validate(self):
		if self.payment_request:
			try:
				req = frappe.get_doc("Vendor Payment Request", self.payment_request)
				self.vendor = req.vendor
				self.amount = req.amount
			except Exception:
				pass
