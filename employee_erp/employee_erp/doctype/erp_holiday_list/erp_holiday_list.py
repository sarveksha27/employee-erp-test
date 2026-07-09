# Copyright (c) 2026, Your Team Name and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class ERPHolidayList(Document):
	def validate(self):
		self.total_holidays = len(self.holidays) if self.holidays else 0
