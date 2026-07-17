import frappe
from frappe.desk.desktop import get_workspaces

def execute():
	frappe.set_user("Administrator")
	ws = get_workspaces()
	pages = ws.get('pages', [])
	print(f"Total pages: {len(pages)}")
	for p in pages:
		if p.get('name') in ['Employee ERP', 'Projects', 'Quality']:
			print(p.get('name'), p.get('title'), p.get('module'), p.get('is_hidden'), p.get('public'))
