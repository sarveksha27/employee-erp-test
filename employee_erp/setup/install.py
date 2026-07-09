import frappe
from frappe.utils import today, add_days

def after_install():
	print("Creating seed data for Employee ERP...")
	create_departments()
	create_designations()
	create_leave_types()
	create_employees()
	create_salary_components()
	create_salary_structures()
	create_holiday_list()
	create_leave_allocations()
	create_attendances()
	print("Seed data creation complete.")


def create_departments():
	departments = [
		{"department_name": "Operations", "is_active": 1},
		{"department_name": "Human Resources", "parent_department": "Operations", "is_active": 1},
		{"department_name": "Engineering", "parent_department": "Operations", "is_active": 1},
		{"department_name": "Marketing", "parent_department": "Operations", "is_active": 1},
		{"department_name": "Sales", "parent_department": "Marketing", "is_active": 1},
		{"department_name": "Finance", "parent_department": "Operations", "is_active": 1},
	]
	
	for dept in departments:
		if not frappe.db.exists("ERP Department", dept.get("department_name")):
			doc = frappe.get_doc({"doctype": "ERP Department", **dept})
			doc.insert(ignore_permissions=True)


def create_designations():
	designations = ["CEO", "CTO", "VP Engineering", "Senior Engineer", "Software Engineer", "HR Manager", "Accountant", "Marketing Lead", "Sales Executive"]
	
	for desig in designations:
		if not frappe.db.exists("ERP Designation", desig):
			doc = frappe.get_doc({
				"doctype": "ERP Designation",
				"designation_name": desig
			})
			doc.insert(ignore_permissions=True)


def create_leave_types():
	leave_types = [
		{"leave_type_name": "Earned Leave", "max_leaves_allowed": 15, "is_carry_forward": 1, "is_paid_leave": 1},
		{"leave_type_name": "Casual Leave", "max_leaves_allowed": 12, "is_carry_forward": 0, "is_paid_leave": 1},
		{"leave_type_name": "Sick Leave", "max_leaves_allowed": 10, "is_carry_forward": 0, "is_paid_leave": 1},
		{"leave_type_name": "Leave Without Pay", "max_leaves_allowed": 365, "is_carry_forward": 0, "is_paid_leave": 0},
	]
	
	for lt in leave_types:
		if not frappe.db.exists("ERP Leave Type", lt.get("leave_type_name")):
			doc = frappe.get_doc({"doctype": "ERP Leave Type", **lt})
			doc.insert(ignore_permissions=True)


def create_employees():
	employees = [
		{"first_name": "John", "last_name": "Doe", "department": "Operations", "designation": "CEO", "gender": "Male", "date_of_birth": "1980-01-01", "date_of_joining": "2020-01-01", "status": "Active", "company_email": "john.doe@example.com"},
		{"first_name": "Jane", "last_name": "Smith", "department": "Engineering", "designation": "CTO", "gender": "Female", "date_of_birth": "1985-05-15", "date_of_joining": "2020-02-01", "status": "Active", "company_email": "jane.smith@example.com", "reports_to_email": "john.doe@example.com"},
		{"first_name": "Alice", "last_name": "Johnson", "department": "Human Resources", "designation": "HR Manager", "gender": "Female", "date_of_birth": "1990-10-20", "date_of_joining": "2021-03-15", "status": "Active", "company_email": "alice.j@example.com", "reports_to_email": "john.doe@example.com"},
		{"first_name": "Bob", "last_name": "Williams", "department": "Engineering", "designation": "Senior Engineer", "gender": "Male", "date_of_birth": "1992-04-10", "date_of_joining": "2021-06-01", "status": "Active", "company_email": "bob.w@example.com", "reports_to_email": "jane.smith@example.com"},
		{"first_name": "Charlie", "last_name": "Brown", "department": "Engineering", "designation": "Software Engineer", "gender": "Male", "date_of_birth": "1995-12-05", "date_of_joining": "2022-01-10", "status": "Active", "company_email": "charlie.b@example.com", "reports_to_email": "bob.w@example.com"},
		{"first_name": "Diana", "last_name": "Prince", "department": "Marketing", "designation": "Marketing Lead", "gender": "Female", "date_of_birth": "1988-08-14", "date_of_joining": "2021-11-01", "status": "Active", "company_email": "diana.p@example.com", "reports_to_email": "john.doe@example.com"},
		{"first_name": "Eve", "last_name": "Davis", "department": "Finance", "designation": "Accountant", "gender": "Female", "date_of_birth": "1991-03-22", "date_of_joining": "2020-05-01", "status": "Active", "company_email": "eve.d@example.com", "reports_to_email": "john.doe@example.com"},
		{"first_name": "Frank", "last_name": "Miller", "department": "Sales", "designation": "Sales Executive", "gender": "Male", "date_of_birth": "1994-07-30", "date_of_joining": "2022-04-15", "status": "Active", "company_email": "frank.m@example.com", "reports_to_email": "diana.p@example.com"},
		{"first_name": "Grace", "last_name": "Hopper", "department": "Engineering", "designation": "Senior Engineer", "gender": "Female", "date_of_birth": "1989-12-09", "date_of_joining": "2021-08-01", "status": "Active", "company_email": "grace.h@example.com", "reports_to_email": "jane.smith@example.com"},
		{"first_name": "Hank", "last_name": "Pym", "department": "Engineering", "designation": "Software Engineer", "gender": "Male", "date_of_birth": "1996-02-28", "date_of_joining": "2023-01-05", "status": "Active", "company_email": "hank.p@example.com", "reports_to_email": "bob.w@example.com"},
	]

	# First pass: create employees without reports_to
	for emp in employees:
		emp_name = f"{emp['first_name']} {emp['last_name']}"
		if not frappe.db.exists("ERP Employee", {"employee_name": emp_name}):
			doc = frappe.get_doc({
				"doctype": "ERP Employee",
				"first_name": emp["first_name"],
				"last_name": emp["last_name"],
				"department": emp["department"],
				"designation": emp["designation"],
				"gender": emp["gender"],
				"date_of_birth": emp["date_of_birth"],
				"date_of_joining": emp["date_of_joining"],
				"status": emp["status"],
				"company_email": emp["company_email"],
			})
			doc.insert(ignore_permissions=True)

	# Second pass: set reports_to
	for emp in employees:
		if "reports_to_email" in emp:
			emp_name = f"{emp['first_name']} {emp['last_name']}"
			emp_doc_name = frappe.db.get_value("ERP Employee", {"employee_name": emp_name}, "name")
			reports_to_doc_name = frappe.db.get_value("ERP Employee", {"company_email": emp["reports_to_email"]}, "name")
			
			if emp_doc_name and reports_to_doc_name:
				doc = frappe.get_doc("ERP Employee", emp_doc_name)
				doc.reports_to = reports_to_doc_name
				doc.save(ignore_permissions=True)

def create_salary_components():
	components = [
		{"component_name": "Basic Pay", "component_type": "Earning", "is_tax_applicable": 1},
		{"component_name": "House Rent Allowance", "component_type": "Earning", "is_tax_applicable": 1},
		{"component_name": "Professional Tax", "component_type": "Deduction", "is_tax_applicable": 0},
		{"component_name": "Provident Fund", "component_type": "Deduction", "is_tax_applicable": 0},
		{"component_name": "Transport Allowance", "component_type": "Earning", "is_tax_applicable": 0},
	]
	
	for comp in components:
		if not frappe.db.exists("ERP Salary Component", comp["component_name"]):
			doc = frappe.get_doc({"doctype": "ERP Salary Component", **comp})
			doc.insert(ignore_permissions=True)


def create_salary_structures():
	structures = [
		{
			"structure_name": "Standard Tier 1",
			"company": "Your Company",
			"salary_details": [
				{"salary_component": "Basic Pay", "amount": 80000},
				{"salary_component": "House Rent Allowance", "amount": 20000},
				{"salary_component": "Transport Allowance", "amount": 5000},
				{"salary_component": "Professional Tax", "amount": 200},
				{"salary_component": "Provident Fund", "amount": 9600},
			]
		},
		{
			"structure_name": "Standard Tier 2",
			"company": "Your Company",
			"salary_details": [
				{"salary_component": "Basic Pay", "amount": 50000},
				{"salary_component": "House Rent Allowance", "amount": 10000},
				{"salary_component": "Transport Allowance", "amount": 3000},
				{"salary_component": "Professional Tax", "amount": 200},
				{"salary_component": "Provident Fund", "amount": 6000},
			]
		}
	]

	for struct in structures:
		if not frappe.db.exists("ERP Salary Structure", struct["structure_name"]):
			doc = frappe.get_doc({
				"doctype": "ERP Salary Structure",
				"structure_name": struct["structure_name"],
				"is_active": 1,
				"company": struct["company"]
			})
			for detail in struct["salary_details"]:
				doc.append("salary_details", detail)
			doc.insert(ignore_permissions=True)


def create_holiday_list():
	fiscal_year = str(today().split('-')[0])
	list_name = f"Standard Holidays {fiscal_year}"
	
	if not frappe.db.exists("ERP Holiday List", list_name):
		doc = frappe.get_doc({
			"doctype": "ERP Holiday List",
			"holiday_list_name": list_name,
			"fiscal_year": fiscal_year
		})
		
		# Add a few default holidays
		holidays = [
			{"holiday_date": f"{fiscal_year}-01-01", "description": "New Year's Day"},
			{"holiday_date": f"{fiscal_year}-05-01", "description": "Labor Day"},
			{"holiday_date": f"{fiscal_year}-12-25", "description": "Christmas Day"},
		]
		
		for h in holidays:
			doc.append("holidays", h)
			
		doc.insert(ignore_permissions=True)


def create_leave_allocations():
	fiscal_year = str(today().split('-')[0])
	employees = frappe.get_all("ERP Employee", pluck="name")
	
	for emp in employees:
		for leave_type in ["Earned Leave", "Casual Leave", "Sick Leave"]:
			max_allowed = frappe.db.get_value("ERP Leave Type", leave_type, "max_leaves_allowed")
			
			if not frappe.db.exists("ERP Leave Allocation", {"employee": emp, "leave_type": leave_type, "fiscal_year": fiscal_year}):
				doc = frappe.get_doc({
					"doctype": "ERP Leave Allocation",
					"employee": emp,
					"leave_type": leave_type,
					"fiscal_year": fiscal_year,
					"total_leaves_allocated": max_allowed
				})
				doc.insert(ignore_permissions=True)


def create_attendances():
	employees = frappe.get_all("ERP Employee", pluck="name")
	dates = [today(), add_days(today(), -1), add_days(today(), -2)]
	
	for emp in employees:
		for d in dates:
			if not frappe.db.exists("ERP Attendance", {"employee": emp, "attendance_date": d}):
				doc = frappe.get_doc({
					"doctype": "ERP Attendance",
					"employee": emp,
					"attendance_date": d,
					"status": "Present",
					"check_in_time": "09:00:00",
					"check_out_time": "18:00:00"
				})
				doc.insert(ignore_permissions=True)
				doc.submit()

def fix_workspace_roles():
	if frappe.db.exists("Workspace", "Employee ERP"):
		ws = frappe.get_doc("Workspace", "Employee ERP")
		ws.set("roles", [])
		ws.append("roles", {"role": "System Manager"})
		ws.append("roles", {"role": "HR Manager"})
		ws.flags.ignore_permissions = True
		ws.save()
		frappe.db.commit()
		print("Workspace roles updated successfully.")
