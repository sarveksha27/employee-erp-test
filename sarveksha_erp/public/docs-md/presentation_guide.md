# Presentation Guide: Vendor Payment Tracking Setup
**Meeting Date:** Saturday, 18th July
**Audience:** Boss / Management Team
**Objective:** Showcase the foundational Company, Fiscal Year, and Vendor Management configurations on the ERPNext platform.

---

## 💡 Pre-Meeting Preparation
Before sharing your screen, ensure you have the ERP open in your browser:
**URL:** `http://development.localhost:8000/app`
*Tip: Keep this guide open on a second monitor or printed out so you can reference the technical talking points.*

---

## Step 1: Technical Foundation Overview
**What to say:**
> "Good morning. Before diving into the screens, I'd like to give a brief technical overview of how we've laid the groundwork. As requested, we are currently running on a local development environment (Ubuntu 24.04) using Frappe Bench. Instead of heavily modifying core ERPNext files—which causes issues during future upgrades—we've built a custom Frappe application named `sarveksha_erp`. This app cleanly injects all our custom configurations, doctypes, and workspaces into the system. We will handle the containerization (Docker) phase later as discussed."

---

## Step 2: Showcasing the Company Structure
**Action:** Press `Ctrl + K` (or `Cmd + K` on Mac), type **Company List**, and hit Enter.

**What to showcase:**
Point out that the system is fully configured for a **Multi-Company Architecture**. You have successfully isolated all 9 entities as completely independent companies.

**The Details to Highlight:**
1.  **Sarveksha Realty and Inframine LLP** (India / INR) - *We set this as the Global Default Company.*
2.  **Sarveksha BSTP SAS** (Guinea / GNF)
3.  **Sarveksha Mining SARL** (Cameroon / XAF)
4.  **Sarveksha Botswana Proprietary Limited** (Botswana / BWP)
5.  **Odhav Holdings** (Sierra Leone / SLE)
6.  **Sarveksha SL Limited** (Sierra Leone / SLE)
7.  **Baani Minerals** (Sierra Leone / SLE)
8.  **Globe Multitrade and Service LLC** (UAE / AED)

> [!WARNING]
> **Assumed Data to Mention:**
> "For *Globe Multitrade and Service LLC*, the specific jurisdiction wasn't mentioned in the initial message. Based on the 'LLC' suffix, we assumed **United Arab Emirates** and configured the default currency as **AED**. We can instantly update this if it's registered elsewhere."

**Technical Talking Point:**
> "We've utilized ERPNext's native multi-company architecture. This ensures that while all companies share the same database for centralized management, their ledgers, default currencies, and vendor transactions remain strictly compartmentalized."

---

## Step 3: Showcasing Fiscal Year Configurations
**Action:** Press `Ctrl + K`, type **Fiscal Year List**, and hit Enter.

**What to showcase:**
Explain that fiscal years are crucial for accounting compliance and have been tailored exactly to their regional requirements.

**The Details to Highlight:**
*   **India Setup:** Show `2025-2026` and `2026-2027` (Runs April 1st to March 31st). Click into one and show that *only* the Indian company is linked to it.
*   **International Setup:** Show `2025`, `2026`, and `2027` (Runs Jan 1st to Dec 31st). Explain that all African and UAE entities are strictly mapped to these calendar fiscal years.

**Technical Talking Point:**
> "ERPNext strictly validates fiscal year overlaps. To prevent the system from throwing validation errors when creating transactions across different regions, we programmatically mapped specific companies to their respective fiscal years in the database. This ensures a user in Sierra Leone can't accidentally post an entry using the Indian financial calendar."

---

## Step 4: Showcasing the Vendor Database
**Action:** On the left sidebar, click **Vendor Management**, then click **Vendors** (or Suppliers).

**What to showcase:**
Show that the exact dataset provided (`VendorList-sarveksha.xlsx`) has been successfully migrated into the ERP.

**The Details to Highlight:**
*   Point out that there are exactly **20 live vendors** in the system.
*   Click on a vendor (e.g., *CruxWeld* or *Energy Compressor*).
*   Show that we captured granular details: PAN, GSTIN, Bank Name, Bank Branch, Account No, IFSC, and Contact Details.

**Technical Talking Point:**
> "Instead of dumping all vendors into a single list, we've structured them using `Supplier Groups` (e.g., Mining & Resources, Equipment & Machinery, Logistics). This categorization will allow us to run highly detailed expense reports by sector later on. All 20 vendors from the dataset are securely loaded with their banking and tax IDs."

---

## Step 5: The "Independent Company" Custom Flow
**Action:** Click your **Profile Icon** (top right) -> **My Settings** (or User Profile). Then go back to a **Supplier** record.

**What to showcase:**
Address the boss's specific requirement regarding the custom business flows for independent companies.

**The Details to Highlight:**
1.  **On the User Profile:** Show the **"Enable Independent Company Flow"** checkbox. Explain that this allows individual employees to toggle their portal view between standard ERPNext logic and the custom Vendor portal logic.
2.  **On the Vendor (Supplier) Form:** Show the **"Independent Company"** checkbox. This flags specific vendors that don't follow standard business flows.

**Technical Talking Point:**
> "To handle the 'Independent Companies' requirement, we didn't want to hardcode logic that restricts the whole system. Instead, we injected Custom Fields at both the `User` level and the `Supplier` level. This creates a matrix: the system knows *who* the user is, and *what* type of vendor they are dealing with, allowing us to dynamically route them to the custom vendor portal or the standard ERP flow on the fly."

---

## Step 6: The Vendor Management Dashboard
**Action:** Click **Vendor Management** on the main left sidebar.

**What to showcase:**
Show the dedicated workspace built specifically for this module.

**The Details to Highlight:**
*   The workspace sits at the top level, right alongside standard modules like CRM or Accounting.
*   It provides direct, clean access to **Vendor Payments**, **Vendors**, and **Companies**.

**Technical Talking Point:**
> "Frappe version 16 has very strict rules about how sidebars and workspaces render. We built a custom `Workspace Sidebar` schema that natively hooks into the Vue.js frontend. This guarantees that our custom Vendor Payment tracking module feels and behaves exactly like a core, out-of-the-box ERPNext feature."

---

## Step 7: Wrapping Up & Next Steps
**What to say:**
> "To summarize, the core infrastructure—Companies, Fiscal rules, Vendor data, and the Custom Flow architecture—is fully implemented and running locally. 
> 
> Looking at the roadmap you provided, our immediate next steps are:
> 1. Configuring the specific **GST and TDS rules** for the Indian entity.
> 2. Expanding the **Vendor Payment Tracking** workflows (approvals, statuses).
> 3. Finalizing the **Containerization (Docker)** for staging/production deployment.
> 
> Are there any specific vendor workflows you'd like us to focus on next?"
