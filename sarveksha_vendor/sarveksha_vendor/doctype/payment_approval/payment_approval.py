import frappe
from frappe.model.document import Document

class PaymentApproval(Document):
	def after_insert(self):
		req = frappe.get_doc("Vendor Payment Request", self.payment_request)
		if self.status == "Approved":
			req.status = "Approved"
		else:
			req.status = "Rejected"
		req.save(ignore_permissions=True)
		
		# Log to Audit Log
		try:
			audit = frappe.new_doc("Audit Log")
			audit.document_type = "Vendor Payment Request"
			audit.document_name = self.payment_request
			audit.action = "Approved" if self.status == "Approved" else "Rejected"
			audit.user = self.approved_by
			audit.timestamp = frappe.utils.now_datetime()
			audit.details = f"Approval document {self.name} created. Comments: {self.comments or ''}"
			audit.insert(ignore_permissions=True)
		except Exception:
			pass
