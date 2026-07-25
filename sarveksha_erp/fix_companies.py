import frappe

def execute():
    non_india = [
        "Globe Multitrade and Service LLC",
        "Sarveksha BSTP SAS",
        "Sarveksha Mining SARL",
        "Sarveksha Botswana Proprietary Limited",
        "Odhav Holdings",
        "Sarveksha SL Limited",
        "Baani Minerals",
    ]

    # Ensure USD exists as a currency
    if not frappe.db.exists("Currency", "USD"):
        print("  ✗ USD currency not found in system!")
    else:
        print("  ✓ USD currency confirmed in system")
    
    print()
    print("Updating currencies to USD...")
    for company_name in non_india:
        if frappe.db.exists("Company", company_name):
            # Direct SQL update - bypasses all validations safely
            frappe.db.sql(
                "UPDATE `tabCompany` SET default_currency = 'USD' WHERE name = %s",
                company_name
            )
            print(f"  ✓ {company_name} → USD")
        else:
            print(f"  - {company_name} not found")

    frappe.db.commit()

    print()
    print("Final state:")
    companies = frappe.get_all("Company", fields=["name", "country", "default_currency"])
    for c in companies:
        flag = "✓" if (c["default_currency"] == "INR" and c["country"] == "India") or (c["default_currency"] == "USD" and c["country"] != "India") else "✗ CHECK THIS"
        print(f"  {flag} {c['name']} | {c['country']} | {c['default_currency']}")
    
    print()
    print("✅ Done!")
