import frappe

def execute():
    # Port mapping from the boss's handwritten note:
    # GUI = Guinea → Conakry
    # SL  = Sierra Leone → Freetown
    # BTS = Botswana → Durban (sea port for landlocked Botswana)
    # CN  = Cameroon → Douala
    # SRI = India → Mumbai, Mundra

    companies = frappe.get_all("Company", fields=["name", "country"])

    COUNTRY_PORT_MAP = {
        "India":        "Mumbai, Mundra",
        "Guinea":       "Conakry",
        "Sierra Leone": "Freetown",
        "Botswana":     "Durban",
        "Cameroon":     "Douala",
    }

    for c in companies:
        port = COUNTRY_PORT_MAP.get(c.country)
        if port:
            frappe.db.set_value("Company", c.name, "custom_default_port", port, update_modified=False)
            print(f"  {c.name} [{c.country}] -> {port}")

    frappe.db.commit()
    print("\nDone! All ports updated from boss's handwritten note.")
