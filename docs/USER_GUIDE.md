# Sarveksha ERP — Complete End-User Guide & Business Manual

Welcome to the **Sarveksha ERP User Guide**. This manual is written in plain, non-technical language to explain how our procurement, inter-company ordering, and billing processes work, what every button and field does, and why each piece of information is required.

---

## 1. The Big Picture: How Our Business Works

Sarveksha operates a global group of companies:
- **Sarveksha Realty and Inframine LLP (SRI)** is our parent entity based in Navi Mumbai, India.
- We have several overseas mining and trading subsidiaries (referred to as **Child Companies**), including:
  - **Odhav Holdings** (Sierra Leone)
  - **Sarveksha SL Limited** (Sierra Leone)
  - **Baani Minerals** (Sierra Leone)
  - **Sarveksha BSTP SAS** (Guinea)
  - **Sarveksha Mining SARL** (Cameroon)
  - **Sarveksha Botswana Proprietary Limited** (Botswana)
  - **Globe Multitrade and Service LLC** (UAE)

### Why Do We Have Two Types of Purchase Orders?

1. **Vendor Purchase Order (External PO)**:
   - Used when a company directly buys equipment, tools, or spare parts from an independent third-party vendor (e.g., buying trucks from Tata Motors or compressors from Energy Compressor).
   - In India, this attracts Indian GST (CGST + SGST or IGST).
   - For an overseas child company, it has 0% GST because foreign companies do not pay Indian domestic taxes.

2. **Internal Purchase Order (Child Company -> SRI)**:
   - When an overseas child company (such as Odhav Holdings in Sierra Leone) needs specialized machinery or lab chemicals manufactured or procured in India, it cannot easily deal directly with small Indian manufacturers.
   - Therefore, the child company issues an **Internal PO** to **SRI** in India.
   - SRI acts as the global procurement, logistics, and export hub.
   - SRI then purchases the goods, handles export documentation, freight, and insurance, and issues a **Proforma Invoice (PI)** to the child company with a regulated service margin (between 5% and 30%).

---

## 2. Who Does What: User Roles & Responsibilities

To prevent mistakes, fraud, or unverified spending, the system divides responsibilities between four distinct roles:

1. **PO Generator (`po_generator@sarveksha.com`)**:
   - Creates new draft Purchase Orders.
   - Selects equipment, specifies quantities, enters negotiated rates, and uploads vendor quotations.
   - Submits the PO for verification.
   - *Cannot verify or approve their own PO.*

2. **PO Verifier (`po_verifier@sarveksha.com`)**:
   - Reviews technical specifications, model numbers, delivery schedules, and verifies that at least one competitive vendor quotation is attached.
   - If everything is accurate, marks the PO as **Verified**.
   - If changes are needed, returns the PO to the Generator with remarks.
   - *Cannot create new POs and cannot give final financial sign-off.*

3. **PO Approver (`po_approver@sarveksha.com`)**:
   - The senior commercial/executive authority.
   - Reviews pricing, payment terms, and margins.
   - Clicks **Approve**. Once approved, the document is legally locked, an official Reference Number (e.g., `SRIPO-2026-0042`) is generated, and the Approver's digital signature is placed on the document.
   - *Cannot create new POs.*

4. **Administrator (`Administrator`)**:
   - IT/management oversight for master data setup and system maintenance.

> [!NOTE]
> The previous "Procurement Manager" approval bottleneck has been removed. Authorized users (Generators, Verifiers, and Approvers) can now manage payment terms and advance payment percentages directly within their workflow.

---

## 3. Detailed Guide: Raising a Purchase Order (Step-by-Step)

Navigate to **Buying** -> **Vendor Purchase Order** -> Click **+ Add Vendor Purchase Order**.

### Section A: Header & General Information

- **PO Type**:
  - `Vendor PO`: Choose this when ordering from an external 3rd-party vendor.
  - `Internal PO`: Choose this when an overseas child company is placing an order with SRI.
- **PO Date**: The official booking date of the order. Defaults to today's date.
- **Company**:
  - Select which Sarveksha group company is issuing this purchase order.
  - *Important Logic*: If you select an overseas child company (like *Odhav Holdings* or *Sarveksha SL Limited*), the system automatically strips Indian GST and sets all taxes to zero.
- **Vendor / Supplier**:
  - For a `Vendor PO`, select the third-party supplier (e.g., *Action Construction Equipment*).
  - For an `Internal PO`, the system requires you to select **Sarveksha Realty and Inframine LLP**.
- **Currency**: Currency of the transaction (e.g., `USD`, `INR`, `EUR`).

### Section B: Quotation Governance & Vendor Quotes

- **Why is this required?**: To ensure corporate transparency, company policy requires evidence of vendor pricing before an order leaves Draft status.
- **Quotation Requirement**:
  - You must enter at least **1 valid vendor quotation** in the quotations table.
- **Upload Quotation File**:
  - Inside the Quotations table, you will see a prominent button: **Upload Quotation File**.
  - Click this button to attach the vendor's PDF quotation.
  - *Tip*: Any quotation PDF you attach here is automatically stitched into the final downloadable PO PDF so that auditing teams have all documents in a single file!

### Section C: Equipment & Line Items Table

Click **Add Row** in the **Equipment Line Items** table:

- **Equipment**: Select the equipment from our catalog (e.g., `EQ-00052`). The system automatically fetches the standard description, manufacturer, brand, and 8-digit HSN code.
- **Quantity**: How many units are being ordered.
- **Unit**: Unit of measurement (e.g., `Nos`, `Sets`, `Kg`, `Mtr`).
- **Rate**: The unit purchase price in the selected currency.
- **Discount (%)**: Any negotiated percentage discount off the list price.
- **Taxable Amount**: Automatically calculated as `(Quantity × Rate) - Discount`.
- **GST Rate (%)**:
  - For Indian orders, defaults to the equipment's standard GST slab (e.g., 18%).
  - For overseas Child Company orders, this is automatically forced to **0%**.
- **Specification**: Enter any custom technical specifications, color codes, motor ratings, or engineering tolerances.

### Section D: Logistics & Incoterms

- **Port of Loading**: The departure seaport or airport (e.g., `Mundra Port, India` or `Nhava Sheva`).
- **Port of Discharge**: The destination arrival port (e.g., `Freetown, Sierra Leone`, `Conakry, Guinea`, or `Douala, Cameroon`).
- **Shipment Type**:
  - Options: `Containerized`, `Flat Rack`, `Oversized (ODC)`, `Air Freight`, or `Break Bulk`.
  - If you select `Containerized`, a sub-dropdown appears allowing you to specify `20 GP`, `40 GP`, `40 HQ`, or `Shipper Owned Container (SOC)`.
- **Logistics Charges**:
  - `Freight Charges`: Cost of ocean/air shipping.
  - `Insurance Charges`: Marine insurance coverage.
  - `Packaging Charges`: Crating, seaworthy palletization, or fumigation.
  - `Other Charges`: Port handling, terminal charges, or documentation fees.

### Section E: Payment Terms & Advance Tracking

- **Payment Terms Template**: Standard credit arrangements (e.g., *100% Advance*, *30% Advance + 70% against BL*, or *30 Days Credit*).
- **Payment Status**:
  - Options: `Pending`, `Advance Paid`, `Partially Paid`, `Fully Paid`.
- **Advance Percentage (%)**: Percentage required prior to shipment (e.g., `25%`).
- **Advance Amount**: Automatically calculated as `Grand Total × (Advance % / 100)`.

---

## 4. Generating a Proforma Invoice (PI) from an Internal PO

When an overseas child company issues an Internal PO to SRI, SRI must issue an official **Proforma Invoice (PI)** back to the child company so that the child company's local bank can open a Letter of Credit (LC) or wire foreign currency.

### Step 1: Open the Approved Internal PO
- Open the Internal PO in the system.
- Ensure the PO Type is set to **Internal PO**.

### Step 2: Click "Generate PI"
- At the top of the form, click the **Generate PI** action button.
- The system automatically creates a new **Proforma Invoice** document linked directly to this Internal PO.

### Step 3: Understand the Proforma Invoice Fields

- **Reference Constraint**: A Proforma Invoice can **only** be created from an Internal PO. The system strictly blocks creating a PI for regular external vendor POs.
- **Seller**: Automatically set to **Sarveksha Realty and Inframine LLP** with our full registered office address, GSTIN, PAN, and IEC (Import Export Code).
- **Buyer**: Automatically set to the Child Company (e.g., *Odhav Holdings*) with their foreign destination address.
- **SRI Margin (%)**:
  - SRI charges a regulated management and procurement margin.
  - **Strict Rule**: The margin must be between **5.0% and 30.0%**.
  - If you enter 3% or 35%, the system will display a validation error and refuse to save.
- **Logistics Entry (Manual)**:
  - **Important**: As per company accounting regulations, freight, insurance, and handling charges on the Proforma Invoice are **never** automatically copied from the PO.
  - You must enter the confirmed shipping quote under **Freight**, **Insurance**, and **Packaging Charges**.
- **Grand Total Calculation**:
  $$\text{Grand Total} = \text{Total Goods Value} + \text{Logistics} + \text{SRI Margin}$$
- **Banking Instructions**:
  - The PI automatically includes SRI's Indian banking coordinates (**RBL Bank Ltd**, Account `409002556124`, SWIFT: `RATNINBBXXX`) and our USD correspondent banking routing (**Standard Chartered Bank**, SWIFT: `SCBLUS33XXX`).

---

## 5. Downloading & Printing PDFs (With Full-Page Stationery Backgrounds)

When you click **Print PO** or **Print Proforma Invoice**:

1. **Full-Page Corporate Stationery Background**:
   - The system automatically loads your company's full-page high-resolution stationery template (containing both the company logo header and official footer).
   - The stationery is applied at 100% full-page A4 size without any cropping or squeezing.
   - All order tables, terms, and signature lines are printed directly over the stationery background with clean margin offsets.
2. **Uniform Page Sizing**:
   - All pages are rendered at standard **A4 paper size** (`210mm x 297mm`).
3. **Attachment Stitching for Purchase Orders**:
   - The system bundles the primary Purchase Order, all vendor quotation sheets, technical spec sheets, and inspection photos into **one single consolidated PDF file**.
   - Vendor quote attachments retain their authentic layout without any company letterhead stamped over them.
4. **Permanent Default Notify Party**:
   - The Notify Party on all Proforma Invoices is permanently defaulted to **Globe Multitrade & Service LLC** (Sharjah, UAE).

---

## 6. Frequently Asked Questions (FAQ)

**Q: Why can't I edit the vendor or equipment on an Approved PO?**
A: Once a PO is approved, it is a legally binding contract. If changes are needed, you must click **Cancel** or use **Amend** to create an amendment revision (which will receive a `-1` suffix).

**Q: Why is GST zero when I select Odhav Holdings or Baani Minerals?**
A: Foreign entities outside India do not possess Indian GST registrations. The system automatically zeros out GST components to comply with international cross-border accounting standards.

**Q: Can I create a Proforma Invoice directly without an Internal PO?**
A: No. Every Proforma Invoice must reference an active Internal PO raised by a child company to maintain an unbroken audit trail for customs and reserve bank audits.
