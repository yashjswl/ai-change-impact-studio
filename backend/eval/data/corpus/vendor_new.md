# New Process: Vendor Portal Onboarding

## Overview
Vendors are onboarded through a self-service Vendor Portal. The portal replaces
the email chain and the Vendor Master workbook, and it creates the supplier record
in the ERP system directly through an API. Procurement reviews only the vendors
that the portal flags as higher risk.

## Steps
1. The requesting team raises a request in the Vendor Portal and picks the
   category of goods or services.
2. The vendor receives an invitation link and completes the onboarding form
   online. Tax documents and the bank letter are uploaded in the same form.
3. Sanctions screening runs automatically through ComplyCheck at the moment of
   submission, and every active vendor is screened again each night.
4. The bank account is verified with a micro-deposit test. The portal sends two
   small deposits and the vendor confirms the amounts, which normally takes
   2 days.
5. The portal assigns a risk tier based on expected annual spend and the type of
   data the vendor will handle.
6. When the tier requirements are met and screening is clean, the portal creates
   the vendor record in the ERP system automatically.

## Risk Tiers
- Tier 1 covers annual spend over $250,000. These vendors complete a security
  questionnaire and the contract goes through legal review.
- Tier 2 covers annual spend from $25,000 to $250,000. These vendors complete a
  shorter questionnaire.
- Tier 3 covers annual spend under $25,000. Tier 3 vendors follow a fast path and
  are approved automatically when sanctions screening is clean.

## Contracts and Re-validation
Signed contracts are stored in the contract repository, which sends renewal alerts
to the contract owner 90 days before expiry. Every vendor is re-validated each
12 months, and the portal sends automated reminders to vendors whose documents
are about to expire.

## Duplicate Prevention
The portal checks the tax ID and the bank account number against existing records
at submission. A match blocks the request and points the requester to the
existing vendor, which addresses the duplicate records found in the last audit.

## Expected Outcomes
- Onboarding time falls from 15 to 20 business days to 3 business days for Tier 3
  and about 10 business days for Tier 1.
- Duplicate vendor records are blocked at the point of entry.
- Requesters can see the status of every request in the portal.
