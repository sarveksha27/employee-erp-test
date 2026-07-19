# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today

class SarvekshaDocument(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		if not self.naming_series:
			self.naming_series = "DOC-.YYYY.-.####"
		self.name = make_autoname(self.naming_series)
		self.document_number = self.name

	def validate(self):
		if not self.upload_date:
			self.upload_date = today()
		if not self.uploaded_by:
			self.uploaded_by = frappe.session.user
