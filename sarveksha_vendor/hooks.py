app_name = "sarveksha_vendor"
app_title = "Sarveksha Vendor"
app_publisher = "Sarveksha"
app_description = "Vendor Payment Tracking module for a multi-company organization."
app_email = "admin@sarveksha.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be imported and tested during tests
# before_install = "sarveksha_vendor.utils.before_install"
after_install = "sarveksha_vendor.setup.install.after_install"

# Integration Cleanup
# -------------------
# before_uninstall = "sarveksha_vendor.utils.before_uninstall"
# after_uninstall = "sarveksha_vendor.utils.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sarveksha_vendor.notifications.get_notification_config"

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sarveksha_vendor.tasks.all"
# 	],
# 	"daily": [
# 		"sarveksha_vendor.tasks.daily"
# 	],
# 	"hourly": [
# 		"sarveksha_vendor.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sarveksha_vendor.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sarveksha_vendor.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sarveksha_vendor.install.before_tests"

# Overriding Methods
# ------------------
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sarveksha_vendor.event.get_events"
# }
#
# each overriding class extension should be subclassed from the parent class
# override_doctype_class = {
# 	"ToDo": "sarveksha_vendor.todo.CustomToDo"
# }

# Document Flow Control
# ---------------------

# accept_letter_of_credit = "sarveksha_vendor.utils.accept_letter_of_credit"

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and Authorization
# --------------------------------

# auth_hooks = [
# 	"sarveksha_vendor.auth.validate"
# ]

# Fixtures
# --------
# Standard fixtures to export configurations like custom workspaces, roles, etc.
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["Organization Admin", "Finance Manager", "Purchase Manager", "Accounts Officer"]]]},
    {"dt": "Workspace", "filters": [["name", "=", "Vendor Payment Tracking"]]}
]
