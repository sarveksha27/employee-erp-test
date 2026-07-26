import frappe

def execute():
    if frappe.db.exists("Equipment", "EQ-03281"):
        doc = frappe.get_doc("Equipment", "EQ-03281")
        doc.brand = "Caterpillar"
        doc.manufacturer = "Caterpillar Inc."
        doc.unit = "Nos"
        
        # Check if country exists, if not use India
        if frappe.db.exists("Country", "United States"):
            doc.country_of_origin = "United States"
        else:
            doc.country_of_origin = "India"
            
        doc.specification = "High power excavator with 15 ton lifting capacity"
        doc.gst_percentage = 18
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated EQ-03281 successfully!")
    else:
        print("EQ-03281 not found")
