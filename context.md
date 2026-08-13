# Sarveksha ERP — Vendor Purchase Order Module: Change Context

## Overview
All changes are on branch `umesh-test` of the `sarveksha_erp` app.
Base commit: `a20ece2`

---

## Files Changed

### 1. `vendor_purchase_order.py`
**New methods added:**

- **`validate()`** — Extended to:
  - Auto-set `prepared_by` to the logged-in user on new docs
  - Clear `ref_number` on draft state
  - Call `validate_unique_ref_number()`

- **`validate_unique_ref_number()`** — Blocks duplicate `ref_number` values across approved POs.

- **`assign_ref_number()`** — Generates a sequential approved-PO reference number (separate from the internal `name`). Handles amendments by appending `-1`, `-2` suffixes.

- **`get_supplier_payment_details(supplier)`** *(whitelisted RPC)* — Returns supplier GSTIN, PAN, bank details, payment terms description, and computed advance percentage from `Payment Terms Template Detail`.

- **`get_workflow_activity_history(docname)`** *(whitelisted RPC)* — Returns a structured chronological list of workflow transitions and manual comments for a given PO, used to render the in-form audit trail table.

**Modified logic:**
- On approval transition: sets `signatory` from approver's full name, calls `assign_ref_number()`.
- On "Returned to Verifier / Generator" transitions: increments `revision` counter.
- `ref_number` added to the immutable fields list (cannot be changed after approval).

---

### 2. `vendor_purchase_order.js`
**New functions added:**

- **`render_sidebar_custom_info(frm)`** — Injects Revision No., Remarks, and Verifier/Approver comments into the Frappe document sidebar.

- **`handle_shipment_type_change(frm)`** — Shows/hides the `shipment_subtype` dropdown based on `shipment_type` selection:
  - `Containerized` → 20/40 GP, HQ, SOC container options
  - `Flat Rack` → 20/40 Flat track options
  - `Oversized` → 20/40 ODC options
  - Other types → hides the subtype field

- **`render_workflow_activity_history(frm)`** — Calls `get_workflow_activity_history` RPC and renders a styled, alternating-row table in the `workflow_history_html` HTML field. Includes "Export to Excel" button.

- **`export_history_to_excel(po_name, data)`** — Generates and triggers download of a `.csv` file containing the full approval audit trail.

**Modified triggers:**
- `refresh`: now calls `render_sidebar_custom_info`, `handle_shipment_type_change`, `render_workflow_activity_history`, and fetches supplier payment details via RPC on load.
- `vendor`: triggers `get_supplier_payment_details` RPC to auto-populate GSTIN, PAN, bank fields, payment terms, and advance percentage.
- `shipment_type`: triggers `handle_shipment_type_change`.
- Approval/verification panel fields (`verified_by`, `approved_by`, etc.) set to `read_only` in the UI.

---

### 3. `vendor_purchase_order.json`
**New fields added:**
| Fieldname | Type | Description |
|---|---|---|
| `po_type` | Select | `Vendor PO` or `Internal PO` |
| `cha` | Link → Supplier | Customs House Agent |
| `expected_delivery_time` | Time | Time component for delivery date |
| `shipment_subtype` | Select | Dynamic sub-options for shipment type |
| `ref_number` | Data | Sequential approved-PO reference number |
| `revision` | Int | Amendment/revision counter |
| `prepared_by` | Link → User | Auto-set to logged-in user on creation |
| `sec_workflow_history` | Section Break | "PO Approval Audit Trail" section |
| `workflow_history_html` | HTML | Rendered audit table (read-only, form-only) |

**Field ordering:** `sec_workflow_history` and `workflow_history_html` placed at the very end of the field list (after `amended_from`) so the audit trail appears at the bottom of the document form.

---

### 4. `vendor_purchase_order_format.html` (Print Format)
- Ref No. column now shows `doc.name` (internal series) only — `ref_number` removed from print.
- Workflow audit trail block removed from the print format — it is form-only.
- Signatures section, Terms & Conditions, Remarks, and Logistics sections remain unchanged.

---

### 5. `test_vendor_purchase_order.py`
**New test added:**
- **`test_get_workflow_activity_history`** — Creates a VPO, transitions it, adds a manual comment, then asserts that `get_workflow_activity_history()` returns the correct structured data with the comment visible.

All 6 tests pass: `test_audit_trail_tracking`, `test_creation_restrictions_for_verifiers_and_approvers`, `test_dynamic_uom_creation`, `test_get_workflow_activity_history`, `test_payment_status_modification_restriction`, `test_print_permission_restriction`.

---

### 6. `hooks.py`
- Added `has_permission` hook pointing to `vendor_purchase_order.has_permission`.
- Added `permission_query_conditions` hook for list-view filtering.
- Fixture exports defined for: Company, Fiscal Year, Supplier Group, Supplier, Custom Field, Equipment, Contact, Bank, Bank Account, Letter Head, Print Format, Property Setter, Port, Terms and Conditions, Role, Workflow, Workflow State, Workflow Action Master, Custom DocPerm.

---

### 7. Fixtures (`fixtures/`)
- **`custom_field.json`** — All new custom fields for VPO, Supplier (GSTIN label via Property Setter).
- **`property_setter.json`** — Supplier `tax_id` label changed to `GSTIN`.
- **`custom_docperm.json`** — Role-based document permissions for VPO.
- **`print_format.json`** — Updated VPO print format fixture.
- **`company.json`** — Pruned: all `_Test*` and test companies removed from fixture export.
- **`supplier.json`** — Pruned: all `_Test*` suppliers removed.
- **`supplier_group.json`** — `_Test Supplier Group` removed.
- **`fiscal_year.json`** — Test fiscal years removed.
- **`contact.json`** — Test contacts removed.

---

## Database Cleanup (Applied Directly)
All Frappe test data that was leaking into the development site UI has been permanently removed:
- Deleted: all `_Test Company *` records (20 companies)
- Deleted: all `_Test Supplier *` records (10 suppliers)
- Deleted: `_Test Supplier Group`

---

## Key Design Decisions

1. **Audit trail is form-only, not printed** — The `PO Approval Audit Trail` section with the workflow history table is visible only on the Frappe desk form (`/app/vendor-purchase-order/SRIPO-####`), not in the PDF/print format. This keeps the printed PO clean and professional.

2. **Activity log vs Audit Trail** — Frappe's built-in "Activity" sidebar (showing field change logs) is separate from our "PO Approval Audit Trail". Our table only shows workflow state transitions and manual comments, structured in a compliance-ready format.

3. **ref_number is approval-gated** — A reference number is only assigned when the PO reaches "Approved" state. Amendments inherit the parent's ref_number with `-1`, `-2` suffixes. The internal `name` (SRIPO-####) is always the primary key.

4. **Supplier payment details via RPC** — Payment terms, bank details, and GSTIN are fetched server-side on vendor selection to avoid stale cache and security issues with client-side `frappe.db` calls.

5. **Shipment subtype is dynamic** — Options in the `shipment_subtype` dropdown are programmatically set based on `shipment_type` selection, not stored as a static list in the DocType.
