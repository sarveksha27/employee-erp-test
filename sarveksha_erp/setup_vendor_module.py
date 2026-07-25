import frappe

def execute():
	frappe.set_user("Administrator")
	print("=" * 60)
	print("PHASE 2: Creating Vendor Management Module & DocType in Sarveksha ERP")
	print("=" * 60)

	# ─── Create Module Def ───
	if not frappe.db.exists("Module Def", "Vendor Management"):
		doc = frappe.new_doc("Module Def")
		doc.module_name = "Vendor Management"
		doc.app_name = "sarveksha_erp"
		doc.insert(ignore_permissions=True)
		print("  ✓ Module Def 'Vendor Management' created.")
	else:
		print("  ✓ Module Def 'Vendor Management' already exists.")

	frappe.db.commit()

	# ─── Create Vendor Payment DocType ───
	if not frappe.db.exists("DocType", "Vendor Payment"):
		doc = frappe.new_doc("DocType")
		doc.name = "Vendor Payment"
		doc.module = "Vendor Management"
		doc.custom = 1
		doc.autoname = "naming_series:"
		doc.naming_rule = "By \"Naming Series\" field"
		
		# Define Fields
		doc.append("fields", {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "VP-.YYYY.-", "reqd": 1, "set_only_once": 1, "hidden": 1, "default": "VP-.YYYY.-"})
		doc.append("fields", {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company", "reqd": 1, "in_list_view": 1})
		doc.append("fields", {"fieldname": "supplier", "fieldtype": "Link", "label": "Supplier", "options": "Supplier", "reqd": 1, "in_list_view": 1})
		doc.append("fields", {"fieldname": "payment_date", "fieldtype": "Date", "label": "Payment Date", "reqd": 1, "default": "Today", "in_list_view": 1})
		doc.append("fields", {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "reqd": 1, "in_list_view": 1, "options": "currency"})
		doc.append("fields", {"fieldname": "currency", "fieldtype": "Link", "label": "Currency", "options": "Currency", "reqd": 1})
		doc.append("fields", {"fieldname": "mode_of_payment", "fieldtype": "Link", "label": "Mode of Payment", "options": "Mode of Payment", "reqd": 1})
		doc.append("fields", {"fieldname": "reference_no", "fieldtype": "Data", "label": "Reference No / UTR"})
		doc.append("fields", {"fieldname": "reference_date", "fieldtype": "Date", "label": "Reference Date"})
		doc.append("fields", {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "\nDraft\nPending Approval\nApproved\nPaid\nCancelled", "default": "Draft", "in_list_view": 1})
		doc.append("fields", {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"})

		# Permissions
		doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1})
		doc.append("permissions", {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1})
		doc.append("permissions", {"role": "Accounts User", "read": 1, "write": 1, "create": 1})

		doc.is_submittable = 1
		doc.insert(ignore_permissions=True)
		print("  ✓ DocType 'Vendor Payment' created.")
	else:
		print("  ✓ DocType 'Vendor Payment' already exists.")

	frappe.db.commit()

	# ─── Create Workspace ───
	if not frappe.db.exists("Workspace", "Vendor Management"):
		doc = frappe.new_doc("Workspace")
		doc.label = "Vendor Management"
		doc.title = "Vendor Management"
		doc.module = "Vendor Management"
		doc.icon = "payment"
		doc.type = "Workspace"
		doc.public = 1
		doc.append("roles", {"role": "System Manager"})
		doc.append("roles", {"role": "Accounts Manager"})
		doc.append("roles", {"role": "Accounts User"})
		doc.content = '[{"id":"h1_shortcuts","type":"header","data":{"text":"<span class=\\"h4\\"><b>Quick Access</b></span>","col":12}},{"id":"sc_vendor_payment","type":"shortcut","data":{"shortcut_name":"Vendor Payment","col":4}},{"id":"sc_supplier","type":"shortcut","data":{"shortcut_name":"Supplier","col":4}},{"id":"sc_company","type":"shortcut","data":{"shortcut_name":"Company","col":4}}]'
		doc.insert(ignore_permissions=True)
		print("  ✓ Workspace 'Vendor Management' created.")
	else:
		print("  ✓ Workspace 'Vendor Management' already exists.")
	
	frappe.db.commit()
	
	# ─── Create Workspace Sidebar ───
	if not frappe.db.exists("Workspace Sidebar", "Vendor Management"):
		doc = frappe.new_doc("Workspace Sidebar")
		doc.name = "Vendor Management"
		doc.title = "Vendor Management"
		doc.module = "Vendor Management"
		doc.icon = "payment"
		doc.header_icon = "payment"
		doc.insert(ignore_permissions=True)
		print("  ✓ Workspace Sidebar 'Vendor Management' created.")
	else:
		print("  ✓ Workspace Sidebar 'Vendor Management' already exists.")
	
	frappe.db.commit()

	# ─── Create Desktop Icon ───
	if not frappe.db.exists("Desktop Icon", "Vendor Management"):
		doc = frappe.new_doc("Desktop Icon")
		doc.name = "Vendor Management"
		doc.label = "Vendor Management"
		doc.icon_type = "Link"
		doc.link_type = "Workspace Sidebar"
		doc.link_to = "Vendor Management"
		doc.parent_icon = "ERPNext"
		doc.standard = 1
		doc.app = "sarveksha_erp"
		doc.icon = "payment"
		doc.hidden = 0
		doc.insert(ignore_permissions=True)
		print("  ✓ Desktop Icon 'Vendor Management' created.")
	else:
		print("  ✓ Desktop Icon 'Vendor Management' already exists.")

	frappe.db.commit()
	print("\n✅ Phase 2 Complete: Vendor Management Module & DocType created in Sarveksha ERP.")
