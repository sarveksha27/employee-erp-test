# Sarveksha ERP — Architectural & Feature Suggestions

This document presents strategic and engineering recommendations for future sprints of the Sarveksha ERP system. These recommendations aim to elevate operational efficiency, financial automation, audit compliance, and system resilience.

---

## 1. Procurement & Workflow Enhancements

### 1.1. Milestone-Based Payment Schedules
- **Current State**: Payments are tracked using a flat `advance_percentage` and a simple `payment_status` dropdown (`Pending`, `Advance Paid`, `Partially Paid`, `Fully Paid`).
- **Proposed Improvement**:
  - Implement a dedicated child table `Purchase Order Payment Milestone`:
    - Milestone Type: `Advance`, `Against Inspection / FAT`, `Against Bill of Lading (BL)`, `On Port Clearance`, `Retention / Warranty`.
    - Due Date, Percentage, Due Amount, Payment Reference No., Payment Date, Bank Advice Attachment.
  - Automatically calculate cash flow forecasts for the treasury department.

### 1.2. Automated Quotation Comparison Matrix (OCR / AI Extraction)
- **Current State**: Users manually transcribe supplier quotation figures into the `Vendor Purchase Order Quotation` child table and manually upload the PDF.
- **Proposed Improvement**:
  - Introduce an automated document parsing or OCR worker (via Python `pdfplumber` or an LLM vision API):
    - When a user uploads a vendor quotation PDF, the parser auto-extracts the quote reference, quote date, total amount, line item prices, and validity.
    - Generates a side-by-side comparison modal highlighting the lowest bidder and delivery timelines.

### 1.3. Multi-Level Dynamic Approvals Based on Monetary Thresholds
- **Current State**: Any PO Approver can approve orders of any monetary value.
- **Proposed Improvement**:
  - Introduce threshold-based approval tiers:
    - Under \$25,000: Single Level Approval (Operations Approver).
    - \$25,000 to \$100,000: Dual Level Approval (Technical Director + Finance Approver).
    - Above \$100,000: Board / Executive Committee Sign-off.

---

## 2. Cross-Border & Customs Logistics Automation

### 2.1. Live Shipping Container & Vessel Tracking
- **Current State**: Container subtypes (`20 GP`, `40 HQ`, etc.) and ports of loading/discharge are static text and select fields.
- **Proposed Improvement**:
  - Integrate a maritime tracking API (e.g., *MarineTraffic*, *VesselFinder*, or *Searates*):
    - Track container numbers and Bills of Lading in real-time.
    - Display an interactive map inside the Purchase Order showing current vessel coordinates, estimated time of arrival (ETA), and transshipment port updates.

### 2.2. Automated Multi-Currency Exchange Rate Buffer
- **Current State**: Currencies are selected manually, but live conversion rates against INR for customs valuation and RBI outward remittances require manual entry.
- **Proposed Improvement**:
  - Integrate an automated daily currency feed (e.g., *Open Exchange Rates* or *European Central Bank API* via ERPNext Currency Exchange).
  - Include an automated FX buffer (e.g., +2% hedging buffer) on Proforma Invoices to shield SRI against foreign exchange volatility between PI issuance and wire settlement.

---

## 3. UI/UX & Printing Enhancements

### 3.1. Interactive Print Customizer & Visual Preview
- **Current State**: Print format rendering relies on server-side Jinja templates and `pdfkit`/`wkhtmltopdf`.
- **Proposed Improvement**:
  - Provide an in-browser live PDF preview using PDF.js embedded in the form sidebar.
  - Allow users to toggle optional sections on the fly (e.g., "Include Technical Specs", "Show Bank Details", "Include Manufacturer Certificates") before generating the final stitched PDF.

### 3.2. Mobile PWA & Push Notifications for Executive Approvals
- **Current State**: Approvers must log into the web desk from a laptop to review and approve POs.
- **Proposed Improvement**:
  - Implement Frappe Push Notifications / Telegram / WhatsApp Bot integration:
    - Send an interactive notification to the Approver's mobile phone: *"New PO SRIPO-0045 for $45,000 from Odhav Holdings awaiting your approval"*.
    - Allow 1-click approval or rejection with remarks directly from mobile.

---

## 4. Technical Architecture & DevOps Recommendations

### 4.1. Asynchronous PDF Merging via Redis Queue Worker
- **Current State**: Large stitched PDFs (e.g., 20-page high-resolution vendor catalogs) are stitched synchronously during the HTTP request lifecycle.
- **Proposed Improvement**:
  - Offload heavy PDF stitching jobs to a background Redis worker (`frappe.enqueue`).
  - When complete, notify the user via a system notification and store the generated PDF in the private files repository.

### 4.2. Automated Nightly S3 / Google Cloud Storage Backups
- **Current State**: Backups are stored on the local virtual machine filesystem.
- **Proposed Improvement**:
  - Configure ERPNext S3 Backup integration to automatically sync encrypted database snapshots and all private/public PDF attachments to an off-site cloud bucket daily.
