import json
import datetime

path = "/workspace/development/frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/workspace/vendor_management/vendor_management.json"

with open(path, "r") as f:
    data = json.load(f)

# Update the modified timestamp to force bench migrate to sync it
data["modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

with open(path, "w") as f:
    json.dump(data, f, indent=1)

print("Workspace JSON timestamp updated successfully.")
