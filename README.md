# 📦 Sarveksha ERP — Vendor Purchase Order (VPO) & Equipment Module

This repository contains the stabilized, secure, and audited **Vendor Purchase Order (VPO)** module and **Equipment Management** module for **Sarveksha ERP**. The system automates dynamic company address/letterhead fetching, enforces strict role-based document locking, overrides standard printing mechanisms, drives an approval workflow using high-visibility action buttons, and maintains a structured audit trail visible on the Frappe desk.

---

## 📑 Table of Contents

1. [System Overview & Business Context](#1-system-overview--business-context)
2. [Workflow State Machine & MoM Design](#2-workflow-state-machine--mom-design)
3. [Key Files & Code Architecture](#3-key-files--code-architecture)
4. [Role-Based Access Control (RBAC) & Permissions](#4-role-based-access-control-rbac--permissions)
5. [Key Feature Implementations](#5-key-feature-implementations)
6. [Local Test Accounts](#6-local-test-accounts)
7. [Running & Verifying Tests](#7-running--verifying-tests)
8. [Migration Guide](#8-migration-guide)
9. [Troubleshooting Migration Errors](#9-troubleshooting-migration-errors)

---

## 1. System Overview & Business Context

In the Sarveksha procurement lifecycle, overseas subsidiary entities raise purchase requirements to **Sarveksha Realty and Inframine LLP (SRI India)**. SRI India then reviews these demands and issues a Purchase Order to vendor manufacturers.

The VPO module ensures:
* **Statutory Compliance**: Issuing entities must display correct physical addresses, registration details, PAN, and local tax numbers (e.g., GSTIN).
* **Tax Optimization**: SRI India holds an Export LUT (Letter of Undertaking) allowing a concessional 0.1% GST rate instead of standard GST rates for export-bound goods.
* **T&C Automation**: Multi-selection of standard terms automatically loaded based on company jurisdiction (e.g., LUT terms, country-specific terms).
* **Audit Trail**: Every workflow transition and comment is recorded and displayed in a structured, exportable audit table at the bottom of the VPO form (desk-only, not printed).

---

## 2. Workflow State Machine & MoM Design

The workflow replaces standard manual state changes with top-level, role-specific action buttons.

### Revised 4-Stage State Machine
```text
                      +-------------------+
                      |     Generator     |
                      |    (State: Draft) |
                      +---------+---------+
                                |
                   Send Forward | (Generate PO)
                                v
                      +-------------------+
                      |     Verifier      |
                      | (State: Generated)|
                      +----+---------+----+
                           |         |
              Send Forward |         | Send Back
                  (Verify) |         | (Reason prompt)
                           v         v
                      +----+---------+----+
                      |     Approver      |
                      | (State: Verified) |
                      +----+---------+----+
                           |         |
              Send Forward |         | Send Back
                 (Approve) |         | (Reason prompt)
                           v         v
                      +----+---------+----+
                      |     Generator     |
                      | (State: Approved) |
                      +---------+---------+
                                |
                                | Print Allowed
                                v
                          [ PDF / Print ]
```

### Automatic Transitions & Rules (MoM Compliance)
1. **Yet to be Verified (Generated)**: When a PO Generator creates a document, the initial status is `Draft`. Once they click `Send Forward` (Generate PO), the document's state transitions to `Generated` (which represents **Yet to be Verified**). It is no longer in the `Draft` state, and the Generator is locked out of making further edits.
2. **No Manual Status Select**: The `workflow_state` is read-only and automatically updated based on the action button clicked.
3. **List View Visibility**: Only **Pending Approval** (Generated, Verified) and **Approved** POs are visible in the PO list view for verification/approval roles; all other draft stages are filtered out.
4. **Send Back Remarks**: Clicking `Send Back` prompts the user for remarks, writes them to `verifier_comments` or `approver_comments`, and redirects the document back.

### Custom Button & Print Logic Modifications
* **Top-Level Exclusive Buttons**: The custom workflow action buttons (`Send Forward` / `Send Back`) are exposed as prominent top-level buttons on the form, avoiding nested dropdowns.
  * **Primary Styling**: `Send Forward` is styled as a primary action button (`primary`).
  * **Danger Styling**: `Send Back` is styled as a danger action button (`danger`).
* **Unsaved & New Documents Support**: Workflow buttons are shown on all editable forms (`docstatus === 0`), even if the form has unsaved edits or is new (`__islocal` / `__unsaved`). When clicked, the script automatically triggers a form save (`frm.save()`) first before running the workflow RPC transition, ensuring no changes are lost.
* **Toolbar Print Guarding**: The default printer icon/button in the top-right toolbar (`frm.page.btn_print`) and the standard Print/PDF menu options are completely hidden (`frm.page.set_print_btn_display(false)`) for all unapproved documents. Printing is restricted to approved VPOs and authorized roles.

---

## 3. Key Files & Code Architecture

### 1. Python Controller
* **Path**: `sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order.py`
* **Key Functions**:
  * `validate_generator_edit_rights()`: Prevents `PO Generator` from editing fields once the PO has moved past the `Draft` state.
  * `validate_audit_comments_edit_rights()`: Protects verification and approval remark logs from being tampered with outside their active stage.
  * `get_company_details(company)`: Whitelisted RPC — retrieves company letterhead, port, currency, tax IDs, and physical address.
  * `get_supplier_payment_details(supplier)`: Whitelisted RPC — fetches GSTIN, PAN, bank details, payment terms, and advance % from supplier master.
  * `get_workflow_activity_history(docname)`: Whitelisted RPC — returns structured workflow transitions + comments for the audit trail table.
  * `assign_ref_number()`: Generates a sequential approved-PO reference number (separate from internal `name`). Amendments get `-1`, `-2` suffixes.
  * `has_permission()`: Enforces server-side print guarding.

### 2. JS Controller
* **Path**: `sarveksha_erp/vendor_management/doctype/vendor_purchase_order/vendor_purchase_order.js`
* **Key Functions**:
  * `company()`: Populates company address, PAN, and GSTIN dynamically via RPC.
  * `vendor()`: Triggers `get_supplier_payment_details` to auto-fill GSTIN, bank, payment terms, advance %.
  * `handle_shipment_type_change()`: Shows/hides `shipment_subtype` dropdown based on selected shipment type.
  * `render_workflow_activity_history()`: Fetches and renders the styled approval audit table in the `workflow_history_html` HTML field.
  * `export_history_to_excel()`: Generates and downloads a `.csv` of the audit trail.
  * `render_sidebar_custom_info()`: Injects Revision No., Remarks, and Verifier/Approver comments into the sidebar.

### 3. Print Format
* **Path**: `sarveksha_erp/vendor_management/print_format/vendor_purchase_order_format/vendor_purchase_order_format.html`
* Audit trail is **not** in the print format — it is desk-only.
* Ref No. prints as `doc.name` (internal series).

### 4. Equipment GST Seeder
* **Path**: `sarveksha_erp/equipment_management/doctype/equipment/populate_gst.py`
* Populates `gst_percentage` on all Equipment records using a two-tier HSN→GST rate lookup based on the official Indian GST Council schedule.

---

## 4. Role-Based Access Control (RBAC) & Permissions

| Role | Create PO | Edit Draft | Verify Stage | Approve Stage | Print Approved PO | Edit Remarks |
|---|---|---|---|---|---|---|
| **PO Generator** | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **PO Verifier** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ *(verifier_comments)* |
| **PO Approver** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ *(approver_comments)* |
| **Procurement Manager**| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **System Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 5. Key Feature Implementations

### Concessional LUT Tax Calculations (0.1% GST)
* If `is_lut_applicable` is ticked, the tax calculations inside `calculate_gst_and_totals` apply a concessional rate of `0.1%` IGST (CGST and SGST are zeroed out).
* If unticked, it falls back to standard tax rules based on vendor location.

### Standard Terms Multi-Selection
* Users can select multiple pre-configured terms (e.g. standard export terms + local LUT terms).
* Standard terms are auto-appended to the document's standard terms table based on the company jurisdiction.

### PO Approval Audit Trail (Desk-Only)
* Visible at the bottom of every VPO form at `/app/vendor-purchase-order/SRIPO-XXXX`.
* Shows: No, Date & Time, User, Workflow State, Remarks/Comments.
* "Export to Excel" button downloads a `.csv` file for compliance records.
* **NOT** rendered in the PDF print format — the printout stays clean.

### Equipment GST Rates from HSN
* All 3,290 Equipment records have `gst_percentage` populated from the official Indian GST schedule.
* Rates: 5% (vaccines, medical O₂, solar), 12% (pharmaceuticals, medical instruments), 18% (chemicals, machinery, electrical), 28% (perfumes, special vehicles).
* Can be re-run after new equipment is added.

---

## 6. Local Test Accounts

All accounts use the password **`admin`** for ease of development and testing.

* **PO Generator**: `po_generator@sarveksha.com`
* **PO Verifier**: `po_verifier@sarveksha.com`
* **PO Approver**: `po_approver@sarveksha.com`
* **Procurement Manager**: `procurement_manager@sarveksha.com`
* **System Admin**: `admin@sarveksha.com`

---

## 7. Running & Verifying Tests

Run the VPO integration test suite:

```bash
bench --site development run-tests --module sarveksha_erp.vendor_management.doctype.vendor_purchase_order.test_vendor_purchase_order
```

*Expected output:*
```
✔  test_audit_trail_tracking
✔  test_creation_restrictions_for_verifiers_and_approvers
✔  test_dynamic_uom_creation
✔  test_get_workflow_activity_history
✔  test_payment_status_modification_restriction
✔  test_print_permission_restriction

Ran 6 tests in ~20s
OK
```

---

## 8. Migration Guide

Migration is required whenever DocType schemas, fixtures, or Python controller changes are pulled from the repository. Run migration every time you pull new changes.

### Standard Migration (after every pull)

```bash
# 1. Navigate to the bench root
cd /home/umeshraj/erp/frappe-bench

# 2. Pull latest changes (your branch)
cd apps/sarveksha_erp
git pull upstream umesh-test
cd ../..

# 3. Run database migration to apply schema changes
bench --site development migrate

# 4. Clear all server-side and browser-side caches
bench --site development clear-cache
bench --site development clear-website-cache

# 5. Hard refresh in browser
# Chrome/Firefox: Ctrl + Shift + R
# Safari/Mac:     Cmd + Shift + R
```

### First-Time Setup / Fresh Install

```bash
# Install the app on your site if not already done
bench --site development install-app sarveksha_erp

# Run migration to create all tables and seed fixtures
bench --site development migrate

# Populate Equipment GST rates from HSN codes
bench --site development execute \
  sarveksha_erp.equipment_management.doctype.equipment.populate_gst.populate_gst_from_hsn

# Start the development server
bench start
```

### Re-export Fixtures (after changing DocTypes via UI)

If you modify a DocType, Custom Field, Workflow, or Print Format through the Frappe UI, export the fixtures before committing:

```bash
bench --site development export-fixtures
```

Then stage and commit:

```bash
cd apps/sarveksha_erp
git add sarveksha_erp/fixtures/
git commit -m "chore: update fixtures after UI changes"
git push upstream umesh-test
```

---

## 9. Troubleshooting Migration Errors

### ❌ Error: `Column already exists` or `Duplicate column`

**Cause**: A field was added manually to the DB or a previous partial migration left the column behind.

**Fix**:
```bash
# Drop the duplicate column manually (replace tabDocType and column_name)
bench --site development mariadb --execute \
  "ALTER TABLE \`tabVendor Purchase Order\` DROP COLUMN IF EXISTS column_name;"

# Then re-run migration
bench --site development migrate
```

---

### ❌ Error: `Table 'development.tabXxx' doesn't exist`

**Cause**: A DocType was added in code but the table was never created (migration not run after adding the DocType).

**Fix**:
```bash
bench --site development migrate
```
If it still fails, reload the DocType manually:
```bash
bench --site development execute \
  "frappe.reload_doctype('Your DocType Name', force=True)"
```

---

### ❌ Error: `frappe.exceptions.AppNotInstalledError`

**Cause**: The `sarveksha_erp` app is not installed on the site.

**Fix**:
```bash
bench --site development install-app sarveksha_erp
bench --site development migrate
```

---

### ❌ Error: `Cannot delete X as it has child nodes`

**Cause**: Trying to delete a parent record (Company/Supplier Group/etc.) that has child records linked to it.

**Fix — delete children first via SQL**:
```bash
bench --site development mariadb
```
```sql
-- Example: find children of a parent company
SELECT name, parent_company FROM `tabCompany` WHERE parent_company = 'Parent Name';

-- Delete children first
DELETE FROM `tabCompany` WHERE parent_company = 'Parent Name';

-- Then delete parent
DELETE FROM `tabCompany` WHERE name = 'Parent Name';
```

---

### ❌ Error: `UOM validation error` on Equipment items

**Cause**: An equipment line item in VPO references a UOM that doesn't exist in the `tabUOM` table.

**Fix**: The controller auto-creates missing UOMs. If it still fails, insert manually:
```bash
bench --site development mariadb --execute \
  "INSERT IGNORE INTO \`tabUOM\` (name, uom_name) VALUES ('Nos', 'Nos');"
bench --site development migrate
```

---

### ❌ Workflow buttons or Audit Trail not appearing in UI

**Cause**: Browser cache is serving old JavaScript.

**Fix**:
```bash
bench --site development clear-cache
```
Then in browser: **`Ctrl + Shift + R`** (hard refresh).

If still not appearing, check the browser console for JS errors:
- Open DevTools → Console tab → reload the VPO form.
- Look for any `Uncaught ReferenceError` or `frappe.call` 404 errors.
- A 404 on a Python RPC usually means `bench migrate` was not run after a Python file change.

---

### ❌ Test data (`_Test Company`, `_Test Supplier`) reappearing in dropdowns

**Cause**: Running `bench run-tests` re-seeds Frappe's built-in test data into the DB.

**Fix — clean with SQL**:
```bash
bench --site development mariadb --execute "
DELETE FROM \`tabCompany\` WHERE name LIKE '\_Test%' OR name LIKE '%Test%';
DELETE FROM \`tabSupplier\` WHERE name LIKE '\_Test%';
DELETE FROM \`tabSupplier Group\` WHERE name = '_Test Supplier Group';
"
bench --site development clear-cache
```

---

### ℹ️ Useful SQL Queries for Debugging

```bash
# Open the interactive SQL console
bench --site development mariadb
```

```sql
-- View all VPOs
SELECT name, vendor, workflow_state, creation FROM `tabVendor Purchase Order` ORDER BY creation DESC LIMIT 20;

-- View workflow history comments for a specific PO
SELECT owner, comment_type, content, creation
FROM `tabComment`
WHERE reference_doctype = 'Vendor Purchase Order'
  AND reference_name = 'SRIPO-0027'
ORDER BY creation ASC;

-- Check GST rates on Equipment
SELECT gst_percentage, COUNT(*) FROM `tabEquipment` GROUP BY gst_percentage;

-- Find Equipment with missing HSN
SELECT equipment_code, equipment_name FROM `tabEquipment` WHERE hsn_code IS NULL OR hsn_code = '';

-- Check all companies (no test data should remain)
SELECT name, parent_company FROM `tabCompany` ORDER BY name;
```
