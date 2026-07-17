import frappe
from frappe.model.document import Document

class Equipment(Document):
	def autoname(self):
		from frappe.model.naming import set_name_by_naming_series
		set_name_by_naming_series(self)
