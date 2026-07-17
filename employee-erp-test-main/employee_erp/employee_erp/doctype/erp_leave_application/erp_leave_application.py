# Copyright (c) 2026, Your Team Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, add_days


class ERPLeaveApplication(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_total_leave_days()
		self.validate_leave_balance()

	def on_submit(self):
		if self.status == "Approved":
			self.update_leave_allocation(cancel=False)

	def on_cancel(self):
		if self.status == "Approved":
			self.update_leave_allocation(cancel=True)

	def validate_dates(self):
		if self.from_date and self.to_date:
			if getdate(self.to_date) < getdate(self.from_date):
				frappe.throw(_("To Date cannot be before From Date."))

	def calculate_total_leave_days(self):
		if self.from_date and self.to_date:
			total_days = date_diff(self.to_date, self.from_date) + 1

			# Exclude holidays if a holiday list exists
			holidays = self.get_holidays()
			leave_days = total_days - len(holidays)
			self.total_leave_days = max(leave_days, 0)
		else:
			self.total_leave_days = 0

	def get_holidays(self):
		"""Get list of holidays between from_date and to_date."""
		holiday_lists = frappe.get_all(
			"ERP Holiday List",
			pluck="name",
			limit=1,
		)
		if not holiday_lists:
			return []

		holidays = frappe.get_all(
			"ERP Holiday",
			filters={
				"parent": holiday_lists[0],
				"holiday_date": ["between", [self.from_date, self.to_date]],
			},
			pluck="holiday_date",
		)
		return holidays

	def validate_leave_balance(self):
		if self.status != "Approved":
			return

		fiscal_year = str(getdate(self.from_date).year)
		allocation = frappe.db.get_value(
			"ERP Leave Allocation",
			{
				"employee": self.employee,
				"leave_type": self.leave_type,
				"fiscal_year": fiscal_year,
			},
			["total_leaves_allocated", "leaves_taken"],
			as_dict=True,
		)

		if not allocation:
			frappe.throw(
				_("No leave allocation found for {0} - {1} in fiscal year {2}.").format(
					self.employee, self.leave_type, fiscal_year
				)
			)

		available = allocation.total_leaves_allocated - (allocation.leaves_taken or 0)
		if self.total_leave_days > available:
			frappe.throw(
				_("Insufficient leave balance. Available: {0}, Requested: {1}").format(
					available, self.total_leave_days
				)
			)

	def update_leave_allocation(self, cancel=False):
		fiscal_year = str(getdate(self.from_date).year)
		allocation_name = frappe.db.get_value(
			"ERP Leave Allocation",
			{
				"employee": self.employee,
				"leave_type": self.leave_type,
				"fiscal_year": fiscal_year,
			},
		)

		if not allocation_name:
			return

		allocation = frappe.get_doc("ERP Leave Allocation", allocation_name)
		if cancel:
			allocation.leaves_taken = max(
				(allocation.leaves_taken or 0) - self.total_leave_days, 0
			)
		else:
			allocation.leaves_taken = (allocation.leaves_taken or 0) + self.total_leave_days

		allocation.balance_leaves = allocation.total_leaves_allocated - allocation.leaves_taken
		allocation.flags.ignore_validate = True
		allocation.save(ignore_permissions=True)
