# 📦 Sarveksha ERP — Vendor Management, Equipment & Purchase Governance

Sarveksha ERP is a specialized Frappe/ERPNext application built for international procurement, heavy equipment lifecycle management, multi-jurisdiction vendor operations, and cross-border purchase order governance.

The system powers procurement workflows between overseas subsidiary operating entities and **Sarveksha Realty and Inframine LLP (SRI India)**, enforcing statutory tax compliance, automated Letter of Undertaking (LuT) concessional GST calculation, strict role-based approval governance, and pixel-perfect corporate letterhead printing.

---

## 📑 Table of Contents

- [1. Architectural Overview & Entity Hierarchy](#1-architectural-overview--entity-hierarchy)
- [2. Vendor Management Module](#2-vendor-management-module)
- [3. Equipment Management Module](#3-equipment-management-module)
- [4. Vendor Purchase Order (VPO) Governance](#4-vendor-purchase-order-vpo-governance)
  - [4.1 Dual PO Category Architecture](#41-dual-po-category-architecture)
  - [4.2 4-Stage Workflow State Machine](#42-4-stage-workflow-state-machine)
  - [4.3 LuT Tax Calculation Engine](#43-lut-tax-calculation-engine)
  - [4.4 PDF Normalization & Full-Page Stationery Engine](#44-pdf-normalization--full-page-stationery-engine)
  - [4.5 Quotation Governance](#45-quotation-governance)
- [5. Proforma Invoice (PI) Module](#5-proforma-invoice-pi-module)
- [6. Role-Based Access Control (RBAC)](#6-role-based-access-control-rbac)
- [7. Production Companies & Master Data Standards](#7-production-companies--master-data-standards)
- [8. Documentation Index](#8-documentation-index)
- [9. Installation & Bench Setup](#9-installation--bench-setup)
- [10. Running Test Suites](#10-running-test-suites)

---

## 1. Architectural Overview & Entity Hierarchy

Sarveksha operates a global trading and mining network where overseas operating entities purchase capital machinery and operational consumables through a centralized procurement hub:

```text
[ Overseas Subsidiary Operating Entities ]
  ├── Sarveksha BSTP SAS (Guinea)
  ├── Sarveksha Mining SARL (Cameroon)
  ├── Odhav Holdings
  ├── Sarveksha SL Limited (Sierra Leone)
  ├── Baani Minerals (Cameroon)
  ├── Globe Multitrade and Service LLC (UAE - Permanent Notify Party)
  └── Sarveksha Botswana Proprietary Limited (Botswana)
                                │
                                │ Internal PO (Mandatory 5% Margin)
                                v
      [ Sarveksha Realty and Inframine LLP (SRI India) ]
                                │
                                │ External PO (Export LuT 0.1% GST)
                                v
               [ Global Equipment Manufacturers & Vendors ]
```

---

## 2. Vendor Management Module

The **Supplier** DocType is enhanced with comprehensive cross-border compliance and operational profiling:

- **Entity Identification**: Vendor Name, Arabic Name, Supplier Group, Vendor Code, Vendor Type (`Manufacturer`, `Trader`, `Service Provider`, `Logistics`).
- **Statutory & Tax Records**: Permanent Account Number (PAN), Tax Identification Number (TIN), GSTIN/VAT Number, and automated TDS applicability/percentage.
- **Multi-Currency Banking**: Bank Name, Branch, Account Number, IFSC, SWIFT Code, IBAN, and Bank Currency.
- **Operational Metrics**:
  - `custom_vendor_rating` (1–5 Star Rating)
  - `custom_lead_time_days` (Average procurement turnaround time)
  - `custom_vendor_remarks` (Operational and audit observations)
  - `custom_vendor_documents` (Mandatory compliance certificates and verification files)

> [!NOTE]
> **Vendor Options Retirement**: The legacy `custom_approved` (Approved Vendor) and `custom_preferred_vendor` (Preferred Vendor) boolean checkboxes have been formally decommissioned and purged from the database to streamline vendor master forms.

---

## 3. Equipment Management Module

The **Equipment** DocType manages 3,290+ heavy machinery, exploratory, and laboratory assets:

- **Asset Identifiers**: Sequential identifier (`EQ-#####`), Equipment Name, Model, Brand, Category.
- **Tax Classification**: Harmonized System Nomenclature (HSN/SAC) with automated GST slab resolution.
- **Service & Maintenance**: Warranty period in months, calibration requirement indicator, and primary supplier reference.

---

## 4. Vendor Purchase Order (VPO) Governance

### 4.1 Dual PO Category Architecture

1. **Internal PO**:
   - Issued by child companies (e.g., Botswana, Cameroon, Guinea) to **Sarveksha Realty and Inframine LLP**.
   - Vendor field is restricted strictly to SRI India.
   - SRI India cannot issue an Internal PO to itself.
   - Enforces a mandatory **5% internal margin** on the total taxable value plus logistics.
   - Serves as the basis for generating downstream **Proforma Invoices**.

2. **External PO**:
   - Issued by SRI India or subsidiary entities directly to external vendors worldwide.
   - Requires at least 1 competitive vendor quotation and a comparative evaluation sheet attached before moving out of Draft.

### 4.2 4-Stage Workflow State Machine

The VPO module implements an approval state machine governed by high-visibility form action buttons:

```text
  [ Draft ]
     │
     │  "Send Forward" (PO Generator)
     v
  [ Generated (Yet to be Verified) ]
     │
     ├── "Send Forward" (PO Verifier) ──> [ Verified (Yet to be approved) ]
     │                                            │
     │  "Send Back" (with mandatory remarks)      ├── "Send Forward" (PO Approver) ──> [ Approved ] (Locked, PDF Active)
     └──> Returns to [ Draft ]                    │
                                                  │  "Send Back" (with mandatory remarks)
                                                  └──> Returns to [ Generated (Yet to be Verified) ]
```

- **Reference Number Generation**: A formal `ref_number` (e.g., `SRIPO-2026-0042`) is generated only upon reaching the **Approved** state.
- **Form Immutability**: All commercial fields are locked once verified/approved.
- **Audit Trail**: Every state change, timestamp, role, and comment is logged into the `PO Approval Audit Trail` table (visible on desk only, omitted from printed copies).

### 4.3 LuT Tax Calculation Engine

- **Export Letter of Undertaking (LuT)**: SRI India possesses an export LuT allowing goods bound for overseas projects to be invoiced at a concessional **0.1% GST** rate.
- Checking the **LuT Applicable** checkbox automatically resets the GST rate of all line items to 0.1%.
- Unchecking the box dynamically restores the standard statutory GST rate from the Equipment Master database.

### 4.4 PDF Normalization & Full-Page Stationery Engine

- Standard Frappe print buttons are hidden on unapproved orders.
- Approved POs are rendered using `pdf_handler.py`:
  - Automatically fetches the full-page A4 corporate stationery background for the issuing entity (`letterhead_sri_india.png`, `letterhead_botswana.jpeg`, etc.).
  - Overlays the document content directly onto the background without distortion or squeezing.
  - Dynamically sets top clearances (`50mm` standard, `74mm` for Botswana/Mining, `80mm` for Baani) and bottom margins (`22mm`).
  - Merges all attached drawings, specifications, and invoices into a unified single PDF, converting image files (`PNG`, `JPG`, `JPEG`) to standard A4 pages.

### 4.5 Quotation Governance

- Tracks competing supplier bids in child table `Vendor Purchase Order Quotation` (Supplier, Date, Amount, Reference, and Quotation File).
- Requires an attached **Quotation Comparison Sheet** before an External PO can be submitted for verification.

---

## 5. Proforma Invoice (PI) Module

The **Proforma Invoice** DocType generates seller-side commercial export invoices for Internal PO transactions:
- **Seller**: Sarveksha Realty and Inframine LLP (SRI India).
- **Buyer**: The purchasing overseas subsidiary entity.
- **Pricing**: Automatically reflects the base PO equipment cost plus the approved internal margin percentage.
- **Logistics**: Freight, insurance, and handling charges are captured independently for export billing.
- **Print Format**: Dedicated `Proforma Invoice Format` styled with export declarations and bank wire instructions.

---

## 6. Role-Based Access Control (RBAC)

| Role | Permissions & Operational Scope |
|---|---|
| **PO Generator** | Creates and edits Draft POs; uploads quotations; clicks `Send Forward` to generate POs. |
| **PO Verifier** | Reviews generated POs; verifies pricing and specifications; forwards to approval or sends back with remarks. |
| **PO Approver** | Executive authority; performs final review; clicks `Approve` to lock document, assign `ref_number`, and activate print formats. |
| **Vendor & Equipment Manager** | Full CRUD access to Vendor (Supplier) records, Company configurations, Equipment catalog, and Port masters. |
| **System Manager / Administrator** | Unrestricted technical oversight, permission assignment, and workflow configuration. |

---

## 7. Production Companies & Master Data Standards

The system strictly enforces production data integrity. All synthetic test records (`_Test Company`, dummy test suppliers, and test vouchers) have been completely purged from the environment.

### Active Operating Entities:
1. **Sarveksha Realty and Inframine LLP** (India — Central Hub)
2. **Sarveksha BSTP SAS** (Guinea)
3. **Sarveksha Mining SARL** (Cameroon)
4. **Odhav Holdings**
5. **Sarveksha SL Limited** (Sierra Leone)
6. **Baani Minerals** (Cameroon)
7. **Globe Multitrade and Service LLC** (UAE — Permanent Notify Party)
8. **Sarveksha Botswana Proprietary Limited** (Botswana)

---

## 8. Documentation Index

Detailed technical specifications and operating guides are maintained in [`docs/`](docs/):

- **[Technical Architecture Guide](docs/TECHNICAL_OVERVIEW.md)**: In-depth controller logic, schema definitions, RPC endpoints, and PDF stitching mechanics.
- **[Database Schema Reference](docs/DATABASE_SCHEMA.md)**: Full SQL table schemas, field data types, foreign keys, and indexes.
- **[End-User Manual](docs/USER_GUIDE.md)**: Step-by-step operating instructions for generators, verifiers, approvers, and logistics staff.
- **[Timeline & AI Context](docs/TIMELINE_AND_AI_CONTEXT.md)**: Git progression, architectural decisions, and key onboarding guidelines.
- **[Requirements & Gap Analysis](docs/REQUIREMENTS_AND_GAPS.md)**: Audit trail of business requirements and ongoing optimizations.
- **[Suggestions & Roadmap](docs/SUGGESTIONS.md)**: Planned future capabilities including OCR quotation ingestion and live vessel tracking.

---

## 9. Installation & Bench Setup

### 1. Clone App into Frappe Bench
```bash
cd ~/erp/frappe-bench
bench get-app https://github.com/sarveksha/sarveksha_erp.git apps/sarveksha_erp
```

### 2. Install on Site
```bash
bench --site development install-app sarveksha_erp
```

### 3. Run Migrations & Fixture Sync
```bash
bench --site development migrate
```

### 4. Clear Cache & Build Assets
```bash
bench --site development clear-cache
bench build --app sarveksha_erp
```

---

## 10. Running Test Suites

Run the automated integration test suite covering end-to-end workflow transitions, quotation governance, LuT calculations, and PDF attachment merging:

```bash
bench --site development run-tests --app sarveksha_erp
```

To run only the Vendor Purchase Order suite:
```bash
bench --site development run-tests --doctype "Vendor Purchase Order"
```
