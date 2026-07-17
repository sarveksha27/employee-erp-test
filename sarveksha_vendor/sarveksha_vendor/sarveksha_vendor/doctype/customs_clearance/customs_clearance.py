import frappe
from frappe.model.document import Document

class CustomsClearance(Document):
	def on_update(self):
		if self.shipment:
			try:
				ship = frappe.get_doc("Shipment", self.shipment)
				if self.status == "Cleared":
					ship.status = "In Transit"
				elif self.status == "Rejected":
					ship.status = "Customs Hold"
				ship.save(ignore_permissions=True)
			except Exception:
				pass
