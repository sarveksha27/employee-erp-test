import json

path = "/workspace/development/frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/workspace/vendor_management/vendor_management.json"

with open(path, "r") as f:
    data = json.load(f)

content = json.loads(data.get("content", "[]"))

# Function to add shortcut if not exists
def add_shortcut(content, name, id_val):
    exists = any(block.get("data", {}).get("shortcut_name") == name for block in content if block.get("type") == "shortcut")
    if not exists:
        content.append({
            "id": id_val,
            "type": "shortcut",
            "data": {
                "shortcut_name": name,
                "col": 4
            }
        })

add_shortcut(content, "Vendor Purchase Order", "sc_vendor_purchase_order")
add_shortcut(content, "Equipment", "sc_equipment")

# Add a Card block if it doesn't exist to render the Links
has_card = any(block.get("type") == "card" for block in content)
if not has_card:
    content.append({
        "id": "cd_vendor_portal",
        "type": "card",
        "data": {
            "card_name": "Vendor Portal",
            "col": 4
        }
    })

data["content"] = json.dumps(content)

with open(path, "w") as f:
    json.dump(data, f, indent=1)

print("Workspace JSON updated successfully.")
