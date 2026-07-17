import frappe
from frappe.model.document import Document

class PaymentBatch(Document):
	def validate(self):
		total = 0
		for item in self.payments:
			if item.amount:
				total += item.amount
		self.total_amount = total

	def on_update(self):
		if self.status == "Paid":
			for item in self.payments:
				if item.payment_request:
					try:
						# Update status of payment request to Paid
						req = frappe.get_doc("Vendor Payment Request", item.payment_request)
						req.status = "Paid"
						req.save(ignore_permissions=True)
					except Exception:
						pass
