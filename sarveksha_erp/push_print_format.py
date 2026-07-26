import frappe

def execute():
    with open(frappe.get_app_path("sarveksha_erp", "vendor_management", "print_format",
              "vendor_purchase_order_format", "vendor_purchase_order_format.html"), "r") as f:
        html_content = f.read()

    pf = frappe.get_doc("Print Format", "Vendor Purchase Order Format")
    pf.html = html_content
    pf.custom_format = 1
    pf.save(ignore_permissions=True)
    frappe.db.commit()
    print("Print format HTML pushed to database successfully!")
    print(f"HTML length: {len(html_content)} chars")
