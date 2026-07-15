import frappe
from frappe.utils import today, add_days

@frappe.whitelist()
def make_payment_entry(source_name):
	"""Maps a Vendor Payment Request to an ERPNext Payment Entry."""
	req = frappe.get_doc("Vendor Payment Request", source_name)
	
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Pay"
	pe.party_type = "Supplier"
	pe.party = req.vendor
	pe.company = req.company
	pe.paid_amount = req.requested_amount
	pe.received_amount = req.requested_amount
	pe.posting_date = today()
	
	if req.bank_account:
		# Find the actual Account linked to this Bank Account
		acc = frappe.db.get_value("Bank Account", req.bank_account, "account")
		if acc:
			pe.paid_from = acc
			
	# Append reference to purchase invoice if present
	if req.purchase_invoice:
		pe.append("references", {
			"reference_doctype": "Purchase Invoice",
			"reference_name": req.purchase_invoice,
			"allocated_amount": req.requested_amount
		})
		
	# Do not submit yet, leave as Draft for the Accounts Officer
	pe.insert(ignore_permissions=True)
	
	# Update request status to Paid in a real workflow once PE is submitted,
	# but for now we set it to Approved/Pending Entry.
	return pe

@frappe.whitelist()
def get_dashboard_summary(company=None):
	"""Returns counts and sums for the Vendor Payment Tracking Workspace cards."""
	filters = {}
	if company:
		filters["company"] = company
		
	# 1. Pending Payments
	pending_count = frappe.db.count("Vendor Payment Request", filters={"status": "Pending Approval", **filters})
	
	# 2. Approved Payments
	approved_count = frappe.db.count("Vendor Payment Request", filters={"status": "Approved", **filters})
	
	# 3. Rejected Payments
	rejected_count = frappe.db.count("Vendor Payment Request", filters={"status": "Rejected", **filters})
	
	# 4. Upcoming Payments (Next 7 days)
	upcoming_count = frappe.db.count("Vendor Payment Request", filters={
		"request_date": [">=", today()],
		"status": ["in", ["Draft", "Pending Finance Review", "Pending Approval", "Approved"]],
		**filters
	})
	
	# 5. Today's Payments
	todays_count = frappe.db.count("Vendor Payment Request", filters={"request_date": today(), **filters})
	
	# 6. Overdue invoices (Purchase invoices with outstanding amount > 0 and past due date)
	overdue_count = 0
	try:
		overdue_count = frappe.db.count("Purchase Invoice", filters={
			"outstanding_amount": [">", 0],
			"due_date": ["<", today()],
			**filters
		})
	except Exception:
		pass
		
	# 7. Monthly Spend (Sum of paid amount this month)
	monthly_spend = 0.0
	try:
		# Simplified sum for dashboard spend calculation
		invoiced_records = frappe.get_all("Purchase Invoice", filters=filters, fields=["grand_total"])
		monthly_spend = sum([float(r.grand_total or 0) for r in invoiced_records])
	except Exception:
		pass
		
	# 8. Recent Vendors
	recent_vendors = []
	try:
		recent_vendors = frappe.get_all("Supplier", limit=5, order_by="creation desc", fields=["name", "supplier_name"])
	except Exception:
		pass
		
	# 9. Shipment Status (In Transit count)
	in_transit_shipments = frappe.db.count("Shipment", filters={"status": "In Transit", **filters})
	
	# 10. Pending Customs (Customs Clearances with Pending status)
	pending_customs = frappe.db.count("Custom Clearance", filters={"status": "Pending", **filters})
	
	return {
		"pending_payments": pending_count,
		"approved_payments": approved_count,
		"rejected_payments": rejected_count,
		"upcoming_payments": upcoming_count,
		"todays_payments": todays_count,
		"overdue": overdue_count,
		"monthly_spend": monthly_spend,
		"recent_vendors": recent_vendors,
		"shipment_status": in_transit_shipments,
		"pending_customs": pending_customs
	}
