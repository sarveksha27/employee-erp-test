import frappe

def execute():
    # Get all companies except the Indian one
    companies = frappe.get_all("Company", filters={"name": ("!=", "Sarveksha Realty and Inframine LLP")})
    
    updated_count = 0
    for c in companies:
        frappe.db.set_value("Company", c.name, "default_currency", "USD")
        updated_count += 1
        print(f"Updated {c.name} to USD")
            
    frappe.db.commit()
    print(f"Successfully updated {updated_count} companies to USD via db.set_value.")
