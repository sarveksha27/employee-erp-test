# Copyright (c) 2026, Your Team Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ERPDepartment(Document):
	def validate(self):
		self.validate_parent_department()

	def validate_parent_department(self):
		if self.parent_department and self.parent_department == self.name:
			frappe.throw(_("Department cannot be its own parent."))

		if self.parent_department:
			parent = self.parent_department
			visited = {self.name}
			while parent:
				if parent in visited:
					frappe.throw(_("Circular reference detected in department hierarchy."))
				visited.add(parent)
				parent = frappe.db.get_value("ERP Department", parent, "parent_department")
