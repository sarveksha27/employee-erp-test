# 📦 Purchase Order (PO) Module Enhancement & Workflow Specification
## Sarveksha ERP — Architectural Specification & Implementation Guide

---

## 📑 Table of Contents
1. [Executive Summary & System Overview](#1-executive-summary--system-overview)
2. [Current Business Flow Context](#2-current-business-flow-context)
3. [Port Selection Enhancement](#3-port-selection-enhancement)
4. [Shipment & Container Type Configuration](#4-shipment--container-type-configuration)
5. [Purchase Order Workflow Stages & State Machine](#5-purchase-order-workflow-stages--state-machine)
6. [Detailed Approval Workflow Implementation](#6-detailed-approval-workflow-implementation)
7. [PO Review & Correction Process (Discrepancy Handling)](#7-po-review--correction-process-discrepancy-handling)
8. [Tax Information & LUT Certificate Logic](#8-tax-information--lut-certificate-logic)
9. [Terms & Conditions Management](#9-terms--conditions-management)
10. [Local User Accounts for Workflow Testing](#10-local-user-accounts-for-workflow-testing)
11. [Role-Based Access Control (RBAC) & Permission Matrix](#11-role-based-access-control-rbac--permission-matrix)
12. [Standard Terms & Conditions Library Catalog](#12-standard-terms--conditions-library-catalog)
13. [Summary of Schema Fields to be Added/Updated](#13-summary-of-schema-fields-to-be-addedupdated)
14. [Company Header, Tax Information & Legal Display Logic](#14-company-header-tax-information--legal-display-logic)

---

## 1. Executive Summary & System Overview

This document presents the detailed architectural specifications, workflow design, schema enhancements, tax logic, user permissions, and Terms & Conditions library for the **Purchase Order (PO) Module Enhancement** in **Sarveksha ERP**.

The enhanced Purchase Order module transforms the vendor procurement lifecycle into an audited, multi-tier compliance framework supporting multi-jurisdictional logistics, flexible shipment containerization, export LUT tax calculations, and dynamic role-based verification.

---

## 2. Current Business Flow Context

```
+-----------------------------------------------------------------------------------+
|  1. Overseas Child Companies (Guinea, Cameroon, Botswana, Sierra Leone, UAE)      |
|     Raise purchase requirements to Sarveksha Realty and Inframine LLP (SRI India) |
+-----------------------------------------------------------------------------------+
                                        │
                                        ▼
+-----------------------------------------------------------------------------------+
|  2. SRI India reviews requirements & generates official Purchase Order (PO)        |
|     to Indian / International Vendors.                                            |
+-----------------------------------------------------------------------------------+
                                        │
                                        ▼
+-----------------------------------------------------------------------------------+
|  3. Vendor issues Proforma Invoice (PI) to SRI.                                   |
|     SRI generates simplified PI for Child Company with 20-30% logistics margin.    |
+-----------------------------------------------------------------------------------+
                                        │
                                        ▼
+-----------------------------------------------------------------------------------+
|  4. Child company transfers funds to SRI. SRI pays Vendor (advance/partial/final) |
|     and manages export/import shipping documents until final delivery.           |
+-----------------------------------------------------------------------------------+
```

1. **Purchase Requirement**: Overseas child companies (e.g., Sarveksha BSTP Guinea, Cameroon, Botswana, Sierra Leone, UAE) raise purchase requirements to Sarveksha Realty and Inframine LLP (SRI India).
2. **PO Generation**: SRI reviews requirements and generates an official Purchase Order to the Indian/International Vendor.
3. **Proforma Invoice (PI) & Logistics Margin**: Vendor issues a PI to SRI. SRI then generates a simplified PI for the Child Company with a 20–30% logistics margin.
4. **Payment & Shipping**: Child company transfers funds to SRI; SRI pays the Vendor (advance/partial/final) and manages export/import shipping documents until final delivery.

---

## 3. Port Selection Enhancement

### Current State
Currently, the port field exists as an unvalidated free-text data field, leading to data entry discrepancies across user entries.

### Required Enhancement
Convert the **Default Port** and **Port** fields into a standardized dropdown selection list (`Select` / `Link` field). Options populate dynamically from system-configured ports categorized by company jurisdiction:

| Jurisdiction | Company Entity | Available Ports |
| :--- | :--- | :--- |
| **India** | Sarveksha Realty and Inframine LLP | Mundra Port, JNPT (Jawaharlal Nehru Port Trust), Chennai Port, Kolkata Port (plus additional configured ports) |
| **Guinea** | Sarveksha BSTP SAS | Port of Conakry |
| **South Africa** | Regional Trade Hub | Port of Durban |
| **Sierra Leone** | Sarveksha SL Limited / Baani Minerals | Freetown Water Quay |
| **Cameroon** | Sarveksha Mining SARL | Port of Douala |
| **UAE** | Globe Multitrade and Service LLC | Jebel Ali Port |

---

## 4. Shipment & Container Type Configuration

### Required Enhancement
Introduce comprehensive shipment and container categorization. Users will be required to select both **Port** and **Shipment/Container Type** during PO creation.

### Shipment Types & Options Catalog

#### General Cargo Types
- **Containerized**: Standard ocean container cargo.
- **Flat Rack**: Heavy machinery or oversized goods requiring open-sided/top containers.
- **Oversized Cargo**: Equipment exceeding standard shipping dimension limits.
- **Hazardous Cargo**: Dangerous chemicals or volatile goods requiring safety protocols.
- **Part Shipment**: Partial LCL (Less than Container Load) consignments.
- **Height Cargo**: Consignments exceeding standard container height limits.

#### Specific Container Selection Types
- **20 GP Container**: 20ft General Purpose Dry Container.
- **40 GP Container**: 40ft General Purpose Dry Container.
- **20 HQ Container**: 20ft High Cube Container (extra height).
- **40 HQ Container**: 40ft High Cube Container (extra height).
- **20 SOC Container**: 20ft Shipper-Owned Container.
- **40 SOC Container**: 40ft Shipper-Owned Container.
- **20 Flat Track (Rack)**: 20ft Flat Rack Container for heavy machinery.
- **40 Flat Track (Rack)**: 40ft Flat Rack Container for heavy equipment.
- **20 ODC**: 20ft Over Dimensional Cargo container setup.
- **40 ODC**: 40ft Over Dimensional Cargo container setup.

---

## 5. Purchase Order Workflow Stages & State Machine

The Purchase Order lifecycle is governed by a strict sequential workflow state machine to ensure auditability, control, and multi-tier verification before printing.

### Workflow Stage Definitions

| Stage Name | Doc Status | Workflow State | Description |
| :--- | :--- | :--- | :--- |
| **1. Generate PO** | `0` (Draft) | **Draft / Pending Verification** | PO Generator creates initial document with equipment, vendor, pricing, and shipment info. |
| **2. Verify PO** | `0` (Draft) | **Pending Approval** | PO Verifier reviews technical details, rate accuracy, HSN codes, and vendor details. |
| **Verification Discrepancy** | `0` (Draft) | **Returned for Verification Fix** | Sent back to Generator by Verifier with corrective feedback. |
| **3. Approve PO** | `0` (Draft) | **Approved & Ready** | PO Approver conducts financial sign-off and commercial terms authorization. |
| **Approval Discrepancy** | `0` (Draft) | **Returned for Approval Fix** | Sent back to Generator by Approver with commercial revision notes. |
| **4. Final Generation & Print** | `1` (Submitted) | **Generated & Printed** | Final PO generated by Generator, locked against edits, exported as official PDF/printed. |

---

## 6. Detailed Approval Workflow Implementation

### Workflow Sequence Steps

1. **PO Generator**: Creates PO (`Draft` state) and forwards to PO Verifier.
2. **PO Verifier Review**:
   - **Option A (Direct Edit)**: Updates technical details directly on the form (captured in Audit History) and forwards to PO Approver.
   - **Option B (Return)**: Enters comments in `Verification Remarks` and sets state to `Returned for Verification Fix`, routing notification back to PO Generator.
3. **PO Approver Review**:
   - **Option A (Direct Edit)**: Adjusts commercial/tax terms directly and signs off, returning approved PO to PO Generator.
   - **Option B (Return)**: Enters comments in `Approval Remarks` and sets state to `Returned for Approval Fix`, routing notification back to PO Generator.
4. **Final Generation & Print**: PO Generator conducts a final review of comments and modification history, submits the PO (`DocStatus 1`), and exports the official document.

---

## 7. PO Review and Correction Process (Discrepancy Handling)

### Verifier Review Controls
When discrepancies are detected during the Verification stage:
- **Option 1 (Direct Correction)**: Verifier modifies incorrect fields directly on the PO form and forwards the PO to the Approver. All field-level edits are automatically captured in the **Correction History Audit Trail** visible to the Generator.
- **Option 2 (Return with Comments)**: Verifier enters mandatory comments in the `verification_remarks` field and changes status to `Returned for Verification Fix`, routing notification back to the Generator.

### Approver Review Controls
When discrepancies are detected during the Approval stage:
- **Option 1 (Direct Correction & Approval)**: Approver adjusts commercial/tax terms directly and signs off. Changes are recorded in **Correction History**.
- **Option 2 (Return with Comments)**: Approver enters notes in `approval_remarks` and returns the PO to the Generator for revision.

### Final Review & Audit Trail Display
Before triggering the **Final Generation & Print** action, the PO Generator is provided with an aggregate Review Dashboard on the PO header showing:
- **Complete Revision History**: Field-by-field diff showing Field Name, Original Value, Updated Value, Modified By, and Timestamp.
- **Review Comments Thread**: Chronological log of all comments submitted by Verifiers and Approvers.

---

## 8. Tax Information & LUT Certificate Logic

### Company Tax Information Display
Every generated Purchase Order must explicitly render company tax identifiers on the printed document header:
- **GSTIN Number**: e.g., `24AAAFX1234F1Z9` (for SRI India)
- **PAN Number**: e.g., `AAAFX1234F`

### SRI India LUT Certificate Tax Calculation Scheme
- **Business Rule**: SRI India holds an Export LUT (Letter of Undertaking) Certificate. When purchasing equipment/supplies intended for export to overseas branches, vendors agreeing to LUT terms are subject to a concessional **0.1% GST rate** instead of standard GST rates (18%, 12%, 28%).
- **Field Implementation & Logic**:
  - Field: `is_lut_applicable` *(Check Box)* — Label: `LUT Certificate Applicable (0.1% GST)`
  - Calculation Formula: If `is_lut_applicable == 1`, set IGST rate to `0.1%` ($\text{Taxable Value} \times 0.001$), setting CGST = 0 and SGST = 0.

---

## 9. Terms & Conditions Management

### Hybrid Structure
Every Purchase Order requires a hybrid Terms & Conditions configuration:
1. **Standard Default Terms**: Auto-loaded standard business clauses on document creation based on standard template selection.
2. **PO-Specific Custom Terms**: Editable rich text section for special project or delivery requirements.

### Form Configuration Preview
- **Standard Terms Dropdown**: Selectable pre-configured templates (e.g., *Standard Export PO Terms*).
- **Standard Clause Preview**: Auto-populated preview of clauses (Payment, Inspection, Delivery).
- **Custom / Special Terms**: Rich text editor for adding specific vendor terms or notes.

---

## 10. Local User Accounts for Workflow Testing

To perform end-to-end integration testing of the 4-step approval process, the following test accounts are configured in the local development environment:

| User Account Name | Email ID | Assigned Role | Access Level |
| :--- | :--- | :--- | :--- |
| **PO Generator User** | `po_generator@sarveksha.com` | PO Generator | Create PO, Edit Drafts, Final Print |
| **PO Verifier User** | `po_verifier@sarveksha.com` | PO Verifier | Verify PO, Direct Edit, Comment & Return |
| **PO Approver User** | `po_approver@sarveksha.com` | PO Approver | Approve PO, Commercial Edit, Sign-off |

---

## 11. Role-Based Access Control (RBAC) & Permission Matrix

### User Account Allocation
- **System Administrators (1–2 users)**: Full system configuration, role assignment, and schema management (`admin@sarveksha.com`, `tech_admin@sarveksha.com`).
- **Procurement Managers (1–2 users)**: Overrule workflows, review executive reports, and audit transactions (`procurement_manager@sarveksha.com`, `manager@sarveksha.com`).

### Role Permission Matrix

| Role Name | Create PO | Edit Draft | Verify Stage | Approve Stage | Submit / Print | Cancel PO |
| :--- | :---c: | :---c: | :---c: | :---c: | :---c: | :---c: |
| **PO Generator** | ✅ | ✅ | ❌ | ❌ | ✅ *(Final Stage)* | ❌ |
| **PO Verifier** | ❌ | ✅ *(Verify)* | ✅ | ❌ | ❌ | ❌ |
| **PO Approver** | ❌ | ✅ *(Approve)* | ❌ | ✅ | ❌ | ❌ |
| **Procurement Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **System Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 12. Standard Terms & Conditions Library Catalog

The system pre-configures a standard library of reusable Purchase Order clauses. Users select pre-defined templates or assemble custom clauses.

### Standard PO Clauses Library

- **Clause 1: Payment Terms & Schedule**
  > "Payment shall be released as per the agreed schedule: 30% advance upon PO acceptance and balance 70% against submission of original shipping documents (Bill of Lading, Commercial Invoice, Packing List, Certificate of Origin)."
- **Clause 2: Inspection & Quality Assurance**
  > "Goods are subject to pre-dispatch inspection by Sarveksha's authorized inspector or third-party agency. Vendor must notify Sarveksha at least 7 days prior to inspection readiness."
- **Clause 3: Delivery & Liquidated Damages (LD)**
  > "Time is of the essence. Delayed delivery shall attract liquidated damages at the rate of 0.5% of PO value per week of delay, subject to a maximum cap of 5% of total PO value."
- **Clause 4: Warranty & Performance Guarantee**
  > "Vendor guarantees that all equipment supplied is new, unused, and free from manufacturing defects for a period of 12 months from installation or 18 months from shipment date, whichever is earlier."
- **Clause 5: Packaging & Export Standards**
  > "All materials must be packaged in export-grade, seaworthy wooden crates with proper moisture protection, ISPM-15 fumigation compliance, and clear container shipping marks."
- **Clause 6: Force Majeure**
  > "Neither party shall be liable for failure or delay in performing obligations if such failure arises from acts of God, war, riot, embargoes, or government order beyond reasonable control."
- **Clause 7: Governing Law & Dispute Resolution**
  > "This Purchase Order shall be governed by and construed in accordance with the laws of India. Any disputes arising hereunder shall be subject to the exclusive jurisdiction of the courts in Ahmedabad, Gujarat."

---

## 13. Summary of Schema Fields to be Added/Updated

The following custom fields enhance the `Vendor Purchase Order` DocType schema:

| Field Name | Type | Options / Values | Description |
| :--- | :--- | :--- | :--- |
| `port` | Select / Link | Dropdown of configured ports | Replaces plain data field with standard port list |
| `shipment_type` | Select | 16 Expanded Options | Includes general cargo and 10 container types |
| `is_lut_applicable` | Check | `0` or `1` | SRI India LUT certificate toggle (0.1% GST) |
| `company_gstin` | Data | Read-only | Fetched from selected Company |
| `company_pan` | Data | Read-only | Fetched from selected Company |
| `workflow_stage` | Select | Draft, Verification, Approval, Printed | Tracks workflow state |
| `verification_remarks` | Small Text | Free text | Verifier comments on return |
| `approval_remarks` | Small Text | Free text | Approver comments on return |
| `correction_history` | HTML | Read-only | Chronological log of modifications made during review |
| `standard_terms` | Link | `Terms and Conditions` | Predefined T&C template selection |
| `custom_terms` | Text Editor | Rich text | PO-specific additional clauses |

---

## 14. Company Header, Tax Information & Legal Display Logic

### 14.1 Company Header GSTIN Display Instructions
To ensure strict statutory compliance, every official Purchase Order print format and document view must explicitly render the issuing company's GSTIN (Goods and Services Tax Identification Number) within the legal letterhead/header block.

### Technical Implementation Guidelines
1. **Schema Binding & Auto-Fetch**:
   - Add read-only field `company_gstin` on the `Vendor Purchase Order` DocType.
   - On selection or change of company, execute a client-side and server-side hook (`fetch_from = company.gst_no` or `company.tax_id`) to automatically fetch and store the active GSTIN into `doc.company_gstin`.
   - Store `company_pan` similarly derived from the primary tax record (`Company.pan` or the first 10 characters of `company_gstin`).
2. **Print & View Rendering**:
   - The header of `vendor_purchase_order_format.html` automatically displays `GSTIN: {{ doc.company_gstin }}` and `PAN: {{ doc.company_pan }}` alongside company registration details.
