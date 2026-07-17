app_name = "sarveksha_vendor"
app_title = "Sarveksha Vendor"
app_publisher = "Sarveksha Team"
app_description = "Vendor Payment Tracking module."
app_email = "info@sarveksha.com"
app_license = "mit"

# Installation
# ------------
after_install = "sarveksha_vendor.setup.install.after_install"

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
	"Vendor Payment Request": {
		"validate": "sarveksha_vendor.sarveksha_vendor.doctype.vendor_payment_request.vendor_payment_request.validate_payment_request",
		"on_update": "sarveksha_vendor.sarveksha_vendor.doctype.vendor_payment_request.vendor_payment_request.log_payment_request"
	},
	"Vendor Contract": {
		"on_update": "sarveksha_vendor.sarveksha_vendor.doctype.vendor_contract.vendor_contract.log_contract_change"
	}
}

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True
