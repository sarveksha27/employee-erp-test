# Copyright (c) 2026, Your Team Name and contributors
# For license information, please see license.txt

import math

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class ERPSalarySlip(Document):
	def validate(self):
		self.validate_dates()
		self.calculate_totals()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if getdate(self.end_date) < getdate(self.start_date):
				frappe.throw(_("Payroll End Date cannot be before Payroll Start Date."))

	def calculate_totals(self):
		self.gross_pay = sum(row.amount for row in (self.earnings or []))
		self.total_deduction = sum(row.amount for row in (self.deductions or []))
		self.net_pay = self.gross_pay - self.total_deduction
		self.rounded_total = math.ceil(self.net_pay)

	@frappe.whitelist()
	def pull_salary_components(self):
		"""Pull components from the linked salary structure into earnings and deductions."""
		if not self.salary_structure:
			frappe.throw(_("Please select a Salary Structure first."))

		structure = frappe.get_doc("ERP Salary Structure", self.salary_structure)

		self.earnings = []
		self.deductions = []

		for detail in structure.salary_details:
			component_type = frappe.db.get_value(
				"ERP Salary Component", detail.salary_component, "component_type"
			)

			row = {
				"salary_component": detail.salary_component,
				"amount": detail.amount,
				"component_type": component_type,
			}

			if component_type == "Earning":
				self.append("earnings", row)
			else:
				self.append("deductions", row)

		self.calculate_totals()
