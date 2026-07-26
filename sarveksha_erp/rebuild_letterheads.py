import frappe

def execute():
    # 1. Fetch the existing India footer to preserve it
    india_footer = ""
    if frappe.db.exists("Letter Head", "Sarveksha Realty & Inframine LLP"):
        india_footer = frappe.db.get_value("Letter Head", "Sarveksha Realty & Inframine LLP", "footer") or ""
    
    # 2. Delete all existing letterheads so we can start perfectly clean
    frappe.db.sql("DELETE FROM `tabLetter Head`")
    
    # 3. Define the perfect matrix of Name -> Image -> Footer
    letterheads = [
        {
            "name": "India (Sarveksha Realty)",
            "image": "/files/LETER HEAD SRI India.png",
            "footer": india_footer or '<div style="text-align:center; font-size:9px; color:#666; border-top:1px solid #ccc; padding-top:4px; margin-top:4px;">Sarveksha Realty &amp; Inframine LLP | Sparsh 303, Plot 101-102, Sec 44 Seawoods, Navi Mumbai, 400706 | Phone: (+91) 9769008220 | Email: sudheerg@sarveksha.com</div>'
        },
        {
            "name": "Botswana (Sarveksha Botswana)",
            "image": "/files/LETTER HEAD Botswana.png",
            "footer": '<div style="text-align:center; font-size:9px; color:#666; border-top:1px solid #ccc; padding-top:4px; margin-top:4px;"><strong>Sarveksha Botswana Proprietary Limited</strong><br>Equipment and Public Works; General Trading; Construction & Civil & Erection Work | UIN: BW00009608412</div>'
        },
        {
            "name": "Cameroon (Sarveksha Mining SARL)",
            "image": "/files/LETTER HEAD camerron.png",
            "footer": '<div style="text-align:center; font-size:9px; color:#666; border-top:1px solid #ccc; padding-top:4px; margin-top:4px;"><strong>Sarveksha Mining SARL</strong><br>BATIMENT ET TRAVAUX PUBLICS; COMMERCE GENERAL (IMPORT-EXPORT); REPRESENTATION COMMERCIALE; AGRO-BUSINESS; PECHE; CONSULTATION; TRANSPORT LOGISTIQUE; PRESTATIONS DE SERVICES; DIVERS. | RCCM: CM-NSI-02-2025-B12-00560</div>'
        },
        {
            "name": "Cameroon (Baani Minerals)",
            "image": "/files/LETTER HEAD cameroon banni.png",
            "footer": '<div style="text-align:center; font-size:9px; color:#666; border-top:1px solid #ccc; padding-top:4px; margin-top:4px;"><strong>Baani Minerals</strong><br>Mining, Mining Services, Construction, Public Works, Trading and Commerce | RCCM: CM-NSI-02-2025-B12-00784</div>'
        },
        {
            "name": "Sierra Leone (Sarveksha SL Limited)",
            "image": "/files/LETTER HEAD Sarveksha SL Limited.png",
            "footer": '<div style="text-align:center; font-size:9px; color:#666; border-top:1px solid #ccc; padding-top:4px; margin-top:4px;"><strong>Sarveksha SL Limited</strong><br>Mining, Mineral Processing, Mining Services, Mineral Trading, Public Works; General Trading; Construction & Civil & Erection Work | Reg No: SL120624SARVE22162 | TIN NO: 1001412648</div>'
        },
        {
            "name": "Guinea (Sarveksha BSTP SAS)",
            "image": "/files/LETTER HEAD Sarveksha BSTP.png",
            "footer": '<div style="text-align:center; font-size:9px; color:#666; border-top:1px solid #ccc; padding-top:4px; margin-top:4px;"><strong>Sarveksha BSTP SAS</strong><br>BATIMENT ET TRAVAUX PUBLICS; COMMERCE GENERAL (IMPORT-EXPORT); REPRESENTATION COMMERCIALE; AGRO-BUSINESS; PECHE; CONSULTATION; TRANSPORT LOGISTIQUE; PRESTATIONS DE SERVICES; DIVERS.</div>'
        }
    ]

    for lh in letterheads:
        doc = frappe.new_doc("Letter Head")
        doc.letter_head_name = lh["name"]
        doc.image = lh["image"]
        doc.footer = lh["footer"]
        # Set India as default
        if "India" in lh["name"]:
            doc.is_default = 1
        doc.insert(ignore_permissions=True)
        print(f"Created Letter Head: {lh['name']}")

    frappe.db.commit()
    print("Done rebuilding letterheads.")
