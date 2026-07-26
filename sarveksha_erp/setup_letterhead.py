import frappe

def execute():
    # Create/update the Sarveksha Letter Head
    if frappe.db.exists("Letter Head", "Sarveksha Realty & Inframine LLP"):
        lh = frappe.get_doc("Letter Head", "Sarveksha Realty & Inframine LLP")
    else:
        lh = frappe.new_doc("Letter Head")
        lh.letter_head_name = "Sarveksha Realty & Inframine LLP"

    lh.is_default = 1
    lh.source = "Image"
    lh.content = '''<div style="margin:0; padding:0;">
        <img src="/files/sarveksha-header-logo.png"
             style="width:100%; display:block; max-height:130px; object-fit:cover;"
             alt="Sarveksha Realty &amp; Inframine LLP">
    </div>'''
    lh.footer = '''<div style="text-align:center; font-size:9px; color:#666; border-top:1px solid #ccc; padding-top:4px; margin-top:4px;">
        Sarveksha Realty &amp; Inframine LLP | Sparsh 303, Plot 101-102, Sec 44 Seawoods, Navi Mumbai, 400706 |
        Phone: (+91) 9769008220 | Email: sudheerg@sarveksha.com
    </div>'''

    lh.save(ignore_permissions=True)
    print(f"Letter Head saved: {lh.name}")

    # Assign the letter head to the print format
    pf = frappe.get_doc("Print Format", "Vendor Purchase Order Format")
    pf.letter_head = "Sarveksha Realty & Inframine LLP"
    pf.save(ignore_permissions=True)
    print(f"Print Format updated with letter head: {pf.letter_head}")

    frappe.db.commit()
    print("Done!")
