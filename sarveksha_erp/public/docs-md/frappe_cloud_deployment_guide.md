# Sarveksha ERP: Frappe Cloud Deployment Guide

Last reviewed: 2026-09-15

This document explains how to deploy the Sarveksha ERP / Vendor Management system to official Frappe Cloud with the least practical risk. It is written for teammates who may not deploy Frappe apps every day.

Important: Frappe Cloud pricing and UI screens can change. Before paying, re-check the official pages:

- Frappe Cloud pricing: https://frappe.io/cloud/pricing
- Shared hosting pricing: https://frappe.io/cloud/shared-hosting
- Server plans: https://frappe.io/cloud/servers
- Frappe Cloud docs: https://docs.frappe.io/cloud
- Restore and migrate site docs: https://docs.frappe.io/cloud/sites/migrate-an-existing-site
- Custom app docs: https://docs.frappe.io/cloud/benches/custom-app

## Current Project Facts

Local bench path:

```text
/workspace/development/frappe-bench
```

Current local site:

```text
development.localhost
```

Installed apps and versions currently verified locally:

```text
frappe        16.26.1 version-16
erpnext       16.26.2 version-16
sarveksha_erp 0.0.1   main
```

Custom app:

```text
sarveksha_erp
```

Current Git remote seen locally:

```text
https://github.com/manikkDev/employee-erp-test.git
```

Before paying for hosting, confirm this is the correct production repository. If this is only a test repository, create or switch to the correct private production repository first.

## Very Important Deployment Decision

There are two possible deployment styles.

### Option A: Fresh Production Site

Use this if the current local site contains test data, trial users, dummy passwords, experimental documents, or records that should not go live.

This means:

- Deploy the app code to Frappe Cloud.
- Create a fresh site.
- Install ERPNext and `sarveksha_erp`.
- Let fixtures/custom app setup create roles, workflows, print formats, custom doctypes, permissions, etc.
- Add only real production master data manually or by clean import.

This is usually the safest option.

### Option B: Migrate Existing Local Site

Use this only if the local database is already the exact production database you want online.

This means:

- Take a full backup of the local site.
- Restore that backup on Frappe Cloud.
- Keep the same documents, users, workflows, passwords, files, and private files.

This is risky if the local database contains test users, old passwords, dummy invoices, temporary files, or broken experiments.

Recommended for Sarveksha right now: choose Option A unless the whole team confirms that `development.localhost` is already production-clean.

## Pricing Summary

Prices below are from the official Frappe pages checked on 2026-09-15. Re-check before payment.

### Site Plans

Site plans are shared, compute-based plans for one site. They are good for quick starts and smaller setups.

Official shared hosting table currently shows:

| Monthly price | CPU time/day | Database | Storage |
|---:|---:|---:|---:|
| $5 / ₹410 | 0.5 hour | 0.2 GB | 2.5 GB |
| $10 / ₹820 | 1.0 hour | 0.5 GB | 5.0 GB |
| $25 / ₹2,050 | 2.0 hours | 1.0 GB | 25.0 GB |
| $38 / ₹3,075 | 3.0 hours | 1.5 GB | 37.5 GB |
| $50 / ₹4,100 | 4.0 hours | 2.0 GB | 50.0 GB |

Site plans include useful managed features such as automated backups, upgrades, monitoring, custom domain support, and offsite backups depending on plan/features.

### Shared Bench vs Private Bench

This matters for us.

Frappe Cloud explains that shared bench groups are managed by Frappe and are ideal for out-of-the-box apps. Private bench groups unlock deeper controls, custom app deployment, SSH access, and multiple environments.

Official comparison currently says:

| Bench type | Starting price | Suitable for us? | Why |
|---|---:|---|---|
| Shared bench | $5/mo | No, not for final deployment | Good for standard apps, but not enough for a custom app workflow. |
| Private bench | $25/mo | Yes | Needed for custom app deployment from GitHub and better control. |

Because `sarveksha_erp` is a custom app, do not assume the $5 shared plan is enough. Budget for at least the private bench/custom app capable path.

### Server Plans

Server plans provide a full virtual machine to host multiple sites and benches. Frappe Cloud pricing currently says server plans start around:

```text
$40 / mo
₹3,600 / mo
```

Server plans are better when:

- You need multiple sites.
- You need dedicated/shared VM resources.
- You need stronger isolation.
- You need predictable performance.
- You need easier scaling, snapshots, server analytics, or more control.

Official server examples vary a lot by cloud provider, region, CPU, RAM, and disk. The public server page includes AWS enterprise examples starting around $125/mo for small instances in some regions, and other providers/configurations may differ.

### Recommended 1-Month Trial Choice

For a one-month paid test of this custom app:

1. Choose a Frappe Cloud plan that supports a private bench/custom app deployment.
2. Start with the lowest private/custom-app-capable option, currently around $25/mo.
3. If database access is required for analytics or direct SQL tools, note that Frappe Cloud says database access is available for plans over $50/month.
4. Avoid dedicated AWS/OCI server plans for the first month unless this is mission-critical production immediately.

Recommended first month:

```text
Private bench / custom app capable plan, starting around $25/mo
```

Upgrade only if monitoring shows CPU, DB, storage, or performance limits.

## What To Prepare Before Spending Money

Do not start payment/deployment until this checklist is complete.

### Code Checklist

- Confirm the correct production GitHub repository.
- Confirm the correct branch to deploy, for example `main`.
- Confirm the repo is private or public according to company policy.
- Confirm Frappe Cloud GitHub app has access to the repository.
- Confirm the app has a valid `pyproject.toml`.
- Add Frappe version compatibility to `pyproject.toml` if Frappe Cloud requires it for custom app deployment.

Recommended addition if not already present:

```toml
[tool.bench.frappe-dependencies]
frappe = ">=16.0.0,<17.0.0"
```

- Commit and push all required app files.
- Do not rely on uncommitted local changes.
- Confirm fixtures are committed.
- Confirm custom doctypes are committed as JSON files.
- Confirm print formats are committed/exported.
- Confirm workflows, roles, custom permissions, and client scripts are exported as fixtures.

### Data Checklist

Decide clearly:

- Are we deploying a fresh production site?
- Or are we migrating the current local database?

If fresh production:

- Prepare real company details.
- Prepare real users and emails.
- Prepare real supplier/vendor data.
- Prepare real bank details.
- Prepare letterheads.
- Prepare roles and workflow assignment list.
- Do not copy test passwords into production unless this is only a temporary UAT site.

If migrating local site:

- Clean test documents.
- Remove dummy suppliers, invoices, purchase orders, files, and users.
- Reset user passwords.
- Confirm email accounts and API keys are valid.
- Confirm print formats work.
- Confirm PDF generation works.
- Confirm workflows work.

### Access Checklist

Before deployment, decide who owns each account:

- Frappe Cloud account owner.
- Billing/payment owner.
- GitHub repository owner.
- GitHub admin who can install the Frappe Cloud GitHub app.
- Production System Manager user.
- Backup/download responsible person.
- Domain/DNS responsible person.

Use company-controlled accounts, not only one developer's personal account.

### Domain Checklist

Decide the production URL before go-live:

```text
erp.sarveksha.com
```

or another final domain.

Prepare DNS access. Someone must be able to add/update records such as CNAME/A records as instructed by Frappe Cloud.

### Payment Checklist

Frappe Cloud currently supports:

- Card payment.
- Prepaid credits/wallet.

Before paying:

- Confirm plan price.
- Confirm whether taxes apply.
- Confirm whether trial credits apply.
- Confirm billing cycle.
- Confirm cancellation policy.
- Add payment method only from the official Frappe Cloud dashboard.

## Deployment Plan: Fresh Production Site

Use this if you do not want to migrate all local data.

### Step 1: Freeze Code For Deployment

1. Stop adding random changes.
2. Create a release branch or tag.

Example:

```bash
cd /workspace/development/frappe-bench/apps/sarveksha_erp
git status
git add .
git commit -m "Prepare Sarveksha ERP for Frappe Cloud deployment"
git tag v1.0.0-cloud-test
git push origin main --tags
```

If `git status` shows unrelated changes, review them before committing.

### Step 2: Verify App Locally

From the bench:

```bash
cd /workspace/development/frappe-bench
bench --site development.localhost migrate
bench --site development.localhost clear-cache
bench build
bench --site development.localhost list-apps
```

Then test locally:

- Login works.
- Vendor Purchase Order list opens.
- PO workflow works from generator to verifier to approver.
- Generate PI works.
- Print PO works.
- Print PI works.
- Roles and permissions work.
- No server errors in logs.

### Step 3: Create Frappe Cloud Account

1. Go to https://frappecloud.com or start from https://frappe.io/cloud.
2. Sign up using the company email.
3. Verify email.
4. Open Account Settings.
5. Add billing details.
6. Add card or prepaid credit only after the team confirms the plan.

### Step 4: Connect GitHub

1. In Frappe Cloud, connect GitHub.
2. Install/authorize the Frappe Cloud GitHub app.
3. Give access only to the required repository.
4. Confirm Frappe Cloud can see the `sarveksha_erp` repository.
5. Confirm branch is correct.

If the repo is private and Frappe Cloud cannot fetch it, deployment will fail.

### Step 5: Create Private Bench

1. Go to Frappe Cloud Dashboard.
2. Open Benches.
3. Create a new private bench.
4. Select Frappe version 16.
5. Select compatible ERPNext version 16.
6. Add custom app from GitHub:

```text
sarveksha_erp
```

7. Select branch:

```text
main
```

8. Start bench build/deploy.
9. Wait until build succeeds.

Do not create production site until the bench build is green.

### Step 6: Create Staging Site First

Create a staging/UAT site before production.

Example:

```text
sarveksha-uat.frappe.cloud
```

Install apps:

```text
frappe
erpnext
sarveksha_erp
```

Run installation/setup. The custom app has an `after_install` hook, so check installation logs carefully.

### Step 7: Test Staging

On staging:

1. Complete ERPNext setup wizard if required.
2. Login as Administrator.
3. Confirm Sarveksha ERP app appears.
4. Confirm custom doctypes exist:
   - Vendor Purchase Order
   - Proforma Invoice
   - Equipment
   - Port
5. Confirm roles exist:
   - PO Generator
   - PO Verifier
   - PO Approver
   - Procurement Manager
6. Confirm workflows exist.
7. Confirm print formats exist.
8. Create test users.
9. Assign roles.
10. Create one test Vendor Purchase Order.
11. Move it through the workflow.
12. Generate PI.
13. Print PO.
14. Print PI.
15. Download PDFs.
16. Check no 500 errors occur.

### Step 8: Fix Any Issues In Code

If staging fails:

1. Fix locally.
2. Test locally.
3. Commit changes.
4. Push to GitHub.
5. In Frappe Cloud bench, fetch/update app.
6. Deploy again.
7. Run migration if required.
8. Retest staging.

Do not patch production manually from SSH unless absolutely necessary. Changes must live in Git.

### Step 9: Create Production Site

After staging passes:

1. Create production site.
2. Use final naming.
3. Install the same apps.
4. Run setup.
5. Create production users.
6. Assign roles.
7. Configure company, suppliers, banks, letterheads, terms, email, and domain.

Suggested production site:

```text
sarveksha.frappe.cloud
```

Then later connect:

```text
erp.sarveksha.com
```

### Step 10: Configure Custom Domain

1. In Frappe Cloud, open the production site.
2. Go to domain settings/custom domains.
3. Add the domain, for example:

```text
erp.sarveksha.com
```

4. Frappe Cloud will show DNS instructions.
5. Add the DNS record at your DNS provider.
6. Wait for propagation.
7. Confirm SSL certificate is active.
8. Open the final URL in browser.

Do not switch users to the custom domain until SSL is active and login works.

### Step 11: Production Readiness Test

Run this exact test before declaring deployment complete:

1. Login as Administrator.
2. Create or verify production users.
3. Login as PO Generator.
4. Create Vendor Purchase Order.
5. Submit/send to next workflow step.
6. Login as PO Verifier.
7. Verify PO.
8. Login as PO Approver.
9. Approve PO.
10. Login as Procurement Manager or Admin.
11. Generate PI.
12. Print PO PDF.
13. Print PI PDF.
14. Check downloaded PDFs.
15. Confirm no server error.
16. Confirm emails if email sending is configured.
17. Confirm backups tab shows backups or trigger a manual backup.

## Deployment Plan: Migrate Existing Local Site

Use this only if local data is production-ready.

### Step 1: Take Backup Locally

From the local bench:

```bash
cd /workspace/development/frappe-bench
bench --site development.localhost backup --with-files
```

You should get these kinds of files:

```text
database.sql.gz
files.tar
private-files.tar
site_config_backup.json
```

Frappe Cloud docs say restore expects four backup files:

- Database backup
- Public files backup
- Private files backup
- Site config backup

Keep these files private. They may contain business data, files, secrets, and password encryption keys.

### Step 2: Confirm Encryption Key

The `site_config_backup.json` contains keys required to decrypt encrypted password fields. Do not lose it.

If the encryption key is missing or wrong, email account passwords/API secrets may fail after restore.

### Step 3: Create New Cloud Site

1. Create a site in Frappe Cloud.
2. Choose Frappe/ERPNext version matching local major version:

```text
version-16
```

3. Ensure the bench has the same apps:

```text
frappe
erpnext
sarveksha_erp
```

### Step 4: Restore Backup

If backup size is small enough:

1. Open site dashboard.
2. Go to Actions.
3. Choose Restore with files.
4. Upload database backup.
5. Upload public files backup.
6. Upload private files backup.
7. Upload site config backup.
8. Start restore.
9. Wait until site returns to Active.

If backup is large, use Frappe Cloud Restore CLI or `bench migrate-to`, as described in official Frappe Cloud docs.

### Step 5: Run Migration

After restore:

1. Open site dashboard.
2. Go to Migrations.
3. Trigger in-place migration if required.
4. Wait for success.

### Step 6: Post-Restore Checks

Check:

- Users can login.
- Existing passwords work.
- Email accounts work.
- File attachments open.
- Private files are accessible only to permitted users.
- PDF printing works.
- Workflows still work.
- Scheduled jobs are running.
- Backups are enabled.

## Required Production Users

Create/verify these users:

```text
admin@sarveksha.com
procurement_manager@sarveksha.com
po_approver@sarveksha.com
po_verifier@sarveksha.com
po_generator@sarveksha.com
```

Temporary test password used locally:

```text
admin@1234
```

Do not keep this password in production.

Production password rule:

- Set strong unique passwords.
- Force users to reset passwords.
- Enable 2FA if company policy requires it.
- Remove/disable any test users.

## Role Mapping

Expected role mapping:

| User | Role |
|---|---|
| `po_generator@sarveksha.com` | PO Generator |
| `po_verifier@sarveksha.com` | PO Verifier |
| `po_approver@sarveksha.com` | PO Approver |
| `procurement_manager@sarveksha.com` | Procurement Manager |
| `admin@sarveksha.com` | System Manager |

## PDF/Printing Checklist

Printing must be tested because Frappe uses server-side PDF generation.

Test:

- Print PO from an approved Vendor Purchase Order.
- Print PI from a generated Proforma Invoice.
- Open PDF in browser.
- Download PDF.
- Check letterhead.
- Check company details.
- Check bank details.
- Check item/equipment table.
- Check totals and currency.
- Check page breaks.

If PDF fails with `500`:

- Check Error Log.
- Check print format.
- Check missing fields.
- Check images/letterhead URLs.
- Check whether wkhtmltopdf can access the site URL.

## Backups And Rollback

Before go-live:

1. Trigger manual backup.
2. Download/confirm backup availability.
3. Confirm offsite backups are enabled.
4. Write down restore steps.

Frappe Cloud backup behavior from docs:

- Backups include database, public files, private files, and site config.
- Offsite backups are kept with daily/weekly/monthly/yearly rotation.
- Manual backups can be triggered from the Backups tab.

Rollback plan:

1. Stop users from entering new data.
2. Take a backup of current broken state.
3. Restore last known good backup.
4. Verify login and workflows.
5. Communicate status to team.

## Go-Live Checklist

Do not go live until every item is checked.

- Correct paid plan selected.
- Billing owner approved cost.
- GitHub repository confirmed.
- Production branch confirmed.
- Private bench/custom app deployment working.
- Staging tested.
- Production site created.
- Custom domain configured.
- SSL active.
- Backups verified.
- Admin user secured.
- Test passwords removed.
- Real users created.
- Roles assigned.
- Workflow tested end-to-end.
- PO print tested.
- PI print tested.
- Email sending tested if needed.
- Team knows support/contact process.
- Team knows how to pause/rollback.

## Suggested Team Responsibilities

| Area | Owner |
|---|---|
| Billing | Finance/Admin |
| Frappe Cloud account | Project lead |
| GitHub repository | Developer |
| DNS/domain | IT/Admin |
| App deployment | Developer |
| Functional testing | Procurement team |
| Workflow approval testing | PO Generator, Verifier, Approver, Procurement Manager |
| Backup verification | Developer/Admin |

## Final Recommendation

For the first month, do not overbuy.

Recommended path:

1. Use Frappe Cloud official hosting.
2. Use a private bench/custom-app-capable plan, currently starting around $25/month.
3. Create staging first.
4. Test all workflows and printing.
5. Only then create production.
6. Upgrade plan only if actual monitoring shows CPU, database, storage, or performance limits.

The cheapest $5 shared plan is attractive, but it is not the right final choice for this custom app unless Frappe Cloud explicitly confirms your custom app can be deployed there. For this project, plan for the private bench route.
