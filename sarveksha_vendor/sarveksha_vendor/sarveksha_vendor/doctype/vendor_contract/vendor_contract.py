import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime

class VendorContract(Document):
	def autoname(self):
		from frappe.model.naming import set_name_by_naming_series
		set_name_by_naming_series(self)

	def validate(self):
		if self.start_date and self.end_date:
			if getdate(self.end_date) < getdate(self.start_date):
				frappe.throw("End Date cannot be before Start Date.")

def log_contract_change(doc, method):
	# Log contract change to Audit Log
	try:
		log = frappe.get_doc({
			"doctype": "Audit Log",
			"reference_doctype": doc.doctype,
			"reference_name": doc.name,
			"user": frappe.session.user,
			"action": "Update",
			"timestamp": now_datetime(),
			"changes": f"Status updated to: {doc.status}, Amount: {doc.contract_amount}"
		})
		log.insert(ignore_permissions=True)
	except Exception:
		pass  # Avoid blocking contract save if Audit Log fails
