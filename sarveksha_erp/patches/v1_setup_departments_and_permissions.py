"""Provision Procurement and Accounts departments and enforce finance confidentiality."""

import frappe
from frappe import _


PRIMARY_COMPANY = "Sarveksha Realty and Inframine LLP"
PROCUREMENT_ROLE = "PO Approver"
ACCOUNTS_ROLE = "Accounts Manager"
BANKING_SUPPLIER_FIELDS = (
	"custom_bank_name",
	"custom_bank_branch",
	"custom_bank_currency",
	"custom_account_number",
	"custom_ifsc",
	"custom_swift_code",
	"custom_iban",
)
PROCUREMENT_ROLES = ("PO Generator", "PO Verifier", "PO Approver")
SENSITIVE_FIELDS = {
	"Supplier": BANKING_SUPPLIER_FIELDS,
	"Bank Account": ("bank_account_no", "iban"),
	"Vendor Purchase Order": (
		"vendor_bank_name",
		"vendor_account_number",
		"vendor_ifsc",
		"company_bank",
	),
}


def _ensure_role(role_name):
	if frappe.db.exists("Role", role_name):
		return

	role = frappe.new_doc("Role")
	role.role_name = role_name
	role.desk_access = 1
	role.flags.ignore_permissions = True
	role.insert()


def _ensure_department_fields():
	custom_fields = (
		{
			"fieldname": "custom_default_cost_center",
			"fieldtype": "Link",
			"label": "Default Cost Center",
			"options": "Cost Center",
			"insert_after": "parent_department",
		},
		{
			"fieldname": "custom_default_approval_role",
			"fieldtype": "Link",
			"label": "Default Approval Role",
			"options": "Role",
			"insert_after": "custom_default_cost_center",
		},
	)

	for field in custom_fields:
		name = f"Department-{field['fieldname']}"
		if frappe.db.exists("Custom Field", name):
			custom_field = frappe.get_doc("Custom Field", name)
			custom_field.update(field)
			custom_field.save(ignore_permissions=True)
			continue

		custom_field = frappe.new_doc("Custom Field")
		custom_field.dt = "Department"
		custom_field.module = "Vendor Management"
		custom_field.update(field)
		custom_field.flags.ignore_permissions = True
		custom_field.insert()

	frappe.clear_cache(doctype="Department")


def _ensure_cost_center(name, parent):
	cost_center_name = f"{name} - SRIL"
	if frappe.db.exists("Cost Center", cost_center_name):
		return cost_center_name

	cost_center = frappe.new_doc("Cost Center")
	cost_center.cost_center_name = name
	cost_center.company = PRIMARY_COMPANY
	cost_center.parent_cost_center = parent
	cost_center.is_group = 0
	cost_center.flags.ignore_permissions = True
	cost_center.insert()
	return cost_center.name


def _ensure_department(name, cost_center, approval_role):
	department_name = f"{name} - SRIL"
	if frappe.db.exists("Department", department_name):
		department = frappe.get_doc("Department", department_name)
	else:
		department = frappe.new_doc("Department")
		department.department_name = name
		department.company = PRIMARY_COMPANY
		department.parent_department = "All Departments"
		department.is_group = 0
		department.flags.ignore_permissions = True
		department.insert()

	department.custom_default_cost_center = cost_center
	department.custom_default_approval_role = approval_role
	department.flags.ignore_permissions = True
	department.save()
	return department.name


def _set_field_permission_level(doctype, fieldname, permlevel=1):
	if doctype == "Supplier":
		custom_field_name = f"{doctype}-{fieldname}"
		if frappe.db.exists("Custom Field", custom_field_name):
			custom_field = frappe.get_doc("Custom Field", custom_field_name)
			if custom_field.permlevel != permlevel:
				custom_field.permlevel = permlevel
				custom_field.save(ignore_permissions=True)
			return

	if not frappe.get_meta(doctype).has_field(fieldname):
		return

	filters = {
		"doctype_or_field": "DocField",
		"doc_type": doctype,
		"field_name": fieldname,
		"property": "permlevel",
	}
	setter_name = frappe.db.get_value("Property Setter", filters, "name")
	if setter_name:
		setter = frappe.get_doc("Property Setter", setter_name)
		if str(setter.value) != str(permlevel):
			setter.value = str(permlevel)
			setter.property_type = "Int"
			setter.flags.ignore_permissions = True
			setter.save()
		return

	frappe.make_property_setter(
		{
			"doctype_or_field": "DocField",
			"doctype": doctype,
			"fieldname": fieldname,
			"property": "permlevel",
			"value": permlevel,
			"property_type": "Int",
		},
		validate_fields_for_doctype=False,
		module="Vendor Management",
	)


def _setup_permission_rows():
	from sarveksha_erp.install import setup_custom_docperm

	no_access = {
		"read": 0,
		"write": 0,
		"create": 0,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"amend": 0,
		"print": 0,
		"email": 0,
		"report": 0,
		"export": 0,
		"share": 0,
	}
	for role in PROCUREMENT_ROLES:
		for doctype in ("Payment Entry", "Journal Entry"):
			if frappe.db.exists("DocType", doctype):
				setup_custom_docperm(doctype, role, no_access)

	finance_permlevel = {"read": 1, "write": 1}
	finance_doctype_permissions = {"read": 1, "write": 1}
	for doctype in ("Supplier", "Bank Account"):
		if frappe.db.exists("DocType", doctype):
			setup_custom_docperm(doctype, "Accounts Manager", finance_doctype_permissions)

	for doctype in ("Supplier", "Bank Account", "Vendor Purchase Order"):
		if not frappe.db.exists("DocType", doctype):
			continue
		for role in ("Accounts Manager", "System Manager"):
			setup_custom_docperm(doctype, role, finance_permlevel, permlevel=1)

	clerk_permissions = {
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"print": 1,
		"email": 1,
	}
	manager_permissions = {
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 1,
		"submit": 1,
		"cancel": 1,
		"amend": 1,
		"print": 1,
		"email": 1,
		"report": 1,
		"export": 1,
	}
	for doctype in ("Payment Entry", "Purchase Invoice", "Journal Entry"):
		if not frappe.db.exists("DocType", doctype):
			continue
		setup_custom_docperm(doctype, "Accounts Clerk", clerk_permissions)
		setup_custom_docperm(doctype, "Accounts Manager", manager_permissions)

	for doctype, fields in SENSITIVE_FIELDS.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for fieldname in fields:
			_set_field_permission_level(doctype, fieldname)

	managed_permissions = [
		(doctype, role, permlevel)
		for doctype in ("Payment Entry", "Journal Entry")
		for role in PROCUREMENT_ROLES
		for permlevel in (0,)
	]
	managed_permissions.extend(
		(doctype, role, 0)
		for doctype in ("Supplier", "Bank Account")
		for role in ("Accounts Manager", "System Manager")
	)
	managed_permissions.extend(
		(doctype, role, 1)
		for doctype in ("Supplier", "Bank Account", "Vendor Purchase Order")
		for role in ("Accounts Manager", "System Manager")
	)
	managed_permissions.extend(
		(doctype, role, 0)
		for doctype in ("Payment Entry", "Purchase Invoice", "Journal Entry")
		for role in ("Accounts Clerk", "Accounts Manager")
	)
	for doctype, role, permlevel in managed_permissions:
		rows = frappe.get_all(
			"Custom DocPerm",
			filters={"parent": doctype, "role": role, "permlevel": permlevel},
			fields=["name"],
			order_by="creation asc",
		)
		for duplicate in rows[1:]:
			frappe.delete_doc("Custom DocPerm", duplicate.name, ignore_permissions=True, force=True)

	for doctype in SENSITIVE_FIELDS:
		if frappe.db.exists("DocType", doctype):
			frappe.clear_cache(doctype=doctype)


def execute():
	"""Idempotently set up department defaults and security permissions."""
	if frappe.db.exists("Property Setter", "Bank Account-main-permlevel"):
		frappe.db.delete("Property Setter", {"name": "Bank Account-main-permlevel"})
		frappe.clear_cache(doctype="Bank Account")

	if not frappe.db.exists("Company", PRIMARY_COMPANY):
		frappe.log_error(
			message=_("Cannot provision procurement departments: company {0} is missing.").format(
				PRIMARY_COMPANY
			),
			title="Department Security Patch Skipped",
		)
		return

	for role in (*PROCUREMENT_ROLES, "Accounts Clerk", "Accounts Manager"):
		_ensure_role(role)

	_ensure_department_fields()
	company_abbr = frappe.db.get_value("Company", PRIMARY_COMPANY, "abbr")
	root_cost_center = f"{PRIMARY_COMPANY} - {company_abbr}"
	if not frappe.db.exists("Cost Center", root_cost_center):
		root_cost_center = frappe.db.get_value(
			"Cost Center",
			{"company": PRIMARY_COMPANY, "is_group": 1, "parent_cost_center": ["is", "not set"]},
			"name",
		)
	if not root_cost_center:
		frappe.throw(
			_("Cannot provision department cost centers: root cost center for {0} is missing.").format(
				PRIMARY_COMPANY
			)
		)

	procurement_cost_center = _ensure_cost_center("Procurement", root_cost_center)
	accounts_cost_center = _ensure_cost_center("Accounts", root_cost_center)
	_ensure_department("Procurement", procurement_cost_center, "PO Approver")
	_ensure_department("Accounts", accounts_cost_center, "Accounts Manager")
	_setup_permission_rows()


@frappe.whitelist()
def get_supplier_payment_details(supplier):
	"""Mask supplier bank details from non-finance roles, including direct RPC calls."""
	from sarveksha_erp.vendor_management.doctype.vendor_purchase_order.vendor_purchase_order import (
		get_supplier_payment_details as get_supplier_details,
	)

	details = get_supplier_details(supplier)
	roles = set(frappe.get_roles(frappe.session.user))
	if frappe.session.user == "Administrator" or roles.intersection(
		{"Accounts Manager", "System Manager"}
	):
		return details

	for fieldname in ("custom_bank_name", "custom_account_number", "custom_ifsc"):
		details[fieldname] = ""
	return details


def payment_entry_has_permission(doc, ptype="read", user=None, **kwargs):
	"""Deny Payment Entry document access to procurement-role users."""
	user = user or frappe.session.user
	if user == "Administrator":
		return True
	roles = set(frappe.get_roles(user))
	if "System Manager" in roles:
		return True
	if roles.intersection(PROCUREMENT_ROLES):
		return False
	return None


def payment_entry_permission_query_conditions(user=None):
	"""Hide every Payment Entry from procurement-only list routes."""
	user = user or frappe.session.user
	if user == "Administrator":
		return ""
	roles = set(frappe.get_roles(user))
	if "System Manager" not in roles and roles.intersection(PROCUREMENT_ROLES):
		frappe.throw(
			_("Procurement roles are not permitted to access Payment Entries."),
			frappe.PermissionError,
		)
	return ""