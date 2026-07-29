# Sarveksha ERP — PO Enhancement Sprint
## Team Task Assignment & Implementation Guide

**Project:** Vendor Procurement & Payment Tracking System  
**Module:** Purchase Order (PO) Enhancement — Post-Meeting Sprint  
**Meeting Date:** July 28, 2026  
**Repository:** https://github.com/manikkDev/employee-erp-test.git  
**Branch:** `manik`  
**Custom App Path:** `frappe-bench/apps/sarveksha_erp/sarveksha_erp/vendor_management/`

---

> [!IMPORTANT]
> **READ THIS BEFORE STARTING:** Everything you build here is **permanent, production-grade code**. No workarounds. No temporary fixes. Every field must be properly defined in JSON, exported as a fixture, and committed to Git. The boss will demo this system to clients — it must look and work flawlessly.

---

## 📋 Executive Summary — What the Boss Asked For

After reviewing the meeting video and the full Google Doc, the boss has defined **10 specific enhancements** to the existing Purchase Order module. These have been balanced across 4 team members.

---

## 🚦 Execution Timeline & Dependencies (Read Carefully)

To avoid team members being blocked, follow this execution order:

### 🟩 Phase 1: Parallel Execution (Can start immediately)
- **Member 1** can start immediately on the Port Master, Dropdowns, and User Accounts.
- **Member 2** can start immediately on the Terms & Conditions system and LUT logic.
- *Dependency:* Member 1 must finish creating the test User Accounts so Member 3 can test the roles.

### 🟨 Phase 2: Workflow Config (Requires Base Fields)
- **Member 3** can configure the Workflow State Machine.
- *Dependency:* Member 3 must finish creating the exact Workflow States (`Pending Verification`, etc.) before Member 4 can write backend logic.

### 🟥 Phase 3: Backend Hooks (Depends on Workflow)
- **Member 4** implements the Python backend hooks. They rely on the workflow states from Member 3 to trigger the audit trails and mandatory remarks.

---

## 👥 Team Assignment Matrix

| Member | Complexity Level | Assigned Tasks |
|--------|------------------|----------------|
| **Member 1** | 🟡 Medium | Port Master, Dropdowns, User Accounts, GST/PAN Display |
| **Member 2** | 🟡 Medium | Terms & Conditions System, LUT Certificate Tax Logic |
| **Member 3** | 🔴 High | Permission Matrix, PO Workflow Stages (State Machine) |
| **Member 4** | 🔴 Very High | Backend Approval Logic, Audit Trail & Correction History |

---

## 🔄 Git Workflow (Mandatory for Everyone)

```bash
# 1. Always start by pulling latest
cd frappe-bench/apps/sarveksha_erp
git pull origin manik

# 2. Create your own branch for your work
git checkout -b <your-name>/<feature-name>

# 3. Make your changes (code, fixtures)

# 4. Export everything before committing
bench --site development.localhost export-fixtures
bench --site development.localhost export-doc DocType "Port"

# 5. Commit and push
git add .
git commit -m "feat: [short description of what you built]"
git push origin <your-name>/<feature-name>
```

---

## 🟡 Member 1: Master Data & UI Form (Medium)

### Context
You are handling UI field conversions, basic display logic, and creating the new Port DocType.

### Task 1.1: Port Master DocType
1. Create a `Port` DocType (Fields: Port Name, Country, Port Code, Is Active).
2. Seed the records: Mundra, JNPT, Conakry, Durban, Freetown, Douala.
3. Update `port` field on PO to be a `Link` pointing to `Port`.

### Task 1.2: Shipment Type Dropdown
Update `shipment_type` field on PO from `Data` → `Select` with options:
`FCL, LCL, Containerized, Flat Rack, Oversized, Hazardous Cargo, Part Shipment, Height Cargo, Break Bulk, RoRo, Air Freight, Express Courier`

### Task 1.3: Local Test User Accounts
Create 5 user accounts for workflow testing via bench:
- po_generator@sarveksha.com, po_verifier@sarveksha.com, po_approver@sarveksha.com, admin@sarveksha.com, procurement_manager@sarveksha.com

### Task 1.4: GST/PAN Auto-Display on PO
1. Add read-only fields `company_gstin` and `company_pan` to PO.
2. Write client-side JS to auto-fetch when Company is selected.
3. Add to the `vendor_purchase_order_format.html` print format.

### ✅ Definition of Done (Member 1)
- [ ] `Port` DocType created and 6 ports seeded.
- [ ] `shipment_type` shows 12 options as a Select dropdown.
- [ ] 5 test user accounts exist.
- [ ] `company_gstin` and `company_pan` fields auto-fill and appear on print.
- [ ] Fixtures exported.

---

## 🟡 Member 2: Terms System & Tax Logic (Medium)

### Context
You are creating the T&C library and implementing the LUT certificate tax overrides.

### Task 2.1: Standard T&C Templates
Create `Terms and Conditions` records:
- Standard Export PO Terms (Payment, Inspection, LD, Warranty, ISPM-15, Force Majeure, Law).
- Export to Africa Terms, Domestic India Terms, LUT Certificate Terms.

### Task 2.2: PO T&C Fields & Print Format
1. Add `standard_terms` (Link) and `custom_terms` (Text Editor) to the PO DocType.
2. JS to show read-only preview of standard terms.
3. Update Print Format to render both standard and custom terms at the bottom.

### Task 2.3: LUT Certificate Logic (0.1% GST)
1. Add `is_lut_applicable` checkbox to PO.
2. In `vendor_purchase_order.py`, if LUT is checked AND company is "Sarveksha Realty", override tax calculations to use 0.1% GST instead of standard.

### ✅ Definition of Done (Member 2)
- [ ] 4 standard T&C templates created.
- [ ] `standard_terms` and `custom_terms` fields on PO form.
- [ ] Printed PO shows both standard and custom terms.
- [ ] LUT Certificate overrides GST rate to 0.1% for India in Python.
- [ ] Code committed and Fixtures exported.

---

## 🔴 Member 3: Workflow State Machine & Permissions (Hard)

### Context
You are configuring Frappe's native Workflow engine and defining the exact permission matrix. **(Wait for Member 1 to create users before assigning roles).**

### Task 3.1: Create Custom Roles & Permissions
1. Create roles: `PO Generator`, `PO Verifier`, `PO Approver`, `Procurement Manager`.
2. Configure permission matrix for Vendor Purchase Order:
   - PO Generator: Create, Read, Write, Print (at Final stage).
   - Verifier/Approver: Read, Write. Manager: Full access.

### Task 3.2: Configure 4-Stage PO Workflow
Create a `Workflow` DocType for Vendor Purchase Order:
1. **States:** Draft, Pending Verification, Verification Returned, Pending Approval, Approval Returned, Approved, Printed.
2. **Transitions:** Draft -> Pending Verification -> Pending Approval -> Approved.
3. Export workflow to fixtures.

### ✅ Definition of Done (Member 3)
- [ ] 4 Custom roles created.
- [ ] Permission matrix strictly configured.
- [ ] Frappe Workflow created, active, and transitions tested.
- [ ] Workflow exported to fixtures (`hooks.py` updated).

---

## 🔴 Member 4: Backend Logic & Audit Trail (Hardest)

### Context
Implement the immutable audit trail (Correction History) and mandatory remarks on return. **(Wait for Member 3's Workflow states to be finalized).**

### Task 4.1: Mandatory Remarks on Return
In `vendor_purchase_order.py` `validate` hook: If workflow state changes to `Verification Returned` or `Approval Returned`, check respective remarks field. If empty, `frappe.throw()`.

### Task 4.2: Correction History Audit Trail
In `before_save` python hook:
1. Compare current doc values to `get_doc_before_save()` for all financial/commercial fields.
2. If changes exist (during Pending Verification/Approval), append HTML row to `correction_history` field: Field Name, Old Value, New Value, Modified By, Timestamp.

### Task 4.3: Notification Triggers
Set up Frappe Notifications for when a PO enters a specific state (e.g. notify Verifiers).

### ✅ Definition of Done (Member 4)
- [ ] `validate` hook blocks return if remarks are empty.
- [ ] `before_save` correctly logs every field change into the HTML table.
- [ ] Generator sees full audit trail before final printing.
- [ ] Notifications fire correctly on state changes.
- [ ] Python code committed.
