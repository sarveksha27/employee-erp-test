# Equipment Management Module

A standalone custom Frappe application designed to catalog heavy engineering, laboratory, construction, electrical, IT, and chemical equipment. 

## Features

1. **Equipment Master DocType**
   - Stores detailed technical and financial metadata for all heavy engineering and laboratory equipment.
   - **Strict 8-digit HSN Code Primary Key:** The unique identifier (ID) is mapped directly to the HSN code for strict compliance.
   - **Auto-generated Equipment Codes:** Sequential codes (e.g., `EQ-00001`, `EQ-00002`) are generated dynamically on insertion.
   - **Dual-Currency Costing:** Support for tracking prices in both `INR` (Indian Rupees) and `USD` (US Dollars).

2. **Pre-Seeded High-Integrity Dataset**
   - Includes **3,290** high-integrity equipment records pre-loaded as app fixtures.
   - All HSN records are normalized to exactly 8 digits.
   - Excludes "General" category items, leaving only specific equipment groups (Mining, Laboratory, Construction, Electrical, IT, and Chemicals).

3. **Workspace Dashboard & Sidebar**
   - Configured with a clean, single-purpose sidebar workspace linking directly to the Equipment list.
   - Includes a visual "Equipment by Category" dashboard chart.

---

## Installation & Setup

1. **Get the App**
   ```bash
   bench get-app https://github.com/manikkDev/employee-erp-test.git --branch equip
   ```

2. **Install on Site**
   ```bash
   bench --site development install-app equipment_management
   ```

3. **Run Migration (Import Data)**
   All 3,290 pre-seeded equipment items are stored as app fixtures and will automatically import into your database during migration:
   ```bash
   bench --site development migrate
   ```

---

## Technical Architecture

* **Database Table:** `tabEquipment`
* **DocType Definition:** `equipment_management/doctype/equipment/`
* **Data Fixtures:** `equipment_management/fixtures/equipment.json`
* **Autonaming Hook:** Handled via `before_insert` in `equipment.py`.
