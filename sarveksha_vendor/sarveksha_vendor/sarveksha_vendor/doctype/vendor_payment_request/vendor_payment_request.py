import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class VendorPaymentRequest(Document):
	def autoname(self):
		from frappe.model.naming import set_name_by_naming_series
		set_name_by_naming_series(self)

	def validate(self):
		if self.amount <= 0:
			frappe.throw("Payment Request amount must be greater than zero.")
		
		# Set default bank details if not already set
		if not self.vendor_bank and self.vendor and self.company:
			default_bank = frappe.db.get_value(
				"Vendor Bank",
				{"vendor": self.vendor, "company": self.company, "is_default": 1},
				"name"
			)
			if default_bank:
				self.vendor_bank = default_bank


def validate_payment_request(doc, method):
	# Check for contract amount validation
	if doc.vendor and doc.company:
		active_contract = frappe.db.get_value(
			"Vendor Contract",
			{"vendor": doc.vendor, "company": doc.company, "status": "Active"},
			["name", "contract_amount"],
			as_dict=1
		)
		if active_contract and doc.amount > active_contract.contract_amount:
			frappe.msgprint(
				f"Warning: Payment request amount ({doc.amount}) exceeds active contract amount ({active_contract.contract_amount}) under Contract {active_contract.name}.",
				indicator="orange"
			)


def log_payment_request(doc, method):
	try:
		# Log payment request status changes
		log = frappe.get_doc({
			"doctype": "Audit Log",
			"reference_doctype": doc.doctype,
			"reference_name": doc.name,
			"user": frappe.session.user,
			"action": "Update",
			"timestamp": now_datetime(),
			"changes": f"Vendor: {doc.vendor}, Status: {doc.status}, Amount: {doc.amount}"
		})
		log.insert(ignore_permissions=True)
	except Exception:
		pass
