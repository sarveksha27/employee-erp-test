app_name = "sarveksha_erp"
app_title = "Sarveksha ERP"
app_publisher = "Sarveksha Group"
app_description = "Modular Procurement & Equipment ERP for Sarveksha Group"
app_email = "erp@sarveksha.com"
app_license = "mit"

# Installation Hooks
# ------------
after_install = "sarveksha_erp.setup.install.after_install"

# Export Python type annotations
export_python_type_annotations = True

# Modular Desk Configuration
has_website_permission = "sarveksha_erp.api.has_website_permission"

# Document Events
doc_events = {
	"Sarveksha Purchase Order": {
		"validate": "sarveksha_erp.sarveksha_erp.doctype.sarveksha_purchase_order.sarveksha_purchase_order.validate_po"
	}
}
