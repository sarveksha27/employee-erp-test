import frappe
from frappe.model.document import Document

class VendorPaymentRequest(Document):
	def validate(self):
		if not self.payment_schedule and self.purchase_invoice:
			self.create_default_schedule()
		
		if self.payment_schedule:
			total_schedule_amount = sum([d.amount for d in self.payment_schedule])
			if total_schedule_amount > self.requested_amount:
				frappe.msgprint("Warning: The sum of Payment Schedule amounts exceeds the Requested Amount.")

	def create_default_schedule(self):
		invoice = frappe.get_doc("Purchase Invoice", self.purchase_invoice)
		if getattr(invoice, "payment_schedule", None):
			for term in invoice.payment_schedule:
				self.append("payment_schedule", {
					"payment_term": term.payment_term,
					"invoice_portion": term.invoice_portion,
					"due_date": term.due_date,
					"amount": term.payment_amount,
					"paid": 0
				})
