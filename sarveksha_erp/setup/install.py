import frappe
from frappe.utils import today, add_days

def after_install():
	print("Creating seed data for Sarveksha ERP...")
	create_tax_configurations()
	create_companies()
	create_vendors()
	create_equipment()
	create_sample_purchase_orders()
	print("Seed data creation complete.")

def create_tax_configurations():
	tax_configs = [
		{
			"country": "India",
			"gst_applicable": 1,
			"gst_percentage": 18.0,
			"tds_applicable": 1,
			"tds_percentage": 10.0,
			"vat_percentage": 0.0,
			"withholding_tax": 0.0,
			"default_tax_rules": "GST 18% and TDS 10% applicable on procurement services.",
			"remarks": "Standard tax rules for India-based operations."
		},
		{
			"country": "Botswana",
			"gst_applicable": 0,
			"gst_percentage": 0.0,
			"tds_applicable": 0,
			"tds_percentage": 0.0,
			"vat_percentage": 14.0,
			"withholding_tax": 7.5,
			"default_tax_rules": "VAT 14% and Withholding 7.5% applicable.",
			"remarks": "Standard VAT and Withholding rules for Botswana."
		},
		{
			"country": "Cameroon",
			"gst_applicable": 0,
			"gst_percentage": 0.0,
			"tds_applicable": 0,
			"tds_percentage": 0.0,
			"vat_percentage": 19.25,
			"withholding_tax": 5.5,
			"default_tax_rules": "VAT 19.25% applicable.",
			"remarks": "Standard tax rules for Cameroon."
		},
		{
			"country": "Sierra Leone",
			"gst_applicable": 0,
			"gst_percentage": 0.0,
			"tds_applicable": 0,
			"tds_percentage": 0.0,
			"vat_percentage": 15.0,
			"withholding_tax": 5.0,
			"default_tax_rules": "VAT 15% applicable.",
			"remarks": "Standard tax rules for Sierra Leone."
		},
		{
			"country": "Guinea",
			"gst_applicable": 0,
			"gst_percentage": 0.0,
			"tds_applicable": 0,
			"tds_percentage": 0.0,
			"vat_percentage": 18.0,
			"withholding_tax": 5.0,
			"default_tax_rules": "VAT 18% applicable.",
			"remarks": "Standard tax rules for Guinea operations."
		},
		{
			"country": "United States",
			"gst_applicable": 0,
			"gst_percentage": 0.0,
			"tds_applicable": 0,
			"tds_percentage": 0.0,
			"vat_percentage": 0.0,
			"withholding_tax": 0.0,
			"default_tax_rules": "No VAT, standard local sales taxes apply.",
			"remarks": "Standard US rules."
		}
	]

	for config in tax_configs:
		if not frappe.db.exists("Sarveksha Tax Configuration", config["country"]):
			doc = frappe.get_doc({"doctype": "Sarveksha Tax Configuration", **config})
			doc.insert(ignore_permissions=True)

def create_companies():
	companies = [
		{
			"company_code": "SRI",
			"company_name": "Sarveksha Realty & Inframine LLP",
			"legal_name": "Sarveksha Realty & Inframine LLP",
			"country": "India",
			"state": "Maharashtra",
			"city": "Mumbai",
			"address": "Sarveksha House, Nariman Point, Mumbai, India",
			"postal_code": "400021",
			"currency": "INR",
			"import_export_code": "AFTFS2557J",
			"fiscal_year_start": "2026-04-01",
			"fiscal_year_end": "2027-03-31",
			"default_warehouse": "Mumbai Port Warehouse",
			"default_bank": "State Bank of India",
			"default_payment_terms": "30% Advance, 70% against BL",
			"default_port": "Mundra, JNPT",
			"default_cfa": "JM Baxi Logistics",
			"phone": "+91-22-12345678",
			"email": "sri@sarveksha.com",
			"website": "www.sarveksha.com",
			"linkedin_url": "https://www.linkedin.com/company/sarveksha-bstp/",
			"authorized_signatory": "Managing Partner",
			"status": "Active"
		},
		{
			"company_code": "OHL",
			"company_name": "Odhav Holdings",
			"legal_name": "Odhav Holdings Private Limited",
			"country": "India",
			"state": "Gujarat",
			"city": "Ahmedabad",
			"address": "Odhav Tower, SG Highway, Ahmedabad, India",
			"postal_code": "380054",
			"currency": "INR",
			"fiscal_year_start": "2026-04-01",
			"fiscal_year_end": "2027-03-31",
			"default_warehouse": "Ahmedabad Depot",
			"default_bank": "ICICI Bank",
			"default_payment_terms": "20% Advance, 80% on delivery",
			"default_port": "Mundra, JNPT",
			"phone": "+91-79-87654321",
			"email": "odhav@sarveksha.com",
			"website": "www.sarveksha.com",
			"linkedin_url": "https://www.linkedin.com/company/sarveksha-bstp/",
			"authorized_signatory": "Director",
			"status": "Active"
		},
		{
			"company_code": "SSL",
			"company_name": "Sarveksha SL Limited",
			"legal_name": "Sarveksha Sierra Leone Limited",
			"country": "Sierra Leone",
			"city": "Freetown",
			"address": "Wilberforce Street, Freetown, Sierra Leone",
			"currency": "USD",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Freetown Port Warehouse",
			"default_bank": "Sierra Leone Commercial Bank",
			"default_payment_terms": "100% LC at sight",
			"default_port": "Freetown",
			"phone": "+232-22-998877",
			"email": "ssl@sarveksha.com",
			"website": "www.sarveksha.com",
			"linkedin_url": "https://www.linkedin.com/company/sarveksha-bstp/",
			"authorized_signatory": "General Manager",
			"status": "Active"
		},
		{
			"company_code": "SMS",
			"company_name": "Sarveksha Mining SARL",
			"legal_name": "Sarveksha Mining SARL",
			"country": "Cameroon",
			"city": "Douala",
			"address": "Avenue Akwa, Douala, Cameroon",
			"currency": "USD",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Douala Logistics Hub",
			"default_bank": "Afriland First Bank",
			"default_payment_terms": "50% Advance, 50% on Dispatch",
			"default_port": "Douala",
			"phone": "+237-677-123456",
			"email": "sms@sarveksha.com",
			"website": "www.sarveksha.com",
			"linkedin_url": "https://www.linkedin.com/company/sarveksha-bstp/",
			"authorized_signatory": "Country Head",
			"status": "Active"
		},
		{
			"company_code": "SBPL",
			"company_name": "Sarveksha Botswana Proprietary Limited",
			"legal_name": "Sarveksha Botswana Proprietary Limited",
			"country": "Botswana",
			"city": "Gaborone",
			"address": "Plot 54321, Broadhurst Industrial, Gaborone, Botswana",
			"currency": "USD",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Gaborone Central Store",
			"default_bank": "First National Bank Botswana",
			"default_payment_terms": "30% Deposit, 70% CAD",
			"default_port": "Durban",
			"phone": "+267-391-2345",
			"email": "sbpl@sarveksha.com",
			"website": "www.sarveksha.com",
			"linkedin_url": "https://www.linkedin.com/company/sarveksha-bstp/",
			"authorized_signatory": "Resident Director",
			"status": "Active"
		},
		{
			"company_code": "SGIN",
			"company_name": "Sarveksha Guinea SARL",
			"legal_name": "Sarveksha Guinea SARL",
			"country": "Guinea",
			"city": "Conakry",
			"address": "Kaloum, Conakry, Guinea",
			"currency": "USD",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Conakry Port Store",
			"default_bank": "Ecobank Guinea",
			"default_payment_terms": "30% Advance, 70% against BL",
			"default_port": "Conakry",
			"phone": "+224-622-000111",
			"email": "sgin@sarveksha.com",
			"website": "www.sarveksha.com",
			"linkedin_url": "https://www.linkedin.com/company/sarveksha-bstp/",
			"authorized_signatory": "Branch Manager",
			"status": "Active"
		}
	]

	for comp in companies:
		if not frappe.db.exists("Sarveksha Company", comp["company_code"]):
			if frappe.db.exists("Sarveksha Tax Configuration", comp["country"]):
				comp["default_tax_configuration"] = comp["country"]
			doc = frappe.get_doc({"doctype": "Sarveksha Company", **comp})
			doc.insert(ignore_permissions=True)

def create_vendors():
	vendors = [
		{
			"vendor_code": "VND-RIGAKU",
			"vendor_name": "Rigaku Corporation",
			"vendor_type": "Manufacturer",
			"country": "Japan",
			"address": "4-14-4, Sendagaya, Shibuya-ku, Tokyo, Japan",
			"contact_person": "Kenji Tanaka",
			"phone": "+81-3-3479-5111",
			"email": "tanaka@rigaku.co.jp",
			"website": "www.rigaku.com",
			"bank_name": "Bank of Tokyo-Mitsubishi UFJ",
			"branch": "Shibuya Branch",
			"account_number": "JP760005111222333",
			"swift": "BOTKJPJT",
			"currency": "USD",
			"payment_terms": "30% Advance, 70% LC at sight",
			"lead_time": 90,
			"vendor_rating": 4.8,
			"preferred_vendor": 1,
			"status": "Active"
		},
		{
			"vendor_code": "VND-MOULIK",
			"vendor_name": "Moulik Doshi Chemicals & Glassware",
			"vendor_type": "Distributor",
			"country": "India",
			"address": "202, Chemical Plaza, GIDC Vadodara, Gujarat, India",
			"contact_person": "Moulik Doshi",
			"phone": "+91-9825012345",
			"email": "moulik.doshi@moulikchemicals.com",
			"bank_name": "HDFC Bank",
			"branch": "Alkapuri Branch",
			"account_number": "50200012345678",
			"ifsc": "HDFC0000012",
			"currency": "INR",
			"payment_terms": "30 days net credit",
			"lead_time": 15,
			"vendor_rating": 4.2,
			"preferred_vendor": 1,
			"gst_applicable": 1,
			"gst_percentage": 18.0,
			"tds_applicable": 1,
			"tds_percentage": 10.0,
			"status": "Active"
		},
		{
			"vendor_code": "VND-RRTECH",
			"vendor_name": "RR Tech Solutions",
			"vendor_type": "Trader",
			"country": "India",
			"address": "104, Tech Park, Andheri East, Mumbai, India",
			"contact_person": "Ramesh Rao",
			"phone": "+91-9820011223",
			"email": "sales@rrtech.co.in",
			"bank_name": "Axis Bank",
			"branch": "Andheri Branch",
			"account_number": "91201004567890",
			"ifsc": "UTIB0000123",
			"currency": "USD",
			"payment_terms": "100% Advance",
			"lead_time": 20,
			"vendor_rating": 4.5,
			"preferred_vendor": 1,
			"status": "Active"
		},
		{
			"vendor_code": "VND-ACE",
			"vendor_name": "ACE Construction Equipment",
			"vendor_type": "Manufacturer",
			"country": "India",
			"address": "Plot 12, Industrial Area, Faridabad, Haryana, India",
			"contact_person": "Vikram Singh",
			"phone": "+91-129-4001100",
			"email": "exports@ace-cranes.com",
			"bank_name": "State Bank of India",
			"branch": "Faridabad Industrial Estate",
			"account_number": "30112233445",
			"ifsc": "SBIN0001234",
			"currency": "USD",
			"payment_terms": "20% Advance, 80% against BL",
			"lead_time": 45,
			"vendor_rating": 4.6,
			"preferred_vendor": 1,
			"status": "Active"
		},
		{
			"vendor_code": "VND-INDUS",
			"vendor_name": "Indus Furnace Systems",
			"vendor_type": "Manufacturer",
			"country": "India",
			"address": "GIDC Makarpura, Vadodara, Gujarat, India",
			"contact_person": "Sanjay Patel",
			"phone": "+91-265-2641122",
			"email": "info@indusfurnace.com",
			"bank_name": "Bank of Baroda",
			"branch": "Makarpura Branch",
			"account_number": "01230200001122",
			"ifsc": "BARB0MAKARP",
			"currency": "USD",
			"payment_terms": "40% Advance, 60% before dispatch",
			"lead_time": 60,
			"vendor_rating": 4.4,
			"preferred_vendor": 1,
			"status": "Active"
		}
	]

	for vendor in vendors:
		if not frappe.db.exists("Sarveksha Vendor", vendor["vendor_code"]):
			doc = frappe.get_doc({"doctype": "Sarveksha Vendor", **vendor})
			doc.insert(ignore_permissions=True)

def create_equipment():
	equipment_list = [
		{
			"hsn_code": "90221900",
			"equipment_name": "Rigaku NEX DE EDXRF Spectrometer",
			"category": "Instrumentation",
			"brand": "Rigaku",
			"manufacturer": "Rigaku Corporation",
			"model": "NEX DE",
			"description": "High-performance Benchtop Energy Dispersive X-ray Fluorescence Spectrometer.",
			"country_of_origin": "Japan",
			"gst_percentage": 18.0,
			"warranty": "24 Months",
			"calibration_required": 1,
			"amc_required": 1,
			"preferred_vendor": "VND-RIGAKU",
			"approximate_cost": 45000.0,
			"latest_purchase_cost": 45000.0,
			"technical_specification": "Element range: Na to U. X-ray tube: 60 kV, 12 W. Detector: FAST SDD.",
			"status": "Active"
		},
		{
			"hsn_code": "70179000",
			"equipment_name": "Chemical Laboratory Glassware Set",
			"category": "Tools",
			"brand": "Borosil",
			"manufacturer": "Borosil Limited",
			"model": "LabSet-Pro",
			"description": "Standard high-borosilicate laboratory glassware including beakers, flasks, and cylinders.",
			"country_of_origin": "India",
			"gst_percentage": 18.0,
			"warranty": "N/A",
			"calibration_required": 0,
			"amc_required": 0,
			"preferred_vendor": "VND-MOULIK",
			"approximate_cost": 1500.0,
			"latest_purchase_cost": 1200.0,
			"technical_specification": "Material: Borosilicate 3.3. Temp resistance: up to 500 C. Meets ISO 3585.",
			"status": "Active"
		},
		{
			"hsn_code": "85176290",
			"equipment_name": "LAN & Networking Equipment Package",
			"category": "Electrical",
			"brand": "Cisco",
			"manufacturer": "Cisco Systems",
			"model": "Catalyst 9300",
			"description": "Managed Gigabit Switch, Routers, and Cat6 Cabling network setup.",
			"country_of_origin": "India",
			"gst_percentage": 18.0,
			"warranty": "36 Months",
			"calibration_required": 0,
			"amc_required": 1,
			"preferred_vendor": "VND-RRTECH",
			"approximate_cost": 12500.0,
			"latest_purchase_cost": 12000.0,
			"technical_specification": "24-Port PoE+ Layer 3 Switch with redundant power supply.",
			"status": "Active"
		},
		{
			"hsn_code": "87051000",
			"equipment_name": "Heavy Duty Hydraulic Boom Truck Crane",
			"category": "Mechanical",
			"brand": "ACE",
			"manufacturer": "ACE Construction Equipment",
			"model": "BT-250",
			"description": "25 Ton Mobile Boom Truck Crane for heavy industrial lifting.",
			"country_of_origin": "India",
			"gst_percentage": 18.0,
			"warranty": "12 Months",
			"calibration_required": 1,
			"amc_required": 1,
			"preferred_vendor": "VND-ACE",
			"approximate_cost": 85000.0,
			"latest_purchase_cost": 82000.0,
			"technical_specification": "Max Lifting Capacity: 25 Tons. Boom Length: 32 Meters. Diesel Engine.",
			"status": "Active"
		},
		{
			"hsn_code": "84178090",
			"equipment_name": "Industrial High Temperature Muffle Furnace",
			"category": "Mechanical",
			"brand": "Indus",
			"manufacturer": "Indus Furnace Systems",
			"model": "IFS-1400",
			"description": "High temperature electric chamber furnace up to 1400 C for material testing.",
			"country_of_origin": "India",
			"gst_percentage": 18.0,
			"warranty": "24 Months",
			"calibration_required": 1,
			"amc_required": 1,
			"preferred_vendor": "VND-INDUS",
			"approximate_cost": 28000.0,
			"latest_purchase_cost": 27500.0,
			"technical_specification": "Chamber size: 300x300x400 mm. Temp uniformity: +/- 5 C. PID Controller.",
			"status": "Active"
		}
	]

	for eq in equipment_list:
		if not frappe.db.exists("Sarveksha Equipment", eq["hsn_code"]):
			doc = frappe.get_doc({"doctype": "Sarveksha Equipment", **eq})
			doc.insert(ignore_permissions=True)

def create_sample_purchase_orders():
	pos = [
		{
			"po_number": "PO-OHL-2026-0001",
			"company": "OHL",
			"vendor": "VND-RIGAKU",
			"equipment": "90221900",
			"status": "Purchase Order",
			"currency": "USD",
			"quantity": 1,
			"rate": 45000.0,
			"grand_total": 45000.0,
			"prepared_by": "Procurement Executive",
			"verified_by": "Procurement Manager",
			"approved_by": "Director",
			"quotation_number": "RIG-QUO-240426",
			"quotation_date": add_days(today(), -10),
			"payment_terms": "30% Advance, 70% LC at sight",
			"delivery_location": "Ahmedabad Depot, Gujarat, India",
			"port": "Mundra"
		},
		{
			"po_number": "PO-SRI-2026-0002",
			"company": "SRI",
			"vendor": "VND-MOULIK",
			"equipment": "70179000",
			"status": "Purchase Order",
			"currency": "INR",
			"quantity": 10,
			"rate": 1200.0,
			"grand_total": 12000.0,
			"prepared_by": "Purchase Officer",
			"verified_by": "Senior Manager",
			"approved_by": "Partner",
			"quotation_number": "MDK-PO-09",
			"quotation_date": add_days(today(), -5),
			"payment_terms": "30 days net credit",
			"delivery_location": "Mumbai Port Warehouse, India",
			"port": "JNPT"
		},
		{
			"po_number": "PO-SSL-2026-0003",
			"company": "SSL",
			"vendor": "VND-RRTECH",
			"equipment": "85176290",
			"status": "Quotation",
			"currency": "USD",
			"quantity": 1,
			"rate": 12000.0,
			"grand_total": 12000.0,
			"prepared_by": "Logistics Coordinator",
			"quotation_number": "RRT-SL-2006",
			"quotation_date": add_days(today(), -3),
			"payment_terms": "100% Advance",
			"delivery_location": "Freetown Port Warehouse, Sierra Leone",
			"port": "Freetown"
		}
	]

	for po_data in pos:
		if not frappe.db.exists("Sarveksha Purchase Order", {"po_number": po_data["po_number"]}):
			doc = frappe.get_doc({"doctype": "Sarveksha Purchase Order", **po_data})
			doc.insert(ignore_permissions=True)
