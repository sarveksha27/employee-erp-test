import frappe
from frappe.utils import today, add_days

def after_install():
	print("Creating seed data for Sarveksha ERP...")
	create_tax_configurations()
	create_companies()
	create_vendors()
	create_equipment()
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
		# Check if country exists in Frappe Country doctype or create config directly
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
			"currency": "INR",
			"fiscal_year_start": "2026-04-01",
			"fiscal_year_end": "2027-03-31",
			"default_warehouse": "Mumbai Port Warehouse",
			"default_bank": "State Bank of India",
			"default_payment_terms": "30% Advance, 70% against BL",
			"phone": "+91-22-12345678",
			"email": "sri@sarveksha.com",
			"website": "www.sarveksha.com",
			"authorized_signatory": "Managing Partner",
			"status": "Active"
		},
		{
			"company_code": "OHL",
			"company_name": "Odhav Holdings",
			"legal_name": "Odhav Holdings Private Limited",
			"country": "India",
			"currency": "INR",
			"fiscal_year_start": "2026-04-01",
			"fiscal_year_end": "2027-03-31",
			"default_warehouse": "Ahmedabad Depot",
			"default_bank": "ICICI Bank",
			"default_payment_terms": "20% Advance, 80% on delivery",
			"phone": "+91-79-87654321",
			"email": "odhav@sarveksha.com",
			"website": "www.odhav.com",
			"authorized_signatory": "Director",
			"status": "Active"
		},
		{
			"company_code": "SSL",
			"company_name": "Sarveksha SL Limited",
			"legal_name": "Sarveksha Sierra Leone Limited",
			"country": "Sierra Leone",
			"currency": "SLE",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Freetown Port Warehouse",
			"default_bank": "Sierra Leone Commercial Bank",
			"default_payment_terms": "100% LC at sight",
			"phone": "+232-22-998877",
			"email": "ssl@sarveksha.com",
			"website": "www.sarvekshasl.com",
			"authorized_signatory": "General Manager",
			"status": "Active"
		},
		{
			"company_code": "GMS",
			"company_name": "Globe Multitrade & Service LLC",
			"legal_name": "Globe Multitrade & Service LLC",
			"country": "United States",
			"currency": "USD",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Houston Main Warehouse",
			"default_bank": "Chase Bank",
			"default_payment_terms": "Net 45 Days",
			"phone": "+1-713-555-0199",
			"email": "gms@globemultitrade.com",
			"website": "www.globemultitrade.com",
			"authorized_signatory": "CEO",
			"status": "Active"
		},
		{
			"company_code": "SMS",
			"company_name": "Sarveksha Mining SARL",
			"legal_name": "Sarveksha Mining SARL",
			"country": "Cameroon",
			"currency": "XAF",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Douala Logistics Hub",
			"default_bank": "Afriland First Bank",
			"default_payment_terms": "50% Advance, 50% on Dispatch",
			"phone": "+237-677-123456",
			"email": "sms@sarveksha.com",
			"website": "www.sarvekshamining.com",
			"authorized_signatory": "Country Head",
			"status": "Active"
		},
		{
			"company_code": "SBPL",
			"company_name": "Sarveksha Botswana Proprietary Limited",
			"legal_name": "Sarveksha Botswana Proprietary Limited",
			"country": "Botswana",
			"currency": "BWP",
			"fiscal_year_start": "2026-01-01",
			"fiscal_year_end": "2026-12-31",
			"default_warehouse": "Gaborone Central Store",
			"default_bank": "First National Bank Botswana",
			"default_payment_terms": "30% Deposit, 70% CAD",
			"phone": "+267-391-2345",
			"email": "sbpl@sarveksha.com",
			"website": "www.sarvekshabotswana.co.bw",
			"authorized_signatory": "Resident Director",
			"status": "Active"
		}
	]

	for comp in companies:
		if not frappe.db.exists("Sarveksha Company", comp["company_code"]):
			# Set tax configuration link if exists
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
		}
	]

	for eq in equipment_list:
		if not frappe.db.exists("Sarveksha Equipment", eq["hsn_code"]):
			doc = frappe.get_doc({"doctype": "Sarveksha Equipment", **eq})
			doc.insert(ignore_permissions=True)
