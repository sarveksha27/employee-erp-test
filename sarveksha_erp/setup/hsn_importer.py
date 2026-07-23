import frappe

# Engineering HSN Chapters filter according to HSN-Codes-for-GST-Enrolment.pdf:
# Chapter 84: Mechanical Appliances & Boilers
# Chapter 85: Electrical Machinery & Equipment
# Chapter 87: Vehicles, Cranes & Heavy Handling Equipment
# Chapter 90: Measuring, Testing & Precision Instruments (Spectrometers, Lab Equipment)

ENGINEERING_HSN_CHAPTERS = ["84", "85", "87", "90"]

def filter_and_import_engineering_equipment(equipment_records):
	"""
	Filters incoming equipment list to only include Engineering Goods and Materials
	based on HSN Chapters (84, 85, 87, 90) and inserts them into Sarveksha Equipment.
	"""
	imported_count = 0
	for item in equipment_records:
		hsn = str(item.get("hsn_code", "")).strip()
		chapter = hsn[:2]
		
		# Ensure only engineering goods are processed
		if chapter in ENGINEERING_HSN_CHAPTERS or item.get("category") in ["Mechanical", "Electrical", "Instrumentation", "Tools"]:
			if not frappe.db.exists("Sarveksha Equipment", hsn):
				doc = frappe.get_doc({
					"doctype": "Sarveksha Equipment",
					"hsn_code": hsn,
					"equipment_name": item.get("equipment_name"),
					"category": item.get("category", "Mechanical"),
					"brand": item.get("brand"),
					"manufacturer": item.get("manufacturer"),
					"model": item.get("model"),
					"description": item.get("description"),
					"technical_specification": item.get("technical_specification"),
					"gst_percentage": item.get("gst_percentage", 18.0),
					"preferred_vendor": item.get("preferred_vendor"),
					"status": "Active"
				})
				doc.insert(ignore_permissions=True)
				imported_count += 1
				
	return imported_count
