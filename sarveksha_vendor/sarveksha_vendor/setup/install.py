import frappe
from frappe.utils import today, add_days, now_datetime

def after_install():
	print("Initializing Sarveksha Vendor Tracking Custom App...")
	create_roles()
	create_companies_and_banks()
	create_payment_terms()
	create_taxes()
	create_dummy_data()
	create_dashboard_and_cards()
	print("Sarveksha Vendor Tracking installation and setup completed successfully.")


def safe_insert(doctype, doc_dict, name_field="name"):
	if frappe.db.table_exists(f"tab{doctype}"):
		val = doc_dict.get(name_field)
		if val and not frappe.db.exists(doctype, {name_field: val}):
			doc = frappe.get_doc({"doctype": doctype, **doc_dict})
			doc.insert(ignore_permissions=True)
			return doc
		elif val:
			try:
				return frappe.get_doc(doctype, val)
			except Exception:
				pass
	return None


def create_roles():
	roles = ["Organization Admin", "Finance Manager", "Purchase Manager", "Accounts Officer", "Vendor Portal User"]
	for role in roles:
		if not frappe.db.exists("Role", role):
			doc = frappe.get_doc({
				"doctype": "Role",
				"role_name": role
			})
			doc.insert(ignore_permissions=True)


def create_companies_and_banks():
	# Define companies to create
	companies = [
		{"name": "Sarveksha Realty and Inframine LLP", "abbr": "SRIL", "default_currency": "INR"},
		{"name": "Globe Multitrade and Service LLC", "abbr": "GMSL", "default_currency": "AED"},
		{"name": "Sarveksha BSTP SAS", "abbr": "SBSTP", "default_currency": "GNF"},
		{"name": "Sarveksha Mining SARL", "abbr": "SMS", "default_currency": "XAF"},
		{"name": "Sarveksha Botswana Proprietary Limited", "abbr": "SBPL", "default_currency": "BWP"},
		{"name": "Odhav Holdings", "abbr": "OH", "default_currency": "SLE"},
		{"name": "Sarveksha SL Limited", "abbr": "SSLL", "default_currency": "SLE"},
		{"name": "Baani Minerals", "abbr": "BM", "default_currency": "SLE"}
	]

	for c in companies:
		# Create Currency if not exists (SLE is new Sierra Leone currency code)
		if c["default_currency"] == "SLE" and not frappe.db.exists("Currency", "SLE"):
			safe_insert("Currency", {
				"currency_name": "New Leone",
				"name": "SLE",
				"fraction": "Cents",
				"symbol": "Le",
				"fraction_units": 100
			})

		comp_doc = safe_insert("Company", {
			"company_name": c["name"],
			"name": c["name"],
			"abbr": c["abbr"],
			"default_currency": c["default_currency"],
			"country": "India" if c["default_currency"] == "INR" else "Sierra Leone" if c["default_currency"] == "SLE" else "Botswana" if c["default_currency"] == "BWP" else "United Arab Emirates" if c["default_currency"] == "AED" else "Cameroon" if c["default_currency"] == "XAF" else "Guinea"
		}, name_field="company_name")

		# Create Default Bank Account for the Company
		bank_name = f"Default Bank - {c['abbr']}"
		safe_insert("Bank Account", {
			"bank_account_name": bank_name,
			"name": bank_name,
			"company": c["name"],
			"account_type": "Saving" if c["default_currency"] == "INR" else "Current",
			"currency": c["default_currency"]
		}, name_field="bank_account_name")


def create_payment_terms():
	terms = [
		{"template_name": "Immediate Payment", "name": "Immediate Payment"},
		{"template_name": "30 Days Credit", "name": "30 Days Credit"},
		{"template_name": "60 Days Credit", "name": "60 Days Credit"},
		{"template_name": "25% Advance", "name": "25% Advance"},
		{"template_name": "50% Advance", "name": "50% Advance"},
		{"template_name": "Letter of Credit (LC)", "name": "Letter of Credit (LC)"}
	]

	for term in terms:
		safe_insert("Payment Terms Template", term, name_field="template_name")


def create_taxes():
	# Custom tax categories or records can be created standardly
	# For custom tax template representation in ERPNext
	tax_templates = [
		{"name": "India GST 18%", "company": "Sarveksha Realty and Inframine LLP", "tax_type": "GST"},
		{"name": "UAE VAT 5%", "company": "Globe Multitrade and Service LLC", "tax_type": "VAT"},
		{"name": "Guinea VAT 18%", "company": "Sarveksha BSTP SAS", "tax_type": "VAT"},
		{"name": "Cameroon VAT 19.25%", "company": "Sarveksha Mining SARL", "tax_type": "VAT"},
		{"name": "Botswana VAT 14%", "company": "Sarveksha Botswana Proprietary Limited", "tax_type": "VAT"},
		{"name": "Odhav Holdings GST 15%", "company": "Odhav Holdings", "tax_type": "GST"},
		{"name": "Sarveksha SL Limited GST 15%", "company": "Sarveksha SL Limited", "tax_type": "GST"},
		{"name": "Baani Minerals GST 15%", "company": "Baani Minerals", "tax_type": "GST"}
	]
	
	for tax in tax_templates:
		safe_insert("Tax Category", {"name": tax["name"]}, name_field="name")


def create_dummy_data():
	companies = [
		"Sarveksha Realty and Inframine LLP",
		"Globe Multitrade and Service LLC",
		"Sarveksha BSTP SAS",
		"Sarveksha Mining SARL",
		"Sarveksha Botswana Proprietary Limited",
		"Odhav Holdings",
		"Sarveksha SL Limited",
		"Baani Minerals"
	]

	# 1. Create approximately 20 Vendors/Suppliers from Excel Sheet data
	excel_vendors = [
		{"vendor_name": "Global Infrastructure", "pan": "", "gstin": "03EKFPS7767R2Z1", "bank_name": "KOTAK MAHINDRA BANK", "bank_branch": "Vibhav Kand Lucknow", "account_no": "3349340868", "ifsc": "KKBK0005204", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Action Construction Equipment", "pan": "", "gstin": "", "bank_name": "ICICI Bank Limited", "bank_branch": "Faridabad", "account_no": "8351000007", "ifsc": "ICIC0000083", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Bissa Engg.", "pan": "", "gstin": "24AMAPB1870D1ZT", "bank_name": "HDFC Bank Ltd", "bank_branch": "Rayson Arcade Gandhidham", "account_no": "50200079115590", "ifsc": "HDFC0004682", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "CruxWeld", "pan": "AAECK2005N", "gstin": "06AAECK2005N1ZO", "bank_name": "ICICI Bank", "bank_branch": "Sector 29 Faridabad", "account_no": "140005001312", "ifsc": "ICIC0001400", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Energy Compressor", "pan": "BMDPM2165A", "gstin": "24BMDPM2165A1ZM", "bank_name": "KOTAK MAHINDRA BANK", "bank_branch": "BLOCK – B –TEJEDRA COMPLEX, ODHAV AHMEDBAD", "account_no": "8949176817", "ifsc": "KKBK0002563", "email": "mkt.energycompressor@gmail.com", "phone": "+91 8401656253", "contact_person": "Mr. Rajesh Goswami"},
		{"vendor_name": "Badri Corporation", "pan": "", "gstin": "24AADFB4258J1ZJ", "bank_name": "STATE BANK OF INDIA,", "bank_branch": "Jamnagar", "account_no": "SBIN0001816", "ifsc": "SBIN0001816", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "ARS International", "pan": "AALCA4690E", "gstin": "24AALCA4690E1ZP", "bank_name": "STATE BANK OF INDIA,", "bank_branch": "Gandhidham.", "account_no": "43377942987", "ifsc": "SBIN0060239", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Chopra Enterprises", "pan": "AAQFC5111Q", "gstin": "24AAQFC5111Q1Z5", "bank_name": "AXIS BANK ", "bank_branch": "Gandhidham (GJ) , Gandhidham", "account_no": "921020011525732", "ifsc": "UTIB0000178", "email": "chopraenterprise21@gmail.com", "phone": "9925017940 ", "contact_person": "Sunil Chopra"},
		{"vendor_name": "Marine Hardware Syndicate", "pan": "ACSPA4930B", "gstin": "24ACSPA4930B1Z2", "bank_name": "ICICI Bank", "bank_branch": "Plot No . 341,  Ward 12/B, Gandhidham , Kutch", "account_no": "25905501103", "ifsc": "ICIC0000259", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Tata Motors", "pan": "AALCT0864B", "gstin": "27AALCT0864B1ZE", "bank_name": "STANDARD CHARTERED BANK", "bank_branch": "MUMBAI BRANCH -90, MAHATMA GANDHI ROAD, FORT, MUMBAI", "account_no": "222-0-526138-4", "ifsc": "SCBL0036084", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Yantralink", "pan": "", "gstin": "24AFOPK0762Q1ZX", "bank_name": "HDFC Bank Ltd", "bank_branch": "NAVRANGPURA, AHMEDABAD", "account_no": "62320012041", "ifsc": "HDFC0000006", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "RR Technologies", "pan": "AAUFR1158A", "gstin": "19AAUFR1158A1Z3", "bank_name": "STATE BANK OF INDIA,", "bank_branch": "Kamalgazi Kolkata", "account_no": "36086785072", "ifsc": "SBIN0018125", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Prime Rigs", "pan": "", "gstin": "", "bank_name": "KOTAK MAHINDRA BANK", "bank_branch": "VANIJYA KUNJ, ENKAY TOWER, GURGAON 122 001, HARAYANA", "account_no": "6045103331", "ifsc": "KKBK0004257", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Indus Furnaces", "pan": "AAQPT3692P", "gstin": "29AAQPT3692P1ZD", "bank_name": "INDIAN OVERSEAS BANK", "bank_branch": "VIDYARANYAPURA BRANCH, BANGLORE ", "account_no": "283702000000085", "ifsc": "IOBA0002837", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Vinspire Agrotech Pvt limited", "pan": "", "gstin": "", "bank_name": "ICICI Bank Limited", "bank_branch": "Ghodasar Ahmedabad", "account_no": "231005501317", "ifsc": "ICIC0002310", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Classic Instruments", "pan": "AABPD7861M", "gstin": "27AABPD7861M1ZF", "bank_name": "UNION BANK OF INDIA,", "bank_branch": "Mandpeshwar Road,Borivali (W),Mumbai", "account_no": "355801010013111", "ifsc": "UBIN0914673", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "OM Enterprises", "pan": "", "gstin": "24AJXPK6770F1ZQ", "bank_name": "ICICI", "bank_branch": "GANDHIDHAM", "account_no": "25905503524", "ifsc": "ICIC0000259", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Central Drug House", "pan": "", "gstin": "", "bank_name": "BANK OF INDIA", "bank_branch": "3,ANSARI ROAD, DARYAGANJ, NEW DELHI", "account_no": "603230100030166", "ifsc": "BKID0006032", "email": "", "phone": "", "contact_person": ""},
		{"vendor_name": "Aavya Logistics", "pan": "", "gstin": "09AAXCA3742K1Z1", "bank_name": "DEVLOPMENT BANK OF SINGAPRORE", "bank_branch": "Noida", "account_no": "8857210000022180", "ifsc": "DBSS0IN0857", "email": "info@aavyalogistics.com", "phone": "", "contact_person": "Mr. Deepak"},
		{"vendor_name": "Bipun Consultancy", "pan": "", "gstin": "20ABGFB1801R1ZN", "bank_name": "STATE BANK OF INDIA,", "bank_branch": "DIPATOLI, RANCHI", "account_no": "44818461706", "ifsc": "SBIN0005991", "email": "", "phone": "91-7979784728", "contact_person": "Mr. Pratyushraj"}
	]

	vendor_names = [v["vendor_name"] for v in excel_vendors]

	for i, v_data in enumerate(excel_vendors):
		v_name = v_data["vendor_name"]
		# Create standard Supplier
		safe_insert("Supplier", {
			"supplier_name": v_name,
			"name": v_name,
			"supplier_group": "Local"
		}, name_field="supplier_name")

		# Create custom Vendor
		safe_insert("Vendor", {
			"vendor_name": v_name,
			"name": v_name,
			"vendor_group": "Local",
			"pan": v_data["pan"],
			"gstin": v_data["gstin"],
			"contact_email": v_data["email"],
			"contact_phone": v_data["phone"],
			"contact_person": v_data["contact_person"]
		}, name_field="vendor_name")

		# Create Vendor Bank Account for each
		comp_idx = i % len(companies)
		comp_name = companies[comp_idx]
		curr = "INR" if "LLP" in comp_name else "AED" if "LLC" in comp_name else "GNF" if "BSTP" in comp_name else "XAF" if "Mining" in comp_name else "BWP" if "Botswana" in comp_name else "SLE"
		
		acc_no = v_data["account_no"] if v_data["account_no"] else f"ACC-{100000+i}"
		b_name = v_data["bank_name"] if v_data["bank_name"] else f"{v_name.split()[0]} Bank"
		ifsc = v_data["ifsc"] if v_data["ifsc"] else ""

		safe_insert("Vendor Bank", {
			"vendor": v_name,
			"bank_name": b_name,
			"account_number": acc_no,
			"currency": curr,
			"company": comp_name,
			"ifsc_code": ifsc,
			"is_default": 1
		}, name_field="account_number")

	# 2. Create 10 Equipments
	eq_types = ["Excavator", "Bulldozer", "Dumper Truck", "Drilling Rig", "Crusher", "Wheel Loader", "Grader", "Crane", "Generator", "Air Compressor"]
	for i in range(10):
		comp_name = companies[i % len(companies)]
		v_name = vendor_names[i % len(vendor_names)]
		safe_insert("Equipment", {
			"equipment_name": f"{eq_types[i]} - {i+1}",
			"equipment_type": eq_types[i],
			"model": f"Model-{2024+i}",
			"serial_number": f"SN-{99900+i}",
			"company": comp_name,
			"purchase_date": today(),
			"purchase_cost": 50000 + (i * 10000),
			"vendor": v_name,
			"status": "Available"
		}, name_field="equipment_name")

	# 3. Create 15 Purchase Orders and Invoices
	for i in range(15):
		comp_name = companies[i % len(companies)]
		v_name = vendor_names[i % len(vendor_names)]
		
		# Create Purchase Orders
		po = safe_insert("Purchase Order", {
			"supplier": v_name,
			"company": comp_name,
			"transaction_date": today(),
			"naming_series": "PO-",
			"items": [
				{"item_code": "Heavy Machinery Spare Parts", "qty": 1, "rate": 1000 * (i+1), "amount": 1000 * (i+1)}
			]
		}, name_field="name")

		po_name = po.name if po else f"MOCK-PO-{100+i}"

		# Create Purchase Invoices
		pi = safe_insert("Purchase Invoice", {
			"supplier": v_name,
			"company": comp_name,
			"posting_date": today(),
			"naming_series": "PINV-",
			"items": [
				{"item_code": "Heavy Machinery Spare Parts", "qty": 1, "rate": 1000 * (i+1), "amount": 1000 * (i+1)}
			]
		}, name_field="name")

		pi_name = pi.name if pi else f"MOCK-PINV-{100+i}"

		# 4. Create 10 Shipment and Customs Clearances
		if i < 10:
			ship = safe_insert("Shipment", {
				"origin_country": "India",
				"destination_country": "Sierra Leone" if i % 2 == 0 else "Cameroon",
				"carrier": "Maersk Cargo" if i % 2 == 0 else "DHL Global",
				"tracking_number": f"TRK-{123000+i}",
				"shipment_date": today(),
				"estimated_delivery_date": add_days(today(), 10),
				"status": "Booked",
				"company": comp_name
			}, name_field="tracking_number")

			ship_name = ship.name if ship else f"MOCK-SHIP-{100+i}"

			safe_insert("Customs Clearance", {
				"shipment": ship_name,
				"port_of_entry": "Port of Freetown" if i % 2 == 0 else "Port of Douala",
				"clearance_agent": "Global Clearances Ltd",
				"customs_declaration_number": f"DEC-{88800+i}",
				"duty_amount": 500 * (i+1),
				"tax_amount": 100 * (i+1),
				"status": "Pending",
				"company": comp_name
			}, name_field="customs_declaration_number")

		# 5. Create 10 Vendor Payment Requests
		if i < 10:
			v_bank = frappe.db.get_value("Vendor Bank", {"vendor": v_name, "company": comp_name}, "name")
			
			# Create schedule first
			sched = safe_insert("Vendor Payment Schedule", {
				"vendor": v_name,
				"company": comp_name,
				"due_date": add_days(today(), 15),
				"amount": 1200 * (i+1),
				"paid_amount": 0,
				"outstanding_amount": 1200 * (i+1),
				"status": "Unpaid"
			}, name_field="name")

			sched_name = sched.name if sched else f"MOCK-SCHED-{100+i}"

			safe_insert("Vendor Payment Request", {
				"vendor": v_name,
				"company": comp_name,
				"amount": 1200 * (i+1),
				"purchase_invoice": pi_name,
				"purchase_order": po_name,
				"status": "Draft",
				"request_date": today(),
				"payment_schedule": sched_name,
				"vendor_bank": v_bank,
				"remarks": f"Demo payment request for item {i+1}."
			}, name_field="name")

		# 6. Create 5 Payment Entries
		if i < 5:
			safe_insert("Payment Entry", {
				"payment_type": "Pay",
				"party_type": "Supplier",
				"party": v_name,
				"company": comp_name,
				"paid_amount": 1200 * (i+1),
				"received_amount": 1200 * (i+1),
				"posting_date": today(),
				"paid_from": f"Default Bank - {comp_name.split()[0][:3].upper()}",
				"paid_to_bank_account": f"ACC-{100000+i}"
			}, name_field="name")


def create_dashboard_and_cards():
	# Programmatically insert Dashboard and Number Cards in the DB
	cards = [
		{"name": "Pending Payments", "label": "Pending Payments", "document_type": "Vendor Payment Request", "function": "Sum", "aggregate_function_fieldname": "amount", "filters_json": '[["Vendor Payment Request","status","in",["Draft","Finance Review","Under Approval"]]]'},
		{"name": "Approved Payments", "label": "Approved Payments", "document_type": "Vendor Payment Request", "function": "Sum", "aggregate_function_fieldname": "amount", "filters_json": '[["Vendor Payment Request","status","=","Approved"]]'},
		{"name": "Overdue Payments", "label": "Overdue Payments", "document_type": "Vendor Payment Schedule", "function": "Sum", "aggregate_function_fieldname": "outstanding_amount", "filters_json": '[["Vendor Payment Schedule","status","!=","Paid"],["Vendor Payment Schedule","due_date","<","' + today() + '"]]'},
		{"name": "Upcoming Payments", "label": "Upcoming Payments", "document_type": "Vendor Payment Schedule", "function": "Sum", "aggregate_function_fieldname": "outstanding_amount", "filters_json": '[["Vendor Payment Schedule","status","!=","Paid"],["Vendor Payment Schedule","due_date",">=","' + today() + '"]]'},
		{"name": "Vendor Summary", "label": "Total Vendors", "document_type": "Supplier", "function": "Count"},
		{"name": "Shipment Summary", "label": "Total Shipments", "document_type": "Shipment", "function": "Count"},
		{"name": "Equipment Summary", "label": "Total Equipment Items", "document_type": "Equipment", "function": "Count"}
	]

	card_links = []
	for card in cards:
		card_doc = safe_insert("Number Card", {
			"name": card["name"],
			"label": card["label"],
			"document_type": card["document_type"],
			"function": card["function"],
			"aggregate_function_fieldname": card.get("aggregate_function_fieldname"),
			"filters_json": card.get("filters_json", "[]"),
			"is_standard": 1,
			"module": "Sarveksha Vendor"
		}, name_field="name")
		
		if card_doc:
			card_links.append({"card": card_doc.name})

	# Create Dashboard
	safe_insert("Dashboard", {
		"dashboard_name": "Vendor Payment Tracking Dashboard",
		"name": "Vendor Payment Tracking Dashboard",
		"is_standard": 1,
		"module": "Sarveksha Vendor",
		"cards": card_links
	}, name_field="dashboard_name")
