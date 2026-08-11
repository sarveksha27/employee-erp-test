# Sarveksha ERP — System Walkthrough Guide

## 📌 Executive Overview
Sarveksha ERP provides an end-to-end procurement and vendor management solution designed for industrial equipment purchasing across global operating entities (**India, Botswana, Cameroon, Guinea, and Sierra Leone**). 

This walkthrough outlines how users interact with the system—from creating a Purchase Order to item entry, multi-tier approvals, and generating branded purchase documents.

---

## 📑 Step-by-Step Operational Walkthrough

### 1. Order Initialization & Company Selection
- **Select Operating Entity**: Choose the Sarveksha company raising the order (e.g., *Sarveksha Botswana Proprietary Limited*).
  - **Automatic Letterhead Detection**: The system automatically detects and applies the appropriate company letterhead (e.g., *Botswana (Sarveksha Botswana)*). Users can also select an alternative letterhead from the visible dropdown if needed.
  - **Automatic Port Filtering**: Customs and delivery ports are automatically filtered to show options relevant to the selected company's region (e.g., *Gaborone Dry Port*, *Walvis Bay*).
  - **Tax & Address Auto-Fill**: Company GSTIN, PAN, and address details automatically populate on the document.
- **Select Vendor**: Choose the supplier. Vendor bank accounts, payment details, and registered addresses auto-populate instantly.

---

### 2. Fast Equipment Line Item Entry
- **Direct Input Fields**: Add equipment items directly on the main form screen without any confusing pop-up windows or dialogs.
- **Auto-Populating Details**: Select an **Equipment Code** (e.g., `EQ-03281`), and the system automatically fills:
  - Equipment Name & Model
  - Official HSN / SAC Code (for GST compliance)
  - Brand & Manufacturer Name
  - Standard Unit Rate & Applicable GST %
  - Technical Specifications
- **One-Click Item Addition**: Click **`+ Add Equipment to Table`** to insert the line item into the summary table. The system recalculates order totals, shows a confirmation message, and clears the input fields for the next item.
- **Clear Equipment Summary Table**: All added items appear in a clean table displaying item code, description, HSN code, brand, quantity, rate, GST, and total amounts.

---

### 3. Shipping, Logistics & Commercial Terms
- **Destination & Port**: Pick the receiving warehouse and delivery port.
- **Logistics Tracking**: Record shipment types, container numbers, and attach shipping documents (Commercial Invoice, Bill of Lading, Packing List, Certificate of Origin).
- **Payment Structure**: Define advance payment percentages, second installments, and final delivery payments. The system automatically calculates advance and balance amounts.
- **Terms & Conditions**: Select pre-defined standard terms or add custom agreement clauses.

---

### 4. Multi-Stage Approval & Audit Workflow
The procurement process follows a strict 3-stage security and audit flow:

1. **Draft Stage (PO Generator)**
   - Procurement team fills order details and submits the document. State changes to **Pending Verification**.
2. **Verification Stage (PO Verifier)**
   - Verifier audits equipment specs, HSN codes, and pricing.
   - Verifier enters official review comments.
   - Can either **Return to Generator** for revisions or **Verify & Forward** to Approver.
3. **Approval Stage (PO Approver / Manager)**
   - Management checks financial budgets and commercial terms.
   - Approver adds final authorization notes and clicks **Approve**.
- **Data Protection**: Audit notes can only be modified by the designated role during their respective stage. Approved orders are locked against unauthorized changes.

---

### 5. Branded Purchase Order Generation & Printing
- **One-Click Print**: Once approved, the **Print PO** button becomes active.
- **Professional Layout**: Generates a clean PDF document containing:
  - Official Company Letterhead Header & Logo
  - Document Naming Series & Dates
  - Complete Company and Vendor Details
  - Structured Equipment Table with HSN Codes & Technical Specs
  - Tax Breakdowns (CGST, SGST, IGST / International Rates)
  - Payment Terms, Remarks & Terms & Conditions
  - Signature & Authorization Blocks

---

## 🔄 Quick Visual Workflow Summary

```
 [ Select Company ]  ──> Auto-detects Letterhead & Regional Clearance Ports
         │
         ▼
 [ Equipment Entry ] ──> Select Equipment -> Auto-fill HSN & Specs -> Click "+ Add"
         │
         ▼
 [ Commercial Terms ]──> Set Payment Terms, Advance %, Delivery & Shipping Docs
         │
         ▼
 [ 3-Stage Audit ]   ──> Draft ──> Verified (Auditor) ──> Approved (Manager)
         │
         ▼
 [ Print Branded PO ]──> Generate PDF with Letterhead, HSN Codes & Signature Blocks
```
