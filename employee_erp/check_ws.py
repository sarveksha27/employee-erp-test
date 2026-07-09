import frappe

def execute():
	projects = frappe.get_doc('Workspace', 'Projects')
	print(f"Projects: public={projects.public}, is_hidden={projects.is_hidden}, parent_page={projects.parent_page}, module={projects.module}, type={projects.type}")
	erp = frappe.get_doc('Workspace', 'Employee ERP')
	print(f"Employee ERP: public={erp.public}, is_hidden={erp.is_hidden}, parent_page={erp.parent_page}, module={erp.module}, type={erp.type}")
