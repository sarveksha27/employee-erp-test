import frappe

def execute():
    footers = {
        "Sarveksha SL Limited": "Mining, Mineral Processing, Mining Services, Mineral Trading, Public Works; General Trading; Construction & Civil & Erection Work | Reg No: SL120624SARVE22162 | TIN NO: 1001412648",
        "Sarveksha Botswana Proprietary Limited": "Equipment and Public Works; General Trading; Construction & Civil & Erection Work | UIN: BW00009608412",
        "Sarveksha Mining SARL": "BATIMENT ET TRAVAUX PUBLICS; COMMERCE GENERAL (IMPORT-EXPORT); REPRESENTATION COMMERCIALE; AGRO-BUSINESS; PECHE; CONSULTATION; TRANSPORT LOGISTIQUE; PRESTATIONS DE SERVICES; DIVERS. | RCCM: CM-NSI-02-2025-B12-00560",
        "Baani Minerals": "Mining, Mining Services, Construction, Public Works, Trading and Commerce | RCCM: CM-NSI-02-2025-B12-00784",
        "Sarveksha BSTP SAS": "BATIMENT ET TRAVAUX PUBLICS; COMMERCE GENERAL (IMPORT-EXPORT); REPRESENTATION COMMERCIALE; AGRO-BUSINESS; PECHE; CONSULTATION; TRANSPORT LOGISTIQUE; PRESTATIONS DE SERVICES; DIVERS."
    }

    for company_name, footer_text in footers.items():
        if frappe.db.exists("Company", company_name):
            doc = frappe.get_doc("Company", company_name)
            doc.registration_details = footer_text
            doc.save(ignore_permissions=True)
            print(f"Updated footer for {company_name}")

    frappe.db.commit()
    print("Done updating company footers.")
