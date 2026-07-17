import frappe
from sarveksha_vendor.setup.install import after_install

def run():
	print("Running Demo Setup for Sarveksha Vendor Payment Tracking...")
	
	# Execute standard install procedures (create companies, banks, terms, taxes, dummy records, dashboard cards)
	after_install()
	
	# Ensure the workspace is correctly set up with the correct roles
	setup_workspace_roles()
	
	frappe.db.commit()
	print("Demo Setup finished successfully.")


def setup_workspace_roles():
	workspace_name = "Vendor Payment Tracking"
	if frappe.db.exists("Workspace", workspace_name):
		try:
			ws = frappe.get_doc("Workspace", workspace_name)
			ws.set("roles", [])
			ws.append("roles", {"role": "System Manager"})
			ws.append("roles", {"role": "Finance Manager"})
			ws.append("roles", {"role": "Purchase Manager"})
			ws.flags.ignore_permissions = True
			ws.save()
			print(f"Workspace roles successfully configured for '{workspace_name}'.")
		except Exception as e:
			print(f"Could not configure workspace roles: {e}")
	else:
		print(f"Workspace '{workspace_name}' does not exist yet. Please run bench migrate first.")

if __name__ == "__main__":
	# If run directly as a script under frappe site context
	run()
