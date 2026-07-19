# Copyright (c) 2026, Sarveksha Group and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class SarvekshaPurchaseOrder(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		# Resolve naming series
		if not self.naming_series:
			self.naming_series = "PO-.company.-.YYYY.-.####"
		
		# Replace .company. token manually if present, because standard make_autoname expects company field
		series = self.naming_series
		if ".company." in series:
			comp_code = self.company or "GEN"
			series = series.replace(".company.", comp_code)
		
		self.name = make_autoname(series)
		self.po_number = self.name

	def validate(self):
		self.calculate_totals()
		self.validate_dates()

	def calculate_totals(self):
		qty = float(self.quantity or 0.0)
		rate = float(self.rate or 0.0)
		discount = float(self.discount or 0.0)
		tax = float(self.tax or 0.0)
		freight = float(self.freight or 0.0)
		packing = float(self.packing or 0.0)
		insurance = float(self.insurance or 0.0)
		other = float(self.other_charges or 0.0)

		self.grand_total = (qty * rate) - discount + tax + freight + packing + insurance + other

	def validate_dates(self):
		if self.quotation_date and self.proforma_invoice_date:
			if getdate(self.proforma_invoice_date) < getdate(self.quotation_date):
				frappe.throw(_("Proforma Invoice Date cannot be before Quotation Date."))


@frappe.whitelist()
def parse_po_pdf(file_url):
	import re
	
	if not file_url:
		return {}
		
	# Get the file document
	file_doc = frappe.get_doc("File", {"file_url": file_url})
	file_path = file_doc.get_full_path()
	
	text = ""
	
	try:
		import pypdf
		reader = pypdf.PdfReader(file_path)
		for page in reader.pages:
			val = page.extract_text()
			if val:
				text += val
	except Exception:
		# Fallback: use filename or mock extraction
		text = file_doc.file_name or ""
	
	extracted_data = {}
	text_lower = text.lower()
	
	# 1. Detect Company
	if "inframine" in text_lower or "realty" in text_lower or "sri" in text_lower:
		extracted_data["company"] = "SRI"
	elif "odhav" in text_lower or "ohl" in text_lower:
		extracted_data["company"] = "OHL"
	elif "sl limited" in text_lower or "sierra leone" in text_lower:
		extracted_data["company"] = "SSL"
	elif "globe multitrade" in text_lower or "gms" in text_lower:
		extracted_data["company"] = "GMS"
	elif "mining sarl" in text_lower or "cameroun" in text_lower:
		extracted_data["company"] = "SMS"
	elif "botswana" in text_lower or "sbpl" in text_lower:
		extracted_data["company"] = "SBPL"
		
	# 2. Detect Vendor
	if "rigaku" in text_lower:
		extracted_data["vendor"] = "VND-RIGAKU"
	elif "moulik" in text_lower or "doshi" in text_lower:
		extracted_data["vendor"] = "VND-MOULIK"
		
	# 3. Detect Equipment
	if "nex de" in text_lower or "spectrometer" in text_lower or "90221900" in text_lower:
		extracted_data["equipment"] = "90221900"
	elif "chemical" in text_lower or "glassware" in text_lower or "70179000" in text_lower:
		extracted_data["equipment"] = "70179000"
		
	# 4. Extract Quote / PI Details
	pi_match = re.search(r"(?:pi|proforma|invoice|po)\s*(?:no|number)?\s*[:#-]?\s*([A-Za-z0-9-/]+)", text, re.IGNORECASE)
	if pi_match:
		extracted_data["proforma_invoice_number"] = pi_match.group(1)
		
	# 5. Extract Rate / Totals
	total_match = re.search(r"(?:grand\s+)?total\s*(?:amount)?\s*[:=-]?\s*(?:usd|inr)?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
	if total_match:
		try:
			val = float(total_match.group(1).replace(",", ""))
			extracted_data["grand_total"] = val
		except Exception:
			pass
			
	rate_match = re.search(r"(?:rate|price)\s*[:=-]?\s*(?:usd|inr)?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
	if rate_match:
		try:
			val = float(rate_match.group(1).replace(",", ""))
			extracted_data["rate"] = val
		except Exception:
			pass

	qty_match = re.search(r"(?:qty|quantity)\s*[:=-]?\s*(\d+)", text, re.IGNORECASE)
	if qty_match:
		try:
			extracted_data["quantity"] = float(qty_match.group(1))
		except Exception:
			pass

	tax_match = re.search(r"(?:tax|gst|vat)\s*(?:amount)?\s*[:=-]?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
	if tax_match:
		try:
			extracted_data["tax"] = float(tax_match.group(1).replace(",", ""))
		except Exception:
			pass

	freight_match = re.search(r"(?:freight|shipping)\s*[:=-]?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
	if freight_match:
		try:
			extracted_data["freight"] = float(freight_match.group(1).replace(",", ""))
		except Exception:
			pass
			
	return extracted_data
