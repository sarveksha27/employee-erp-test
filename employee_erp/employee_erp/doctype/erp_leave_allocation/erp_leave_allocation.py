# Copyright (c) 2026, Your Team Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ERPLeaveAllocation(Document):
	def validate(self):
		self.validate_allocation_limit()
		self.validate_duplicate()
		self.update_balance()

	def validate_allocation_limit(self):
		max_allowed = frappe.db.get_value(
			"ERP Leave Type", self.leave_type, "max_leaves_allowed"
		)
		if max_allowed and self.total_leaves_allocated > max_allowed:
			frappe.throw(
				_("Total allocated leaves ({0}) cannot exceed the maximum allowed ({1}) for {2}.").format(
					self.total_leaves_allocated, max_allowed, self.leave_type
				)
			)

	def validate_duplicate(self):
		existing = frappe.db.exists(
			"ERP Leave Allocation",
			{
				"employee": self.employee,
				"leave_type": self.leave_type,
				"fiscal_year": self.fiscal_year,
				"name": ["!=", self.name],
			},
		)
		if existing:
			frappe.throw(
				_("Leave allocation for {0} - {1} in {2} already exists: {3}").format(
					self.employee, self.leave_type, self.fiscal_year, existing
				)
			)

	def update_balance(self):
		self.balance_leaves = self.total_leaves_allocated - (self.leaves_taken or 0)
