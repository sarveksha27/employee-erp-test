# Sarveksha ERP — Chronological Timeline & AI Agent Onboarding Context

This document is specifically crafted for **AI Coding Agents** and **Incoming Engineers** taking over development of `sarveksha_erp`. It details the chronological evolution of the codebase from git history, the engineering rationales behind architectural decisions, key invariant rules, and codebase gotchas.

---

## 1. Chronological Repository Timeline

### Phase 1: Inception & Master Data Foundations
- **Commit Range**: `fd80d52` -> `fac4199`
- **What Was Done**:
  - Initialized custom Frappe application `sarveksha_erp`.
  - Configured core company masters for the group entities: *Sarveksha Realty and Inframine LLP (SRI)* as the Indian parent hub, and overseas subsidiaries across Africa and UAE (*Odhav Holdings*, *Sarveksha SL Limited*, *Baani Minerals*, *Sarveksha BSTP SAS*, *Sarveksha Mining SARL*, *Globe Multitrade and Service LLC*, *Sarveksha Botswana*).
  - Seeded initial suppliers and fiscal years via Frappe fixtures.
- **Why**: Established multi-entity organizational structure required for cross-border mining procurement.

### Phase 2: Equipment Master & Primary Key Architecture
- **Commit Range**: `fac4199` -> `09171da` (PRs #2, #3, #4)
- **What Was Done**:
  - Implemented `Equipment` custom DocType with 8-digit HSN codes.
  - Refactored Equipment primary key from HSN code to sequential `equipment_code` (`EQ-00001`, `EQ-00002`...).
  - Populated GST slabs per HSN code and created UI search bars without cluttering the Frappe desk.
- **Why**: Different pieces of equipment frequently share the same 8-digit HSN classification; using HSN as the primary key caused uniqueness collisions.

### Phase 3: Vendor Purchase Order & Approval Workflow Engine
- **Commit Range**: `a1b1722` -> `7c0b1e3` (PRs #18, #19)
- **What Was Done**:
  - Created `Vendor Purchase Order` and child table `Vendor Purchase Order Item`.
  - Designed 4-stage governance workflow: `Draft` -> `Pending Verification` -> `Verified` -> `Approved`.
  - Implemented role segregation: `PO Generator` initiates; `PO Verifier` conducts technical review; `PO Approver` provides commercial sign-off.
  - Restricted PO creation permissions so Verifiers and Approvers cannot bypass the generator queue.
- **Why**: Enforced SOX-style separation of duties to prevent unverified procurement commitments.

### Phase 4: Sequential Numbering, Auditing & UI Enhancements
- **Commit Range**: `4e6ab52` -> `6d83488` (PR #20)
- **What Was Done**:
  - Added sequential commercial reference numbering (`ref_number`) distinct from internal document names (`SRIPO-XXXX`).
  - Added amendment suffix handling (`-1`, `-2`) on document cancellation and re-issuance.
  - Added `get_workflow_activity_history` RPC and styled in-form audit trail table with CSV export.
  - Implemented dynamic container subtype selection based on `shipment_type`.
- **Why**: External suppliers and shipping lines require concise, sequential contract references, while auditors require timestamped user transition histories.

### Phase 5: Legal Compliance, LUT Tax Handling & PDF Stitching
- **Commit Range**: `734de17` -> `606473a` (PRs #21, #22, #23)
- **What Was Done**:
  - Formulated `po_type`: `Vendor PO` vs `Internal PO`.
  - Added LUT (Letter of Undertaking) export tax logic at 0.1% IGST.
  - Implemented `pdf_handler.py` to intercept PDF downloads and dynamically stitch attached supplier quotation PDFs and JPEG/PNG specification sheets into a single consolidated PDF document.
- **Why**: Customs brokers, bankers, and freight forwarders demand all supporting quotes and invoices in one unified PDF rather than multiple detached emails.

### Phase 6: Role Simplification, Proforma Invoice (PI) & Compliance Refinement
- **Current Development Phase**:
  - **Decommissioned Procurement Manager**: Removed `procurement_manager@sarveksha.com` and allowed authorized workflow roles to directly manage payment terms and advance payment percentages.
  - **Proforma Invoice System**:
    - Created DocTypes `Proforma Invoice` and `Proforma Invoice Item`.
    - Enforced strict generation constraint: PI can **only** reference an `Internal PO` (Child -> SRI); external PO references are blocked.
    - Bound SRI margin strictly between **5.0% and 30.0%**.
    - Mandated manual logistics cost entry (freight/insurance are **never** auto-fetched from the PO).
    - Designed `proforma_invoice_format` print format matching contract dataset `PI no 18. SRI-SVB-Tools and Consumables.pdf`.
  - **Loosened Quotation Governance**: Reduced minimum quotation requirement from 3 to **1 quotation**, and added a visible **"Upload Quotation File"** button in the list view row.
  - **Payment Tracking Cleanup**: Deleted redundant fields `second_payment` and `final_payment`.
  - **Uniform A4 PDF Scaling**: Implemented `normalize_page_to_a4()` in `pdf_handler.py` using `pypdf` transformation matrices so all pages scale to exact A4 (`595.28 x 841.89 pt`) with a letter pad on the last page.
  - **Child Company GST Removal**: Completely stripped GST whenever an overseas Child Company is selected as the issuing company.
- **Why**: Aligns system directly with real-world trading flows, international tax exemptions, and streamlined cross-border operations.

### Phase 7: Database Sanitization & Test Fixture Purge
- **What Was Done**:
  - Purged 19 demo/test companies (`_Test Company`, `Parent Group Company India`, etc.) created during ERPNext installation.
  - Purged 10 dummy test suppliers and auxiliary test customers, items, and contacts.
- **Why**: Eliminates user confusion in dropdown selection modals and guarantees a clean production-grade database.

### Phase 8: Data Refresh & Permanent Notify Party
- **What Was Done**:
  - Purged all legacy test POs and PIs.
  - Generated a clean, realistic baseline dataset:
    - **9 Internal POs**: 2 in `Generated (Yet to be Verified)`, 3 in `Verified (Yet to be approved)`, 4 in `Approved`.
    - **9 External POs**: 2 in `Generated (Yet to be Verified)`, 3 in `Verified (Yet to be approved)`, 4 in `Approved`.
    - **4 Proforma Invoices**: Generated strictly over the 4 Approved Internal POs.
  - Codified permanent default Notify Party to `Globe Multitrade & Service LLC` (Sharjah, UAE).
  - Configured DocType Property Setters for default print formats.
- **Why**: Fulfills exact business operational distribution requirements and establishes production-ready test data.

### Phase 9: Full-Page Stationery Background Architecture & Revert of 'श्री'
- **What Was Done**:
  - **Reverted 'श्री' Text & Image**: Removed `॥ श्री ॥` and `shree_symbol.jpg` completely from PO and PI print formats, along with the outer `<thead>` table wrapper that caused artificial page breaks.
  - **Identified Full-Page Stationery Assets**: Recognized that the company letterhead files in `public/files` (`letterhead_sri_india.png`, `letterhead_botswana.jpeg`, `letterhead_sierra_leone.jpeg`, `letterhead_cameroon_baani.jpeg`, `letterhead_cameroon_mining.jpeg`, `letterhead_guinea_bstp.jpeg`) are full-page A4 stationery images (header + border + footer pre-printed).
  - **Eliminated Faulty Cropping/Squeezing**: Removed `<div class="lh-header-crop">` and hardcoded `<div class="letterpad-footer-block">`.
  - **Full-Page Background Overlay Engine**: In `pdf_handler.py`, implemented `apply_stationery_background()`:
    - Renders the stationery image as an exact standard A4 background page (`595.28 x 841.89 pt`) with zero squeezing or distortion.
    - Stamps the document data directly OVER the background image across every page.
    - Configured dynamic top margin clearance (`50mm` standard, `74mm` for Botswana/Mining, `80mm` for Baani) and bottom clearance (`22mm`).
    - Ensures vendor quotation and inspection attachments appended to POs remain in their original format without letterhead stamping.
  - **Synchronized UI Actions**: Updated `proforma_invoice.js` and `proforma_invoice_format.html` to direct all print actions and `/printview` routes to the compiled PDF route `frappe.utils.print_format.download_pdf`.
- **Why**: Delivers pixel-perfect corporate letterhead stationery rendering across all companies without cropping, squeezing, or duplicate footers, exactly matching user requirements.

### Phase 10: Vendor Options Retirement & Comprehensive Test Data Purge
- **What Was Done**:
  - **Removed Vendor Options**: Permanently deleted custom fields `Supplier-custom_approved` (Approved Vendor) and `Supplier-custom_preferred_vendor` (Preferred Vendor) from `tabCustom Field` and dropped the respective columns from `tabSupplier`.
  - **Re-linked Custom Field Ordering**: Linked `Supplier-custom_lead_time_days` directly after `custom_vendor_rating`, and `Supplier-custom_vendor_remarks` after `custom_lead_time_days`.
  - **Purged `_Test Company` and Linked Transactions**: Completely removed `_Test Company` and all its associated test transactions across ERPNext (`Sales Invoice`, `Purchase Invoice`, `Stock Entry`, `Journal Entry`, `Quotation`, `Sales Order`, `Purchase Receipt`, `Material Request`, `Supplier Quotation`, `Accounts`, `Shipping Rules`, etc.).
  - **Purged Residual Test Data**: Deleted dummy/test records in `tabVendor Payment`, disabled test record generation in `test_records.py`, and updated test fixtures to reference production companies.
- **Why**: Eliminates obsolete checkboxes on vendor masters, ensures clean dropdowns with only active production entities, and maintains database integrity.

---

## 2. Critical Architecture Rules for Future AI Agents

When working on this repository, you **MUST** adhere to the following rules:

### Rule 1: Bench Site Context & CWD
- In this environment, the Frappe bench is located at `/home/umeshraj/erp/frappe-bench`.
- When invoking Python scripts importing `frappe`, always execute from `/home/umeshraj/erp/frappe-bench/sites` OR initialize with:
  ```python
  import frappe
  frappe.init('development', sites_path='sites')
  frappe.connect()
  ```
- The local development server runs as a background process on port 8000 (`bench serve --port 8000`).

### Rule 2: DocType Linking Conventions
- Do NOT confuse field names:
  - In `Vendor Purchase Order`, the link to `Company` is named `company`.
  - The link to `Supplier` is named `vendor` (its options point to `Supplier`).
  - The child table for equipment is named `items` (DocType `Vendor Purchase Order Item`).
  - In `Proforma Invoice`, the reference field is `internal_po` (linking to `Vendor Purchase Order`).

### Rule 3: The `gst_type` Select Field Trap
- The DocField `gst_type` has options: `\nIGST\nCGST + SGST`.
- **CRITICAL**: Never set `self.gst_type = "None"` (string). That will fail Select validation!
- For non-GST documents (such as overseas Child Companies), set `self.gst_type = None` (in Python) or `""` (in JavaScript).

### Rule 4: Proforma Invoice Reference Invariance
- A Proforma Invoice **MUST NEVER** be created without a referenced `Internal PO`.
- `po.po_type` must equal `"Internal PO"`.
- If a user or API attempts to create a PI for a `"Vendor PO"`, throw a `frappe.ValidationError`.

### Rule 5: Margin Constraints
- Both on `Vendor Purchase Order` (when `po_type == "Internal PO"`) and on `Proforma Invoice`, margin percentages must satisfy:
  $$5.0\% \le \text{margin\_percentage} \le 30.0\%$$
- Any value outside this range must raise a user-friendly `frappe.ValidationError`.

### Rule 6: Logistics Costs Manual Invariance
- In `Proforma Invoice`, freight, insurance, packing, and other logistics charges **MUST NOT** be copied automatically from the PO.
- They must default to `0.0` upon creation and be entered manually by the logistics manager.

---

## 3. Directory Layout & Key Files Quick-Reference

```
sarveksha_erp/
├── docs/                                    # Documentation directory
│   ├── TECHNICAL_OVERVIEW.md                # System architecture & engineering guide
│   ├── USER_GUIDE.md                        # End-user business manual
│   ├── TIMELINE_AND_AI_CONTEXT.md           # This onboarding file
│   ├── SUGGESTIONS.md                       # Roadmap & enhancement proposals
│   └── REQUIREMENTS_AND_GAPS.md             # Gap analysis & missing assets audit
├── datasets-needed/                         # Real-world contract PDFs and datasets
│   ├── PI no 18. SRI-SVB-Tools and Consumables.pdf
│   ├── Final PO SVB - SRI Tools and Consumables.pdf
│   └── ODHAV TO SRI AUGUR FINAL PO No 006 Dt. 12.06.2026.pdf
└── sarveksha_erp/
    └── vendor_management/
        ├── doctype/
        │   ├── vendor_purchase_order/       # Core PO controller, JS, JSON & pdf_handler.py
        │   ├── vendor_purchase_order_item/  # Equipment child table
        │   ├── vendor_purchase_order_quotation/ # Quotation governance child table
        │   ├── proforma_invoice/            # PI controller, JS & schema
        │   └── proforma_invoice_item/       # PI items child table
        └── print_format/
            ├── vendor_purchase_order_format/# Formal PO Print HTML
            └── proforma_invoice_format/     # Export PI Print HTML
```
