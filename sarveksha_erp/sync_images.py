import os
import shutil
import frappe

def execute():
    app_files_dir = frappe.get_app_path('sarveksha_erp', 'public', 'files')
    site_files_dir = frappe.get_site_path('public', 'files')

    if not os.path.exists(site_files_dir):
        os.makedirs(site_files_dir)

    copied = 0
    for filename in os.listdir(app_files_dir):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            src = os.path.join(app_files_dir, filename)
            dst = os.path.join(site_files_dir, filename)
            shutil.copy2(src, dst)
            copied += 1
            print(f"Synced {filename} to site public/files")

    print(f"Successfully synced {copied} images to the site directory!")
