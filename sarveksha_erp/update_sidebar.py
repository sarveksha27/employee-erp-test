import json
import datetime

path = "/workspace/development/frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/workspace_sidebar/vendor_management/vendor_management.json"

with open(path, "r") as f:
    data = json.load(f)

# Add Equipment if it's missing
has_equipment = any(item.get("link_to") == "Equipment" for item in data.get("items", []))
if not has_equipment:
    data["items"].append({
        "child": 0,
        "collapsible": 1,
        "icon": "settings",
        "indent": 0,
        "keep_closed": 0,
        "label": "Equipment",
        "link_to": "Equipment",
        "link_type": "DocType",
        "show_arrow": 0,
        "type": "Link"
    })

# Also rename 'Purchase Orders' to 'Vendor Purchase Order' to be clear for the user
for item in data.get("items", []):
    if item.get("link_to") == "Vendor Purchase Order":
        item["label"] = "Vendor Purchase Orders"

# Update modified timestamp to force sync
data["modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

with open(path, "w") as f:
    json.dump(data, f, indent=1)

print("Workspace Sidebar updated successfully.")
