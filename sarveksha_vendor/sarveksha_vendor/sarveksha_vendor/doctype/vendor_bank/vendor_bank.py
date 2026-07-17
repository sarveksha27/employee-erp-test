import frappe
from frappe.model.document import Document

class VendorBank(Document):
	def validate(self):
		if self.is_default:
			# Unset default bank account for this vendor in this company
			frappe.db.sql("""
				update `tabVendor Bank`
				set is_default = 0
				where vendor = %s and company = %s and name != %s
			""", (self.vendor, self.company, self.name or ""))
