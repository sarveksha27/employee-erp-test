# 🏆 The Ultimate Boss Test Guide (Updated with GST Engine)

I have updated the test guide to reflect our newly built **Professional Indian GST Calculation Engine** (CGST/SGST/IGST auto-determination, Taxable Value, GST % fetching, and Balance Due calculation). 

Follow these exact steps to walk through the entire system like your boss or QA lead!

---

## Phase 1: The Core Transaction & GST Engine

1. **Start Fresh**: Go to the **Vendor Purchase Order** list and click **Add Vendor Purchase Order**.
2. **Test 1 - Company & Port Auto-Fetch**: 
   - Under the "Company" field, select **Sarveksha Realty and Inframine LLP**.
   - **Look at:** `Default Port` just below it. It should instantly populate as **Mundra, JNPT**.
   - **Behind the scenes:** Company GSTIN (`27AAFFS2131J1ZI` - State Code `27`, Maharashtra) is loaded for tax calculations.
3. **Test 2 - Vendor & Master Data Fetch**:
   - Under "Vendor Details", select **Bissa Engg.** in the Vendor field.
   - **Look at:** `Vendor GSTIN`, `Vendor PAN`, `Vendor Bank`, `Vendor Account No.`, and `IFSC Code`. 
   - **What to expect:** These will all auto-populate with Bissa Engg's actual stored data!
4. **Test 3 - Equipment & GST Rate Fetch**:
   - In "Equipment Details", select **EQ-03281** (or search **Parts and accessories**).
   - **Look at:** `Equipment Name`, `HSN Code`, `Brand`, `Manufacturer`, `Unit of Measure`, `Country of Origin`, and `Specification`.
   - **GST Rate:** `GST %` under Pricing & Charges will automatically fetch as **18%** from the Equipment master!
5. **Test 4 - Pricing & The Automated GST Calculation Engine**:
   - Scroll down to "Pricing & Charges".
   - Enter **Unit Rate**: `500,000`
   - Enter **Quantity**: `2`
   - Enter **Discount %**: `5`
   - **Look at Taxable Value:** It will automatically calculate `(500,000 × 2) - 5% = 950,000`.
   - **Look at GST Type & Tax Breakdown:**
     - The engine compares the state code of Company (`27`) and Vendor.
     - If inter-state (different state): **IGST Amount** will automatically show **171,000** (18% of 950,000).
     - If intra-state (same state): **CGST Amount** (`85,500`) and **SGST Amount** (`85,500`) will display separately!
   - **Total Tax Amount:** Automatically sums up to **171,000**.
   - **Grand Total:** Automatically calculates `950,000 (Taxable Value) + 171,000 (Tax) = 1,121,000`.

## Phase 2: The Final Logistics & Payment Info (What to fill in)

Many fields in this section are meant for later stages of the supply chain, but here is exactly what you should fill in for the Boss Test:

1. **References & Logistics**:
   - **Quotation Ref**: Type `QT-2026-001`
   - **Quotation Date**: Select today's date
   - **Expected Delivery Date**: Select a date next week
   - **Shipment Type**: Select `Road` (or Sea)
   - *(You can leave PI Number, PI Date, Delivery Location, Warehouse, and Container Number blank for now).*
   - **Port**: This should already say `Mumbai, Mundra`!

2. **Shipping Documents**:
   - **LEAVE ALL BLANK**. These are file attachment fields used by the logistics team *after* the goods are dispatched.

3. **Payment Tracking**:
   - **Payment Terms**: Type `20% Advance, balance against delivery`
   - **Advance %**: Type `20`
   - **Look at Advance Amount:** Automatically calculates **224,200** (20% of 1,121,000).
   - **Look at Balance Due:** Automatically calculates **896,800** (`Grand Total - Advance Amount`).
   - *(Leave Second Payment, Final Payment, and Company Bank blank).*

4. **Approval & Sign-off**:
   - **Prepared By**: Select your name (Administrator).
   - *(Leave Verified By, Approved By, Signatory, and Remarks blank for now).*

## Phase 3: The Final Deliverable (Print Format)

1. **Submit the PO**: In the top right corner, click the blue **Submit** button and click **Yes** to confirm.
2. **Click Print PO**: Click the **Print PO** button that appears near the top actions menu (or the print icon).
3. **Select Format**: Make sure **Vendor Purchase Order Format** is selected.
4. **Verification**:
   - **Header**: Shows Company logo/name, PO Number, Date, Port of Shipment.
   - **Vendor Info**: Displays Vendor Name, GSTIN, PAN, and Bank Details clearly.
   - **Item Table**: Displays Equipment Name, HSN Code, Specs, Brand, Qty, Rate, Discount, Taxable Value, and Total.
   - **Tax Summary**: Shows exact CGST/SGST or IGST breakdown.
   - **Footer**: Displays Payment Terms, Advance Paid, Balance Due, and Authorized Signatory block.

If all steps pass, your end-to-end procurement and GST engine workflow is 100% complete and ready for presentation!
