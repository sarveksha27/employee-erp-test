# -*- coding: utf-8 -*-
import frappe

def seed_ports():
    ports = [
        {"port_name": "Mundra", "country": "India", "port_code": "INMUN", "is_active": 1},
        {"port_name": "JNPT", "country": "India", "port_code": "INJNP", "is_active": 1},
        {"port_name": "Mumbai", "country": "India", "port_code": "INBOM", "is_active": 1},
        {"port_name": "Conakry", "country": "Guinea", "port_code": "GNCKY", "is_active": 1},
        {"port_name": "Durban", "country": "South Africa", "port_code": "ZADUR", "is_active": 1},
        {"port_name": "Freetown", "country": "Sierra Leone", "port_code": "SLFNA", "is_active": 1},
        {"port_name": "Douala", "country": "Cameroon", "port_code": "CMDLA", "is_active": 1}
    ]
    for p in ports:
        if not frappe.db.exists("Port", p["port_name"]):
            doc = frappe.new_doc("Port")
            doc.update(p)
            doc.insert(ignore_permissions=True)
            print(f"Seeded Port: {p['port_name']}")

def seed_users():
    users = [
        {
            "email": "po_generator@sarveksha.com",
            "first_name": "PO Generator",
            "roles": ["Purchase User", "Accounts User"]
        },
        {
            "email": "po_verifier@sarveksha.com",
            "first_name": "PO Verifier",
            "roles": ["Purchase User", "Accounts User"]
        },
        {
            "email": "po_approver@sarveksha.com",
            "first_name": "PO Approver",
            "roles": ["Purchase Manager", "Accounts Manager", "System Manager"]
        },
        {
            "email": "admin@sarveksha.com",
            "first_name": "Admin",
            "roles": ["System Manager"]
        },
        {
            "email": "procurement_manager@sarveksha.com",
            "first_name": "Procurement Manager",
            "roles": ["Purchase Manager", "Accounts Manager", "System Manager"]
        }
    ]
    for u in users:
        if frappe.db.exists("User", u["email"]):
            doc = frappe.get_doc("User", u["email"])
        else:
            doc = frappe.new_doc("User")
            doc.email = u["email"]
            doc.send_welcome_email = 0

        doc.first_name = u["first_name"]
        doc.save(ignore_permissions=True)
        from frappe.utils.password import update_password
        update_password(u["email"], "123")
        
        # Remove old roles and add targeted ones
        doc.remove_roles(*[r.role for r in doc.roles])
        for role in u["roles"]:
            doc.add_roles(role)
        print(f"Seeded/Updated User: {u['email']}")

def seed_terms_and_conditions():
    terms_list = [
        {
            "title": "Standard Export PO Terms",
            "terms": """
<h3>Terms and Conditions: Standard Export</h3>
<ol>
  <li><strong>Payment:</strong> 30% advance, 70% balance payable against shipping documents.</li>
  <li><strong>Inspection:</strong> Inspection to be carried out by pre-shipment agency (e.g., SGS/BV) at supplier's works before dispatch.</li>
  <li><strong>Liquidated Damages (LD):</strong> Penalty of 0.5% per week of delay up to a maximum of 5% of the PO value.</li>
  <li><strong>Warranty:</strong> 12 months from the date of commissioning or 18 months from shipment, whichever is earlier.</li>
  <li><strong>ISPM-15:</strong> All wooden packing material must be heat treated or fumigated and marked in accordance with ISPM-15 standards.</li>
  <li><strong>Force Majeure:</strong> Neither party shall be liable for delay or failure of performance due to acts of God, war, riot, or government restrictions.</li>
  <li><strong>Governing Law:</strong> This Purchase Order shall be governed by and construed in accordance with the laws of India.</li>
</ol>
"""
        },
        {
            "title": "Export to Africa Terms",
            "terms": """
<h3>Terms and Conditions: Export to Africa</h3>
<ol>
  <li><strong>Shipping & Logistics:</strong> Goods to be shipped on CIF basis to the designated African port of discharge.</li>
  <li><strong>Compliance:</strong> Supplier must provide pre-shipment inspection certificate, certificate of conformity, and clean report of findings as required by the destination country's customs.</li>
  <li><strong>Documentation:</strong> Complete set of original shipping documents (Bill of Lading, Invoice, Packing List, Certificate of Origin) to be couriered to the buyer's logistics agent within 7 days of sailing.</li>
</ol>
"""
        },
        {
            "title": "Domestic India Terms",
            "terms": """
<h3>Terms and Conditions: Domestic India</h3>
<ol>
  <li><strong>Tax Compliance:</strong> GST rate as applicable. Tax invoice must conform to GST rules, and Supplier must upload the invoice to the GSTN portal in time for Buyer to claim Input Tax Credit (ITC).</li>
  <li><strong>Payment:</strong> Payment terms as agreed, subject to receipt of conforming materials and matching ITC reflection in GSTR-2B.</li>
  <li><strong>Dispute Jurisdiction:</strong> Any disputes arising under this transaction shall be subject to the exclusive jurisdiction of the courts of Mumbai, India.</li>
</ol>
"""
        },
        {
            "title": "LUT Certificate Terms",
            "terms": """
<h3>Terms and Conditions: LUT Certificate Override</h3>
<ol>
  <li><strong>LUT Applicability:</strong> Goods are being purchased for export under Letter of Undertaking (LUT) / Bond scheme.</li>
  <li><strong>Tax Rate:</strong> Concessional IGST at 0.1% (or CGST 0.05% + SGST 0.05%) applies as per Notification No. 40/2017-Central Tax (Rate) / 41/2017-Integrated Tax (Rate) for merchant exporters.</li>
  <li><strong>Exporter Undertaking:</strong> The exporter (buyer) undertakes to export the goods within 90 days from the date of issue of the tax invoice by the supplier.</li>
</ol>
"""
        }
    ]

    for t in terms_list:
        if not frappe.db.exists("Terms and Conditions", t["title"]):
            doc = frappe.new_doc("Terms and Conditions")
            doc.title = t["title"]
            doc.terms = t["terms"]
            doc.buying = 1
            doc.selling = 0
            doc.insert(ignore_permissions=True)
            print(f"Seeded Terms & Conditions: {t['title']}")

def main():
    seed_ports()
    seed_users()
    seed_terms_and_conditions()
    frappe.db.commit()

def run_tests():
    print("=========================================")
    print("RUNNING PO ENHANCEMENT VERIFICATION TESTS")
    print("=========================================")

    # 1. Verify Ports
    expected_ports = ["Mundra", "JNPT", "Mumbai", "Conakry", "Durban", "Freetown", "Douala"]
    missing_ports = []
    for port in expected_ports:
        if not frappe.db.exists("Port", port):
            missing_ports.append(port)
    
    if missing_ports:
        print(f"FAIL: Missing ports: {missing_ports}")
    else:
        print("PASS: All expected ports seeded successfully.")

    # 2. Verify Users
    expected_users = [
        "po_generator@sarveksha.com",
        "po_verifier@sarveksha.com",
        "po_approver@sarveksha.com",
        "admin@sarveksha.com",
        "procurement_manager@sarveksha.com"
    ]
    missing_users = []
    for user in expected_users:
        if not frappe.db.exists("User", user):
            missing_users.append(user)
    
    if missing_users:
        print(f"FAIL: Missing users: {missing_users}")
    else:
        print("PASS: All expected workflow users exist in database.")

    # 3. Verify DocType Fields
    meta = frappe.get_meta("Vendor Purchase Order")
    
    # Check port field
    port_field = meta.get_field("port")
    if not port_field:
        print("FAIL: Field 'port' not found on Vendor Purchase Order")
    elif port_field.fieldtype != "Select":
        print(f"FAIL: Field 'port' fieldtype={port_field.fieldtype} (expected Select)")
    else:
        print("PASS: 'port' field successfully converted to Select dropdown.")

    # Check shipment_type field
    st_field = meta.get_field("shipment_type")
    if not st_field:
        print("FAIL: Field 'shipment_type' not found on Vendor Purchase Order")
    elif st_field.fieldtype != "Select":
        print(f"FAIL: Field 'shipment_type' fieldtype={st_field.fieldtype} (expected Select)")
    else:
        print("PASS: 'shipment_type' field successfully converted to Select.")

    # Check company gstin/pan
    gstin_field = meta.get_field("company_gstin")
    pan_field = meta.get_field("company_pan")
    if not gstin_field or not pan_field:
        print(f"FAIL: 'company_gstin'={bool(gstin_field)}, 'company_pan'={bool(pan_field)} (expected both to exist)")
    else:
        print("PASS: Read-only 'company_gstin' and 'company_pan' fields added to Vendor Purchase Order.")

    # Check terms fields
    st_field = meta.get_field("standard_terms")
    if not st_field:
        print("FAIL: Field 'standard_terms' not found on Vendor Purchase Order")
    elif st_field.fieldtype != "Link":
        print(f"FAIL: Field 'standard_terms' fieldtype={st_field.fieldtype} (expected Link)")
    else:
        print("PASS: 'standard_terms' field added to Vendor Purchase Order.")

    ct_field = meta.get_field("custom_terms")
    if not ct_field:
        print("FAIL: Field 'custom_terms' not found on Vendor Purchase Order")
    elif ct_field.fieldtype != "Text Editor":
        print(f"FAIL: Field 'custom_terms' fieldtype={ct_field.fieldtype} (expected Text Editor)")
    else:
        print("PASS: 'custom_terms' field added to Vendor Purchase Order.")

    lut_field = meta.get_field("is_lut_applicable")
    if not lut_field:
        print("FAIL: Field 'is_lut_applicable' not found on Vendor Purchase Order")
    elif lut_field.fieldtype != "Check":
        print(f"FAIL: Field 'is_lut_applicable' fieldtype={lut_field.fieldtype} (expected Check)")
    else:
        print("PASS: 'is_lut_applicable' field added to Vendor Purchase Order.")

    print("=========================================")
