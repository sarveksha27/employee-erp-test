import frappe
from frappe.model.document import Document

class PaymentApproval(Document):
	def on_update(self):
		if self.payment_request:
			try:
				req = frappe.get_doc("Vendor Payment Request", self.payment_request)
				if self.approval_status == "Approved":
					req.status = "Approved"
				elif self.approval_status == "Rejected":
					req.status = "Rejected"
				req.save(ignore_permissions=True)
			except Exception:
				pass
