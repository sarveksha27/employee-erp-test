import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def after_install():
	"""Sets up standard companies, banks, payment terms, and roles/users for Sarveksha Vendor."""
	create_roles()
	setup_companies()
	setup_banks()
	setup_taxes()
	setup_payment_terms()
	setup_standard_users()
	setup_workflows()

def create_roles():
	"""Create the standard roles required by the Vendor tracking system."""
	roles = [
		"Organization Admin",
		"Finance Manager",
		"Purchase Manager",
		"Accounts Officer",
		"Employee",
		"Vendor"
	]
	for role_name in roles:
		if not frappe.db.exists("Role", role_name):
			role = frappe.new_doc("Role")
			role.role_name = role_name
			role.insert(ignore_permissions=True)

def setup_companies():
	"""Creates the six independent companies."""
	companies = [
		{"name": "Sarveksha Realty and Inframine LLP", "country": "India", "currency": "INR", "chart": "India - Chart of Accounts"},
		{"name": "Globe Multitrade and Service LLC", "country": "United Arab Emirates", "currency": "AED", "chart": "U.A.E - Chart of Accounts"},
		{"name": "Sarveksha BSTP SAS", "country": "Guinea", "currency": "GNF", "chart": "Standard"},
		{"name": "Sarveksha Mining SARL", "country": "Cameroon", "currency": "XAF", "chart": "Standard"},
		{"name": "Sarveksha Botswana Proprietary Limited", "country": "Botswana", "currency": "BWP", "chart": "Standard"},
		{"name": "Odhav Holdings", "country": "Sierra Leone", "currency": "SLE", "chart": "Standard"}
	]
	
	for c in companies:
		# Create currency SLE if needed
		if c["currency"] == "SLE" and not frappe.db.exists("Currency", "SLE"):
			try:
				curr = frappe.new_doc("Currency")
				curr.currency_name = "SLE"
				curr.symbol = "Le"
				curr.fraction = "Cent"
				curr.fraction_units = 100
				curr.enabled = 1
				curr.insert(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Failed to create currency SLE: {str(e)}", "Sarveksha Setup Error")

		if not frappe.db.exists("Company", c["name"]):
			try:
				company = frappe.new_doc("Company")
				company.company_name = c["name"]
				company.default_currency = c["currency"]
				company.country = c["country"]
				company.chart_of_accounts = c["chart"]
				company.insert(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Failed to create company {c['name']}: {str(e)}", "Sarveksha Setup Error")

def setup_banks():
	"""Creates standard banks and bank accounts for the companies."""
	# Define Banks first
	banks = [
		"HDFC Bank", "ICICI Bank", "Emirates NBD", "Mashreq Bank",
		"Ecobank Guinea", "Afriland First Bank", "First National Bank Botswana", "Rokel Commercial Bank"
	]
	for bank in banks:
		if not frappe.db.exists("Bank", bank):
			try:
				b = frappe.new_doc("Bank")
				b.bank_name = bank
				b.insert(ignore_permissions=True)
			except Exception:
				pass

	# Define Bank Accounts
	bank_accounts = [
		{"account_name": "Sarveksha Realty HDFC Current", "bank": "HDFC Bank", "company": "Sarveksha Realty and Inframine LLP", "currency": "INR", "number": "1234567890"},
		{"account_name": "Sarveksha Realty ICICI Current", "bank": "ICICI Bank", "company": "Sarveksha Realty and Inframine LLP", "currency": "INR", "number": "0987654321"},
		{"account_name": "Globe Multitrade Emirates NBD Current", "bank": "Emirates NBD", "company": "Globe Multitrade and Service LLC", "currency": "AED", "number": "2345678901"},
		{"account_name": "Globe Multitrade Mashreq Current", "bank": "Mashreq Bank", "company": "Globe Multitrade and Service LLC", "currency": "AED", "number": "8765432109"},
		{"account_name": "Sarveksha BSTP Ecobank Current", "bank": "Ecobank Guinea", "company": "Sarveksha BSTP SAS", "currency": "GNF", "number": "3456789012"},
		{"account_name": "Sarveksha Mining Afriland Current", "bank": "Afriland First Bank", "company": "Sarveksha Mining SARL", "currency": "XAF", "number": "4567890123"},
		{"account_name": "Botswana FNB Current", "bank": "First National Bank Botswana", "company": "Sarveksha Botswana Proprietary Limited", "currency": "BWP", "number": "5678901234"},
		{"account_name": "Odhav Holdings Rokel Current", "bank": "Rokel Commercial Bank", "company": "Odhav Holdings", "currency": "SLE", "number": "6789012345"}
	]
	
	for ba in bank_accounts:
		if not frappe.db.exists("Bank Account", ba["account_name"]):
			# Only check if company exists
			if frappe.db.exists("Company", ba["company"]):
				try:
					account = frappe.new_doc("Bank Account")
					account.bank_account_name = ba["account_name"]
					account.bank = ba["bank"]
					account.company = ba["company"]
					account.account_type = "Current"
					account.bank_account_no = ba["number"]
					account.is_default = 1
					account.insert(ignore_permissions=True)
				except Exception:
					pass

def setup_taxes():
	"""Creates standard Purchase Taxes and Charges templates for each company."""
	tax_configs = [
		{"company": "Sarveksha Realty and Inframine LLP", "title": "GST 18%", "rate": 18.0},
		{"company": "Globe Multitrade and Service LLC", "title": "VAT 5%", "rate": 5.0},
		{"company": "Sarveksha BSTP SAS", "title": "VAT 18%", "rate": 18.0},
		{"company": "Sarveksha Mining SARL", "title": "VAT 19.25%", "rate": 19.25},
		{"company": "Sarveksha Botswana Proprietary Limited", "title": "VAT 14%", "rate": 14.0},
		{"company": "Odhav Holdings", "title": "GST 15%", "rate": 15.0}
	]
	
	for tc in tax_configs:
		company = tc["company"]
		if not frappe.db.exists("Company", company):
			continue
		
		template_name = f"{tc['title']} - {company}"
		if frappe.db.exists("Purchase Taxes and Charges Template", template_name):
			continue
			
		# Find a suitable tax account
		tax_account = frappe.db.get_value("Account", {
			"company": company,
			"account_type": ["in", ["Tax", "Chargeable"]],
			"is_group": 0
		}, "name")
		
		if not tax_account:
			tax_account = frappe.db.get_value("Account", {
				"company": company,
				"account_name": ["like", "%Tax%"],
				"is_group": 0
			}, "name")
			
		if not tax_account:
			tax_account = frappe.db.get_value("Account", {
				"company": company,
				"is_group": 0
			}, "name")
			
		if tax_account:
			try:
				tpl = frappe.new_doc("Purchase Taxes and Charges Template")
				tpl.title = template_name
				tpl.company = company
				tpl.is_default = 1
				tpl.append("taxes", {
					"category": "Total",
					"charge_type": "On Net Total",
					"account_head": tax_account,
					"description": tc["title"],
					"rate": tc["rate"]
				})
				tpl.insert(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Failed to create tax template {template_name}: {str(e)}", "Sarveksha Tax Setup Error")

def setup_payment_terms():
	"""Creates standard payment terms and payment terms templates."""
	terms = [
		{"name": "Immediate Pay", "credit_days": 0, "portion": 100.0, "description": "Immediate Payment"},
		{"name": "30 Credit Days", "credit_days": 30, "portion": 100.0, "description": "30 Credit Days"},
		{"name": "60 Credit Days", "credit_days": 60, "portion": 100.0, "description": "60 Credit Days"},
		{"name": "25% Advance", "credit_days": 0, "portion": 25.0, "description": "25% Advance Payment"},
		{"name": "75% after Invoice", "credit_days": 30, "portion": 75.0, "description": "75% after Invoice"},
		{"name": "50% Advance", "credit_days": 0, "portion": 50.0, "description": "50% Advance Payment"},
		{"name": "50% Delivery", "credit_days": 15, "portion": 50.0, "description": "50% Delivery Payment"},
		{"name": "Letter of Credit", "credit_days": 90, "portion": 100.0, "description": "Letter of Credit"}
	]
	
	for t in terms:
		if not frappe.db.exists("Payment Term", t["name"]):
			try:
				pt = frappe.new_doc("Payment Term")
				pt.payment_term_name = t["name"]
				pt.credit_days = t["credit_days"]
				pt.invoice_portion = t["portion"]
				pt.description = t["description"]
				pt.insert(ignore_permissions=True)
			except Exception:
				pass

	# Create Templates
	templates = [
		{"name": "Immediate", "terms": [{"term": "Immediate Pay", "portion": 100.0}]},
		{"name": "30 Days", "terms": [{"term": "30 Credit Days", "portion": 100.0}]},
		{"name": "60 Days", "terms": [{"term": "60 Credit Days", "portion": 100.0}]},
		{"name": "Advance 25%", "terms": [{"term": "25% Advance", "portion": 25.0}, {"term": "75% after Invoice", "portion": 75.0}]},
		{"name": "Advance 50%", "terms": [{"term": "50% Advance", "portion": 50.0}, {"term": "50% Delivery", "portion": 50.0}]},
		{"name": "LC Payment", "terms": [{"term": "Letter of Credit", "portion": 100.0}]}
	]
	
	for temp in templates:
		if not frappe.db.exists("Payment Terms Template", temp["name"]):
			try:
				ptt = frappe.new_doc("Payment Terms Template")
				ptt.template_name = temp["name"]
				for term_data in temp["terms"]:
					ptt.append("terms", {
						"payment_term": term_data["term"],
						"invoice_portion": term_data["portion"]
					})
				ptt.insert(ignore_permissions=True)
			except Exception:
				pass

def setup_standard_users():
	"""Creates standard production-ready users for the login roles."""
	standard_users = [
		{"email": "admin.realty@sarveksha.com", "first_name": "Realty Admin", "role": "Organization Admin", "company": "Sarveksha Realty and Inframine LLP"},
		{"email": "finance.mgr@sarveksha.com", "first_name": "Finance Manager", "role": "Finance Manager", "company": "Sarveksha Realty and Inframine LLP"},
		{"email": "purchase.mgr@sarveksha.com", "first_name": "Purchase Manager", "role": "Purchase Manager", "company": "Sarveksha Realty and Inframine LLP"},
		{"email": "accounts.off@sarveksha.com", "first_name": "Accounts Officer", "role": "Accounts Officer", "company": "Sarveksha Realty and Inframine LLP"},
		{"email": "staff.user@sarveksha.com", "first_name": "Employee Staff", "role": "Employee", "company": "Sarveksha Realty and Inframine LLP"},
		{"email": "portal.vendor@sarveksha.com", "first_name": "Portal Supplier", "role": "Vendor", "company": ""}
	]
	
	for du in standard_users:
		if not frappe.db.exists("User", du["email"]):
			try:
				user = frappe.new_doc("User")
				user.email = du["email"]
				user.first_name = du["first_name"]
				user.enabled = 1
				user.send_welcome_email = 0
				user.append("roles", {
					"role": du["role"]
				})
				user.append("roles", {
					"role": "Blogger"
				})
				user.insert(ignore_permissions=True)
				
				# Set default password
				user_auth = frappe.get_doc("User", du["email"])
				user_auth.new_password = "password123"
				user_auth.save(ignore_permissions=True)
				
				# Setup Company User Permission mapping
				if du["company"] and frappe.db.exists("Company", du["company"]):
					create_user_permission(du["email"], "Company", du["company"])
			except Exception:
				pass

def create_user_permission(user, doctype, docname):
	"""Create User Permission to restrict records by Company/Entity."""
	if not frappe.db.exists("User Permission", {"user": user, "allow": doctype, "for_value": docname}):
		try:
			up = frappe.new_doc("User Permission")
			up.user = user
			up.allow = doctype
			up.for_value = docname
			up.is_default = 1
			up.insert(ignore_permissions=True)
		except Exception:
			pass

def setup_workflows():
	"""Creates standard workflow for Vendor Payment Request."""
	workflow_name = "Vendor Payment Request Workflow"
	doctype_name = "Vendor Payment Request"
	
	if not frappe.db.exists("Workflow", workflow_name):
		try:
			wf = frappe.new_doc("Workflow")
			wf.workflow_name = workflow_name
			wf.document_type = doctype_name
			wf.is_active = 1
			wf.workflow_state_field = "status"
			
			# Define States
			states = [
				{"state": "Draft", "doc_status": 0, "allow_edit": "Accounts Officer", "update_field": "status", "update_value": "Draft"},
				{"state": "Pending Finance Review", "doc_status": 0, "allow_edit": "Accounts Officer", "update_field": "status", "update_value": "Pending Finance Review"},
				{"state": "Pending Approval", "doc_status": 0, "allow_edit": "Finance Manager", "update_field": "status", "update_value": "Pending Approval"},
				{"state": "Approved", "doc_status": 1, "allow_edit": "Finance Manager", "update_field": "status", "update_value": "Approved"},
				{"state": "Rejected", "doc_status": 0, "allow_edit": "Finance Manager", "update_field": "status", "update_value": "Rejected"},
				{"state": "Paid", "doc_status": 1, "allow_edit": "Finance Manager", "update_field": "status", "update_value": "Paid"}
			]
			
			for s in states:
				wf.append("states", s)
				
			# Define Transitions
			transitions = [
				{"state": "Draft", "action": "Submit for Review", "next_state": "Pending Finance Review", "allowed": "Accounts Officer"},
				{"state": "Pending Finance Review", "action": "Request Approval", "next_state": "Pending Approval", "allowed": "Accounts Officer"},
				{"state": "Pending Approval", "action": "Approve Payment", "next_state": "Approved", "allowed": "Finance Manager"},
				{"state": "Pending Approval", "action": "Reject Payment", "next_state": "Rejected", "allowed": "Finance Manager"},
				{"state": "Approved", "action": "Pay Request", "next_state": "Paid", "allowed": "Accounts Officer"}
			]
			
			for t in transitions:
				wf.append("transitions", t)
				
			wf.insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Failed to create Workflow: {str(e)}", "Sarveksha Workflow Setup Error")
