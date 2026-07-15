import frappe
import random
from frappe.utils import add_days, today

@frappe.whitelist()
def seed_bootstrap_data():
	"""Automatically generates standard initial dataset for the Vendor Tracking system."""
	# 1. Create Suppliers (Vendors)
	suppliers = create_initial_suppliers(20)
	
	# Get list of active companies
	companies = frappe.get_all("Company", pluck="name")
	if not companies:
		companies = ["Sarveksha Realty and Inframine LLP"]
		# Make sure at least one company exists
		if not frappe.db.exists("Company", companies[0]):
			c = frappe.new_doc("Company")
			c.company_name = companies[0]
			c.default_currency = "INR"
			c.country = "India"
			c.insert(ignore_permissions=True)

	# Ensure standard item exists
	item_code = create_standard_item()

	# 2. Create 40 Purchase Orders
	pos = create_initial_purchase_orders(40, suppliers, companies, item_code)

	# 3. Create 40 Purchase Invoices
	invoices = create_initial_purchase_invoices(40, suppliers, companies, pos, item_code)

	# 4. Create 20 Shipments
	shipments = create_initial_shipments(20, companies, pos, item_code)

	# 5. Create 10 Customs Records
	customs = create_initial_customs_clearance(10, companies, shipments, suppliers)

	# 6. Create 15 Equipment Records
	equipment = create_initial_equipment(15, companies, pos, invoices)

	# 7. Create 10 Payment Requests
	requests = create_initial_payment_requests(10, companies, suppliers, invoices)

	return {
		"suppliers": len(suppliers),
		"purchase_orders": len(pos),
		"purchase_invoices": len(invoices),
		"shipments": len(shipments),
		"customs_records": len(customs),
		"equipment_records": len(equipment),
		"payment_requests": len(requests)
	}

def create_initial_suppliers(count):
	suppliers = []
	supplier_names = [
		"Acme Industrial", "Apex Logistics", "Bharti Steel", "Carthage Mining",
		"Delta Engineering", "Emirates Trading", "Fuji Machinery", "Global Spares",
		"Hassan Imports", "Indo-Gulf Corp", "Jupiter Systems", "Kalahari Heavy Equip",
		"Logitech Builders", "Metro Cement", "Nordic Power", "Oasis Trading",
		"Pacific Oceanics", "Quality Casting", "Reliable Tech", "Summit Materials"
	]
	for i in range(count):
		name = supplier_names[i] if i < len(supplier_names) else f"Supplier {i+1}"
		if not frappe.db.exists("Supplier", name):
			try:
				supplier = frappe.new_doc("Supplier")
				supplier.supplier_name = name
				supplier.supplier_group = "All Supplier Groups"
				supplier.insert(ignore_permissions=True)
				suppliers.append(supplier.name)
			except Exception:
				pass
		else:
			suppliers.append(name)
	return suppliers

def create_standard_item():
	item_code = "SARV-MAT-001"
	if not frappe.db.exists("Item", item_code):
		try:
			# Standard item requires item group and UOM
			item_group = frappe.get_all("Item Group", limit=1, pluck="name")
			ig = item_group[0] if item_group else "All Item Groups"
			if not frappe.db.exists("Item Group", ig):
				d_ig = frappe.new_doc("Item Group")
				d_ig.item_group_name = ig
				d_ig.insert(ignore_permissions=True)

			uom = frappe.get_all("UOM", limit=1, pluck="name")
			u = uom[0] if uom else "Nos"
			if not frappe.db.exists("UOM", u):
				d_u = frappe.new_doc("UOM")
				d_u.uom_name = u
				d_u.insert(ignore_permissions=True)

			item = frappe.new_doc("Item")
			item.item_code = item_code
			item.item_name = "Sarveksha Standard Material"
			item.item_group = ig
			item.stock_uom = u
			item.is_stock_item = 0 # Service/non-stock to avoid complex warehouse/valuation validations
			item.insert(ignore_permissions=True)
		except Exception:
			pass
	return item_code

def create_initial_purchase_orders(count, suppliers, companies, item_code):
	pos = []
	for _ in range(count):
		company = random.choice(companies)
		supplier = random.choice(suppliers)
		
		# Set currency based on company
		currency = frappe.db.get_value("Company", company, "default_currency") or "INR"
		
		try:
			po = frappe.new_doc("Purchase Order")
			po.company = company
			po.supplier = supplier
			po.transaction_date = add_days(today(), -random.randint(10, 60))
			po.schedule_date = add_days(po.transaction_date, 15)
			po.currency = currency
			po.append("items", {
				"item_code": item_code,
				"qty": random.randint(5, 50),
				"rate": random.randint(100, 5000),
				"uom": "Nos"
			})
			po.flags.ignore_mandatory = True
			po.insert(ignore_permissions=True)
			po.submit()
			pos.append(po.name)
		except Exception:
			# Fallback creation for standard validation bypass
			try:
				po = frappe.new_doc("Purchase Order")
				po.company = company
				po.supplier = supplier
				po.transaction_date = today()
				po.flags.ignore_mandatory = True
				po.insert(ignore_permissions=True)
				pos.append(po.name)
			except Exception:
				pass
	return pos

def create_initial_purchase_invoices(count, suppliers, companies, pos, item_code):
	invoices = []
	for _ in range(count):
		company = random.choice(companies)
		supplier = random.choice(suppliers)
		po = random.choice(pos) if pos else None
		
		currency = frappe.db.get_value("Company", company, "default_currency") or "INR"
		
		try:
			pi = frappe.new_doc("Purchase Invoice")
			pi.company = company
			pi.supplier = supplier
			pi.posting_date = add_days(today(), -random.randint(5, 45))
			pi.currency = currency
			pi.append("items", {
				"item_code": item_code,
				"qty": random.randint(5, 50),
				"rate": random.randint(100, 5000),
				"uom": "Nos"
			})
			if po:
				pi.items[0].purchase_order = po
			pi.flags.ignore_mandatory = True
			pi.insert(ignore_permissions=True)
			pi.submit()
			invoices.append(pi.name)
		except Exception:
			# Fallback creation
			try:
				pi = frappe.new_doc("Purchase Invoice")
				pi.company = company
				pi.supplier = supplier
				pi.posting_date = today()
				pi.flags.ignore_mandatory = True
				pi.insert(ignore_permissions=True)
				invoices.append(pi.name)
			except Exception:
				pass
	return invoices

def create_initial_shipments(count, companies, pos, item_code):
	shipments = []
	countries = frappe.get_all("Country", pluck="name", limit=10)
	if not countries:
		countries = ["India", "Guinea", "Cameroon", "Botswana", "Sierra Leone", "United Arab Emirates"]
		for c_name in countries:
			if not frappe.db.exists("Country", c_name):
				c = frappe.new_doc("Country")
				c.country_name = c_name
				c.insert(ignore_permissions=True)
				
	statuses = ["In Transit", "Customs Clearance", "Delivered", "Delayed"]
	carriers = ["DHL Express", "FedEx Cargo", "Maersk Line", "MSC Shipping", "Emirates SkyCargo"]

	for i in range(count):
		company = random.choice(companies)
		po = random.choice(pos) if pos else ""
		
		ship = frappe.new_doc("Shipment")
		ship.shipment_date = add_days(today(), -random.randint(5, 30))
		ship.estimated_delivery = add_days(ship.shipment_date, 10)
		if i % 3 == 0:
			ship.actual_delivery = add_days(ship.shipment_date, 9)
			ship.status = "Delivered"
		else:
			ship.status = random.choice(statuses)
		ship.origin_country = random.choice(countries)
		ship.destination_country = random.choice(countries)
		ship.carrier_name = random.choice(carriers)
		ship.tracking_number = f"TRK{random.randint(100000, 999999)}"
		ship.company = company
		
		if po:
			ship.append("shipment_items", {
				"purchase_order": po,
				"item": item_code,
				"qty": random.randint(10, 100),
				"rate": random.randint(50, 1000),
				"amount": random.randint(500, 100000)
			})
		ship.insert(ignore_permissions=True)
		shipments.append(ship.name)
	return shipments

def create_initial_customs_clearance(count, companies, shipments, suppliers):
	customs = []
	statuses = ["Pending", "Cleared", "Rejected"]
	for i in range(count):
		company = random.choice(companies)
		shipment = shipments[i] if i < len(shipments) else random.choice(shipments)
		broker = random.choice(suppliers)
		
		cc = frappe.new_doc("Custom Clearance")
		cc.shipment = shipment
		cc.customs_broker = broker
		cc.bill_of_lading = f"BOL{random.randint(100000, 999999)}"
		cc.customs_duty_amount = random.randint(500, 10000)
		cc.clearance_date = add_days(today(), random.randint(-5, 5))
		cc.status = random.choice(statuses)
		cc.company = company
		cc.clearance_notes = "Standard customs review."
		cc.insert(ignore_permissions=True)
		customs.append(cc.name)
	return customs

def create_initial_equipment(count, companies, pos, invoices):
	equipment = []
	names = ["Excavator", "Generator 500kVA", "Crusher", "Drill Rig", "Dump Truck", "Conveyor Belt", "Substation Transformer"]
	statuses = ["In Transit", "Installed", "Under Maintenance", "Retired"]
	for i in range(count):
		company = random.choice(companies)
		po = pos[i] if i < len(pos) else random.choice(pos)
		inv = invoices[i] if i < len(invoices) else random.choice(invoices)
		name = f"{random.choice(names)} {random.randint(1, 100)}"
		
		eq = frappe.new_doc("Equipment")
		eq.equipment_name = name
		eq.asset_code = f"AST-{random.randint(1000, 9999)}"
		eq.serial_no = f"SN-{random.randint(100000, 999999)}"
		eq.company = company
		eq.purchase_order = po
		eq.purchase_invoice = inv
		eq.installation_date = add_days(today(), -random.randint(10, 100))
		eq.status = random.choice(statuses)
		eq.insert(ignore_permissions=True)
		equipment.append(eq.name)
	return equipment

def create_initial_payment_requests(count, companies, suppliers, invoices):
	requests = []
	statuses = ["Draft", "Pending Finance Review", "Pending Approval", "Approved", "Rejected", "Paid"]
	for i in range(count):
		company = random.choice(companies)
		vendor = random.choice(suppliers)
		inv = invoices[i] if i < len(invoices) else random.choice(invoices)
		
		bank_account = frappe.db.get_value("Bank Account", {"company": company}, "name")
		
		pr = frappe.new_doc("Vendor Payment Request")
		pr.vendor = vendor
		pr.company = company
		pr.purchase_invoice = inv
		if bank_account:
			pr.bank_account = bank_account
		pr.requested_amount = random.randint(1000, 50000)
		pr.request_date = add_days(today(), -random.randint(0, 15))
		pr.status = random.choice(statuses)
		pr.description = "Supplier invoice payment settlement."
		pr.insert(ignore_permissions=True)
		requests.append(pr.name)
	return requests
