# Sarveksha ERP — Requirements & Project Gap Analysis

This document provides a detailed audit of missing assets, unconfigured integrations, master data gaps, and operational requirements that must be resolved prior to full enterprise deployment.

---

## 1. Missing Corporate Branding & Letterhead Assets

While the print format engine supports company letterheads, several corporate entities are missing graphical letterheads in the system:

| Company Name | Jurisdiction | Current Letter Head Status | Required Asset |
|---|---|---|---|
| **Odhav Holdings** | Sierra Leone | **MISSING** | High-resolution SVG / PNG header image with registered office in Freetown, Sierra Leone. |
| **Globe Multitrade and Service LLC** | United Arab Emirates | **MISSING** | High-resolution SVG / PNG header image with Dubai / UAE corporate registration details. |
| **Sarveksha Realty and Inframine LLP** | India | Present (`letterhead_sri_india.png`) | Asset exists on disk. |
| **Sarveksha BSTP SAS** | Guinea | Present (`letterhead_guinea_bstp.jpeg`) | Asset exists on disk. |
| **Sarveksha SL Limited** | Sierra Leone | Present (`letterhead_sierra_leone.jpeg`) | Asset exists on disk. |
| **Baani Minerals** | Sierra Leone | Present (`letterhead_cameroon_baani.jpeg`) | Asset exists on disk. |
| **Sarveksha Mining SARL** | Cameroon | Present (`letterhead_cameroon_mining.jpeg`) | Asset exists on disk. |
| **Sarveksha Botswana Proprietary Limited** | Botswana | Present (`letterhead_botswana.jpeg`) | Asset exists on disk. |

> [!IMPORTANT]
> To resolve this gap:
> 1. Graphic design team must provide full-page A4 corporate stationery images (2480 x 3508 px at 300 DPI or vector PDF) for *Odhav Holdings* and *Globe Multitrade* containing both corporate header and official registered address footer.
> 2. Upload them to `/files/` and link them to the corresponding `Letter Head` records in ERPNext.

---

## 2. Master Data Incompleteness & Gaps

### 2.1. Customs House Agent (CHA) Master Data
- **Current State**: The `cha` field on `Vendor Purchase Order` links to `Supplier`. Currently, all 24 suppliers in the database are equipment manufacturers or logistics providers (e.g., *Tata Motors*, *Action Construction Equipment*, *Aavya Logistics*).
- **Gap**: There are no dedicated Customs House Agent entities registered.
- **Required**:
  - Register authorized Indian customs brokers (handling Mundra, Nhava Sheva, and Mumbai Air Cargo).
  - Add CHA registration numbers, port authorization licenses, and customs broker badges to the records.

### 2.2. Port Master Data Coverage
- **Current State**: The `Port` doctype contains only 7 ports: `Mumbai`, `Douala`, `Freetown`, `Durban`, `Conakry`, `JNPT`, and `Mundra`.
- **Gap**:
  - Critical transshipment hubs and regional African corridors are missing (e.g., *Tema (Ghana)*, *Lagos / Apapa (Nigeria)*, *Mombasa (Kenya)*, *Walvis Bay (Namibia)*, *Kolkata / Haldia (India)*, *Chennai (India)*).
- **Required**:
  - Populate comprehensive seaports, dry ports (ICDs), and international air cargo terminals with official UN/LOCODE identifiers.

### 2.3. Overseas Child Company Bank Master Data
- **Current State**: SRI's domestic and Nostro foreign exchange banking coordinates are hardcoded into `Proforma Invoice`.
- **Gap**:
  - Local operational bank accounts for the 8 overseas child companies are not configured in ERPNext `Bank Account`.
- **Required**:
  - Configure the receiving commercial bank accounts for each child company in their host countries (e.g., *Sierra Leone Commercial Bank*, *Ecobank Guinea*, *Standard Chartered Cameroon*, *First National Bank Botswana*).

---

## 3. Communication & Notification Gaps

### 3.1. Outgoing SMTP Email Infrastructure
- **Current State**: The database only contains legacy test email stubs (`_Test Email Account 1`, `Test`). There is **no active outgoing SMTP server** configured.
- **Impact**:
  - Automated transactional notifications cannot be dispatched.
  - When a PO moves to `Pending Verification`, the Verifier does not receive an alert.
  - When a PO is `Approved`, the vendor does not receive the automated PO PDF email.
- **Required**:
  - Configure a production SMTP relay (e.g., Google Workspace SMTP / Amazon SES / SendGrid) with TLS authentication for `erp@sarveksha.com`.
  - Create standardized Jinja email templates for PO dispatch and workflow state transitions.

---

## 4. Digital Signature & Legal Authorization

- **Current State**: The print formats place the logged-in Approver's name (`doc.signatory`) in the signature box.
- **Gap**:
  - There is no cryptographic digital signature (DSC) or verified PNG signature stamp of the authorized signatories.
- **Required**:
  - Store encrypted signature stamps for authorized directors in Frappe private files.
  - Render official corporate seal and authorized signatory stamps on final approved PO and PI print formats.
