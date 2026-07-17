# Copyright (c) 2026, Your Team Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours


class ERPAttendance(Document):
	def validate(self):
		self.validate_duplicate()
		self.calculate_working_hours()

	def validate_duplicate(self):
		existing = frappe.db.exists(
			"ERP Attendance",
			{
				"employee": self.employee,
				"attendance_date": self.attendance_date,
				"name": ["!=", self.name],
				"docstatus": ["<", 2],
			},
		)
		if existing:
			frappe.throw(
				_("Attendance for employee {0} on {1} already exists: {2}").format(
					self.employee, self.attendance_date, existing
				),
				frappe.DuplicateEntryError,
			)

	def calculate_working_hours(self):
		if self.check_in_time and self.check_out_time:
			hours = time_diff_in_hours(self.check_out_time, self.check_in_time)
			self.working_hours = round(max(hours, 0), 1)
		else:
			self.working_hours = 0
