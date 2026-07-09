# Copyright (c) 2026, Your Team Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, today


class ERPEmployee(Document):
	def autoname(self):
		from frappe.model.naming import set_name_by_naming_series

		set_name_by_naming_series(self)

	def validate(self):
		self.set_employee_name()
		self.validate_date_of_birth()
		self.validate_date_of_joining()
		self.validate_email()
		self.validate_reports_to()
		self.validate_status_change()

	def set_employee_name(self):
		self.employee_name = " ".join(
			filter(lambda x: x, [self.first_name, self.middle_name, self.last_name])
		)

	def validate_date_of_birth(self):
		if self.date_of_birth:
			age = date_diff(today(), self.date_of_birth) / 365
			if age < 18:
				frappe.throw(
					_("Employee must be at least 18 years old. Current age: {0} years.").format(
						int(age)
					)
				)

	def validate_date_of_joining(self):
		if self.date_of_birth and self.date_of_joining:
			if getdate(self.date_of_joining) < getdate(self.date_of_birth):
				frappe.throw(_("Date of Joining cannot be before Date of Birth."))

		if self.relieving_date and self.date_of_joining:
			if getdate(self.relieving_date) < getdate(self.date_of_joining):
				frappe.throw(_("Relieving Date cannot be before Date of Joining."))

	def validate_email(self):
		if self.company_email:
			frappe.utils.validate_email_address(self.company_email, throw=True)
		if self.personal_email:
			frappe.utils.validate_email_address(self.personal_email, throw=True)

	def validate_reports_to(self):
		if self.reports_to and self.reports_to == self.name:
			frappe.throw(_("Employee cannot report to themselves."))

	def validate_status_change(self):
		if self.status == "Left" and not self.relieving_date:
			frappe.msgprint(
				_("Please set the Relieving Date for employees with status 'Left'."),
				alert=True,
				indicator="orange",
			)
