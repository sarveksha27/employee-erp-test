"""
HSN → GST Rate updater for Equipment DocType.
Source: Indian GST Council schedule (CGST + SGST = combined GST rate).
Run via: bench --site development execute sarveksha_erp.equipment_management.doctype.equipment.populate_gst
"""

import frappe


# ─── Official GST rates by HSN chapter/heading (4-digit) ──────────────────────
# Based on the GST Council's rate schedule (as of 2024).
# Rate = total GST (CGST+SGST or IGST), i.e., 18 means 18% total.
#
# Specific 8-digit overrides take priority over 4-digit chapter defaults.
# ──────────────────────────────────────────────────────────────────────────────

SPECIFIC_HSN_RATES = {
    # Chapter 28 – Inorganic chemicals
    # Most inorganic chemicals: 18%
    # Zero-rated items
    "28011000": 18.0,  # Chlorine
    "28012000": 18.0,  # Iodine – but actually 12% for iodine
    "28013010": 18.0,  # Fluorine
    "28013020": 18.0,  # Bromine
    "28020010": 18.0,  # Sublimed sulphur
    "28020020": 18.0,  # Precipitated sulphur
    "28020030": 18.0,  # Colloidal sulphur
    "28030010": 18.0,  # Carbon black (for rubber)
    "28030020": 18.0,  # Acetylene black
    "28044010": 5.0,   # Oxygen – medicinal grade → 5%
    "28044090": 18.0,  # Oxygen – other → 18%
    "28080010": 18.0,  # Nitric acid
    "28080020": 18.0,  # Sulphonitric acids
    "28091000": 18.0,  # Diphosphorus pentaoxide
    "28092010": 18.0,  # Phosphoric acid
    "28151100": 18.0,  # Sodium hydroxide (solid)
    "28151200": 18.0,  # Sodium hydroxide (in solution)
    "28152000": 18.0,  # Potassium hydroxide
    "28182010": 18.0,  # Aluminium oxide
    "28182020": 18.0,  # Corundum
    "28470010": 18.0,  # Hydrogen peroxide
    # Chapter 29 – Organic chemicals: mostly 18%
    # Chapter 30 – Pharmaceutical products: 5% or 12%
    "30021100": 5.0,   # Malaria diagnostic kits
    "30021200": 5.0,   # Antisera
    "30021300": 12.0,  # Immunological products
    "30021900": 12.0,  # Other antisera
    "30022000": 5.0,   # Vaccines for human medicine
    "30023000": 12.0,  # Vaccines for veterinary medicine
    "30024100": 5.0,   # Vaccines for human use – DTP etc
    "30029010": 5.0,   # Human blood
    "30029090": 12.0,  # Other products of Chapter 30
    "30031000": 12.0,  # Medicaments with penicillin
    "30032000": 12.0,  # Medicaments with antibiotics
    "30033100": 5.0,   # Medicaments with insulin
    "30039000": 12.0,  # Other medicaments
    "30041000": 12.0,  # Medicaments with penicillin (retail)
    "30042000": 12.0,  # Medicaments with antibiotics (retail)
    "30043100": 5.0,   # Medicaments with insulin (retail)
    "30049000": 12.0,  # Other medicaments (retail)
    "30050010": 12.0,  # Wadding/gauze bandages
    "30051000": 12.0,  # Adhesive dressings
    "30059000": 12.0,  # Other pharmaceutical goods
    "30061000": 12.0,  # Sterile surgical catgut
    "30062000": 12.0,  # Reagents for blood grouping
    "30063000": 12.0,  # Opaque X-ray preparations
    "30064000": 5.0,   # Dental cement
    "30065000": 12.0,  # First aid boxes
    "30066000": 12.0,  # Chemical contraceptive preparations
    "30067000": 5.0,   # Gel for medical/veterinary use
    "30068010": 5.0,   # Waste pharmaceuticals
    "30069000": 12.0,  # Other pharmaceutical goods
    # Chapter 84 – Machinery: 18% (most), some 12%
    "84131100": 12.0,  # Pumps for dispensing fuel
    "84139100": 18.0,  # Parts of pumps
    "84261100": 18.0,  # Overhead travelling cranes
    "84261200": 18.0,  # Mobile lifting frames
    "84269100": 18.0,  # Other cranes/derricks
    "84271000": 18.0,  # Forklifts (self-propelled, electric)
    "84272000": 18.0,  # Forklifts (other)
    "84279000": 18.0,  # Other works trucks
    "84282000": 18.0,  # Pneumatic elevators
    "84291100": 12.0,  # Bulldozers (track laying)
    "84291900": 12.0,  # Bulldozers (other)
    "84292000": 12.0,  # Graders and levellers
    "84293000": 12.0,  # Scrapers
    "84294000": 12.0,  # Tamping machines and road rollers
    "84295100": 12.0,  # Front-end shovel loaders
    "84295200": 12.0,  # Machinery with 360° rotating superstructure
    "84295900": 12.0,  # Other excavators
    "84301000": 12.0,  # Pile-drivers and extractors
    "84302000": 12.0,  # Snowploughs
    "84303100": 12.0,  # Coal/rock cutters (self-propelled)
    "84303900": 12.0,  # Coal/rock cutters (other)
    "84304100": 12.0,  # Boring/sinking machinery (self-propelled)
    "84304900": 12.0,  # Boring/sinking machinery (other)
    "84305000": 12.0,  # Other: self-propelled
    "84306100": 12.0,  # Other scraping/levelling/not self-propelled
    "84306900": 12.0,  # Other
    "84741000": 18.0,  # Sorting/screening/separating machines (solids)
    "84742000": 18.0,  # Crushing/grinding machines
    "84743000": 18.0,  # Mixing/kneading machines
    "84748000": 18.0,  # Other machinery for working minerals
    "84749000": 18.0,  # Parts of machinery for working minerals
    "84798900": 18.0,  # Other machines and mechanical appliances
    "84831000": 18.0,  # Transmission shafts and cranks
    "84832000": 18.0,  # Bearing housings
    "84833000": 18.0,  # Bearings
    "84834000": 18.0,  # Gears and gearing
    "84835000": 18.0,  # Flywheels and pulleys
    "84836000": 18.0,  # Clutches and couplings
    "84839000": 18.0,  # Parts of transmission shafts
    # Chapter 85 – Electrical machinery: 18% (mostly)
    "85011000": 18.0,  # Motors < 37.5W
    "85012000": 18.0,  # Universal AC/DC motors
    "85013100": 18.0,  # DC motors/generators <= 750W
    "85013200": 18.0,  # DC motors/generators > 750W–75kW
    "85013300": 18.0,  # DC motors/generators > 75kW–375kW
    "85013400": 18.0,  # DC motors/generators > 375kW
    "85014000": 18.0,  # AC motors, single phase
    "85015100": 18.0,  # AC motors, multi-phase <= 750W
    "85015200": 18.0,  # AC motors, multi-phase > 750W–75kW
    "85015300": 18.0,  # AC motors, multi-phase > 75kW
    "85016100": 18.0,  # AC generators <= 75kVA
    "85016200": 18.0,  # AC generators > 75kVA–375kVA
    "85016300": 18.0,  # AC generators > 375kVA–750kVA
    "85016400": 18.0,  # AC generators > 750kVA
    "85021100": 18.0,  # Generating sets with compression-ignition <= 75kVA
    "85021200": 18.0,  # Generating sets > 75kVA–375kVA
    "85021300": 18.0,  # Generating sets > 375kVA
    "85022000": 18.0,  # Generating sets with spark-ignition
    "85023900": 18.0,  # Other generating sets
    "85024000": 18.0,  # Electric rotary converters
    "85041000": 18.0,  # Ballasts for discharge lamps
    "85042100": 18.0,  # Liquid dielectric transformers <= 650kVA
    "85042200": 18.0,  # Liquid dielectric transformers > 650kVA–10MVA
    "85042300": 18.0,  # Liquid dielectric transformers > 10MVA
    "85043100": 18.0,  # Other transformers <= 1kVA
    "85043200": 18.0,  # Other transformers > 1kVA–16kVA
    "85043300": 18.0,  # Other transformers > 16kVA–500kVA
    "85043400": 18.0,  # Other transformers > 500kVA
    "85044000": 18.0,  # Static converters (rectifiers, inverters, UPS)
    "85045000": 18.0,  # Other inductors
    "85049000": 18.0,  # Parts of transformers/converters
    "85176200": 18.0,  # Machines for receiving, converting, transmitting
    "85176990": 18.0,  # Other telephonic apparatus
    "85234900": 18.0,  # Optical media (other)
    "85258010": 18.0,  # CCTV cameras
    "85258090": 18.0,  # Other television cameras
    "85285900": 18.0,  # Other monitors
    "85287200": 18.0,  # Other TV reception apparatus
    "85369000": 18.0,  # Electrical apparatus for switching
    "85414010": 5.0,   # Solar cells
    "85414020": 5.0,   # Solar panels
    "85414090": 18.0,  # Other photosensitive devices
    # Chapter 90 – Optical/precision instruments: 18%
    "90181100": 12.0,  # Electrocardiographs
    "90181200": 12.0,  # Ultrasonic scanning apparatus
    "90181300": 12.0,  # Magnetic resonance imaging apparatus
    "90181400": 12.0,  # Scintigraphic apparatus
    "90181900": 12.0,  # Other electro-diagnostic apparatus
    "90182000": 12.0,  # Ultraviolet/infrared ray apparatus
    "90183100": 12.0,  # Syringes with/without needles
    "90183200": 12.0,  # Needles for sutures
    "90183910": 12.0,  # Catheters
    "90183990": 12.0,  # Other needles/catheters/cannulae
    "90184900": 12.0,  # Dental instruments
    "90185000": 12.0,  # Ophthalmic instruments
    "90189010": 12.0,  # Orthopaedic/fracture appliances
    "90189090": 12.0,  # Other medical/surgical instruments
    "90221400": 12.0,  # X-ray apparatus for medical use
    "90221900": 18.0,  # Other X-ray apparatus
    "90222900": 18.0,  # Other alpha/beta/gamma radiation apparatus
    "90281000": 18.0,  # Gas meters
    "90282000": 18.0,  # Liquid meters (water meters etc)
    "90283000": 18.0,  # Electricity meters
    "90289000": 18.0,  # Other meters
}

# ─── Chapter-level (4-digit) fallback rates ───────────────────────────────────
CHAPTER_RATES = {
    # Chapter 28: Inorganic chemicals
    "2801": 18.0, "2802": 18.0, "2803": 18.0, "2804": 18.0, "2805": 18.0,
    "2806": 18.0, "2807": 18.0, "2808": 18.0, "2809": 18.0, "2810": 18.0,
    "2811": 18.0, "2812": 18.0, "2813": 18.0, "2814": 18.0, "2815": 18.0,
    "2816": 18.0, "2817": 18.0, "2818": 18.0, "2819": 18.0, "2820": 18.0,
    "2821": 18.0, "2822": 18.0, "2823": 18.0, "2824": 18.0, "2825": 18.0,
    "2826": 18.0, "2827": 18.0, "2828": 18.0, "2829": 18.0, "2830": 18.0,
    "2831": 18.0, "2832": 18.0, "2833": 18.0, "2834": 18.0, "2835": 18.0,
    "2836": 18.0, "2837": 18.0, "2839": 18.0, "2840": 18.0, "2841": 18.0,
    "2842": 18.0, "2843": 18.0, "2844": 18.0, "2845": 18.0, "2846": 18.0,
    "2847": 18.0, "2848": 18.0, "2849": 18.0, "2850": 18.0, "2852": 18.0,
    "2853": 18.0,
    # Chapter 29: Organic chemicals – 18%
    "2901": 18.0, "2902": 18.0, "2903": 18.0, "2904": 18.0, "2905": 18.0,
    "2906": 18.0, "2907": 18.0, "2908": 18.0, "2909": 18.0, "2910": 18.0,
    "2911": 18.0, "2912": 18.0, "2913": 18.0, "2914": 18.0, "2915": 18.0,
    "2916": 18.0, "2917": 18.0, "2918": 18.0, "2919": 18.0, "2920": 18.0,
    "2921": 18.0, "2922": 18.0, "2923": 18.0, "2924": 18.0, "2925": 18.0,
    "2926": 18.0, "2927": 18.0, "2928": 18.0, "2929": 18.0, "2930": 18.0,
    "2931": 18.0, "2932": 18.0, "2933": 18.0, "2934": 18.0, "2935": 18.0,
    "2936": 18.0, "2937": 18.0, "2938": 18.0, "2939": 18.0, "2940": 18.0,
    "2941": 18.0, "2942": 18.0,
    # Chapter 30: Pharmaceutical products
    "3001": 12.0, "3002": 5.0,  "3003": 12.0, "3004": 12.0, "3005": 12.0,
    "3006": 12.0,
    # Chapter 31: Fertilisers – 5%
    "3101": 5.0,  "3102": 5.0,  "3103": 5.0,  "3104": 5.0,  "3105": 5.0,
    # Chapter 32: Tanning/dyeing extracts – 18%
    "3201": 18.0, "3202": 18.0, "3203": 18.0, "3204": 18.0, "3205": 18.0,
    "3206": 18.0, "3207": 18.0, "3208": 18.0, "3209": 18.0, "3210": 18.0,
    "3211": 18.0, "3212": 18.0, "3213": 18.0, "3214": 18.0, "3215": 18.0,
    # Chapter 33: Essential oils/cosmetics
    "3301": 18.0, "3302": 18.0, "3303": 28.0, "3304": 28.0, "3305": 18.0,
    "3306": 18.0, "3307": 18.0,
    # Chapter 34: Soap/waxes – 18% or 28%
    "3401": 18.0, "3402": 18.0, "3403": 18.0, "3404": 18.0, "3405": 18.0,
    "3406": 28.0, "3407": 18.0,
    # Chapter 35: Albuminoidal substances – 18%
    "3501": 18.0, "3502": 18.0, "3503": 12.0, "3504": 18.0, "3505": 18.0,
    "3506": 18.0, "3507": 18.0,
    # Chapter 36: Explosives/matches – 18%
    "3601": 18.0, "3602": 18.0, "3603": 18.0, "3604": 18.0, "3605": 18.0,
    "3606": 18.0,
    # Chapter 37: Photographic goods – 18%
    "3701": 18.0, "3702": 18.0, "3703": 18.0, "3704": 18.0, "3705": 18.0,
    "3706": 18.0, "3707": 18.0,
    # Chapter 38: Miscellaneous chemical products – 18%
    "3801": 18.0, "3802": 18.0, "3803": 18.0, "3804": 18.0, "3805": 18.0,
    "3806": 18.0, "3807": 18.0, "3808": 18.0, "3809": 18.0, "3810": 18.0,
    "3811": 18.0, "3812": 18.0, "3813": 18.0, "3814": 18.0, "3815": 18.0,
    "3816": 18.0, "3817": 18.0, "3818": 18.0, "3819": 18.0, "3820": 18.0,
    "3821": 18.0, "3822": 18.0, "3823": 18.0, "3824": 18.0, "3825": 18.0,
    "3826": 18.0,
    # Chapter 84: Nuclear reactors/boilers/machinery – 18% (earth-moving: 12%)
    "8413": 18.0, "8426": 18.0, "8427": 18.0, "8428": 18.0,
    "8429": 12.0,  # Earth-moving machinery
    "8430": 12.0,  # Other earth-moving machinery
    "8431": 18.0, "8471": 18.0, "8474": 18.0, "8479": 18.0, "8483": 18.0,
    # Chapter 85: Electrical machinery – 18% (solar: 5%)
    "8501": 18.0, "8502": 18.0, "8503": 18.0, "8504": 18.0, "8505": 18.0,
    "8506": 18.0, "8507": 18.0, "8508": 18.0, "8509": 18.0, "8510": 18.0,
    "8511": 18.0, "8512": 18.0, "8513": 18.0, "8514": 18.0, "8515": 18.0,
    "8516": 18.0, "8517": 18.0, "8518": 18.0, "8519": 18.0, "8521": 18.0,
    "8522": 18.0, "8523": 18.0, "8525": 18.0, "8526": 18.0, "8527": 18.0,
    "8528": 18.0, "8529": 18.0, "8530": 18.0, "8531": 18.0, "8532": 18.0,
    "8533": 18.0, "8534": 18.0, "8535": 18.0, "8536": 18.0, "8537": 18.0,
    "8538": 18.0, "8539": 12.0, # LED lights 12%
    "8540": 18.0, "8541": 18.0, "8542": 18.0, "8543": 18.0, "8544": 18.0,
    "8545": 18.0, "8546": 18.0, "8547": 18.0, "8548": 18.0,
    # Chapter 87: Vehicles – 28% but 8705 (special purpose vehicles): 28%
    "8705": 28.0,
    # Chapter 90: Optical/measuring instruments – 18% (medical: 12%)
    "9001": 18.0, "9002": 18.0, "9003": 18.0, "9004": 18.0, "9005": 18.0,
    "9006": 18.0, "9007": 18.0, "9008": 18.0, "9010": 18.0, "9011": 18.0,
    "9012": 18.0, "9013": 18.0, "9014": 18.0, "9015": 18.0, "9016": 18.0,
    "9017": 18.0,
    "9018": 12.0,  # Medical/surgical instruments
    "9019": 12.0,  # Mechano-therapy / massage apparatus
    "9020": 12.0,  # Breathing appliances / gas masks
    "9021": 12.0,  # Orthopaedic appliances
    "9022": 12.0,  # X-ray apparatus (medical)
    "9023": 18.0, "9024": 18.0, "9025": 18.0, "9026": 18.0, "9027": 18.0,
    "9028": 18.0, "9029": 18.0, "9030": 18.0, "9031": 18.0,
}


def get_gst_rate(hsn_code):
    """Resolve GST rate for a given HSN code using specific-first, then chapter fallback."""
    if not hsn_code:
        return 18.0  # Default fallback

    hsn = str(hsn_code).strip()

    # Try 8-digit exact match first
    if hsn in SPECIFIC_HSN_RATES:
        return SPECIFIC_HSN_RATES[hsn]

    # Try 6-digit prefix
    if len(hsn) >= 6 and hsn[:6] in SPECIFIC_HSN_RATES:
        return SPECIFIC_HSN_RATES[hsn[:6]]

    # Try 4-digit chapter
    chapter = hsn[:4]
    if chapter in CHAPTER_RATES:
        return CHAPTER_RATES[chapter]

    # Last resort: 2-digit section
    section = hsn[:2]
    section_defaults = {
        "28": 18.0, "29": 18.0, "30": 12.0, "31": 5.0,
        "32": 18.0, "33": 18.0, "34": 18.0, "35": 18.0,
        "36": 18.0, "37": 18.0, "38": 18.0,
        "84": 18.0, "85": 18.0, "87": 28.0, "90": 18.0,
    }
    return section_defaults.get(section, 18.0)


@frappe.whitelist()
def populate_gst_from_hsn():
    """
    Fetches all Equipment records, determines GST rate from HSN code
    using the official Indian GST schedule, and updates gst_percentage in the DB.
    Returns a summary dict.
    """
    frappe.only_for("System Manager")

    equipment_list = frappe.db.get_all(
        "Equipment",
        fields=["name", "equipment_name", "hsn_code", "gst_percentage"],
        order_by="name asc"
    )

    updated = []
    skipped = []
    no_hsn = []

    for eq in equipment_list:
        if not eq.hsn_code:
            no_hsn.append(eq.name)
            continue

        new_rate = get_gst_rate(eq.hsn_code)

        if float(eq.gst_percentage or 0) == new_rate:
            skipped.append(eq.name)
            continue

        frappe.db.set_value(
            "Equipment",
            eq.name,
            "gst_percentage",
            new_rate,
            update_modified=False
        )
        updated.append({
            "name": eq.name,
            "equipment_name": eq.equipment_name,
            "hsn_code": eq.hsn_code,
            "old_rate": float(eq.gst_percentage or 0),
            "new_rate": new_rate
        })

    frappe.db.commit()

    return {
        "total": len(equipment_list),
        "updated": len(updated),
        "skipped_already_correct": len(skipped),
        "no_hsn": len(no_hsn),
        "sample_updates": updated[:20]  # Show first 20 for review
    }
