# Equipment Management Module

A standalone custom Frappe application designed to catalog heavy engineering, laboratory, construction, electrical, IT, and chemical equipment.

## Features

1. **Equipment Master DocType**
   - Stores detailed technical and financial metadata for all heavy engineering and laboratory equipment.
   - **Auto-generated Equipment Codes as Primary Key:** The unique identifier (ID) is dynamically generated sequentially (e.g., `EQ-00001`, `EQ-00002`) on record creation, acting as the primary key.
   - **Non-Unique 8-digit HSN Codes:** Equipment items can share the same HSN code (for cases where multiple equipment configurations fall under a single classification).
   - **Dual-Currency Costing:** Support for tracking prices in both `INR` (Indian Rupees) and `USD` (US Dollars).

2. **Pre-Seeded High-Integrity Dataset**
   - Includes **3,290** high-integrity equipment records pre-loaded as app fixtures.
   - All HSN records are normalized to exactly 8 digits.
   - Excludes "General" category items, leaving only specific equipment groups (Mining, Laboratory, Construction, Electrical, IT, and Chemicals).

3. **Workspace & Sidebar**
   - Clean, minimal sidebar with a single **Equipment** link — no clutter.
   - Home workspace shows a **Quick Access** shortcut directly to the Equipment list (no dashboard charts).

4. **Equipment Name Search Bar**
   - A real-time search bar is rendered at the top of the Equipment list view.
   - Type any part of an equipment name to instantly filter the list.
   - Includes a `×` clear button to reset the search.

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

| Component | Path |
|---|---|
| Database Table | `tabEquipment` |
| DocType Definition | `equipment_management/doctype/equipment/` |
| List View Controller | `equipment_management/doctype/equipment/equipment.js` |
| Data Fixtures | `equipment_management/fixtures/equipment.json` |
| Workspace Definition | `equipment_management/workspace/equipment_management/` |
| Sidebar Definition | `equipment_management/workspace_sidebar/equipment_management.json` |
| Autonaming | Custom `autoname` method in `equipment.py` |

