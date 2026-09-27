# New Process: Automated Employee Onboarding Workflow

## Overview
Onboarding is initiated automatically the moment a hiring manager marks an
offer as "Accepted" in the Applicant Tracking System (ATS). A single
onboarding workflow engine orchestrates HR, IT, and Finance tasks in
parallel with a shared status dashboard.

## Steps
1. Hiring manager marks the offer as Accepted in the ATS. This automatically
   creates an employee record in the HRIS via API integration, no manual
   re-entry.
2. The workflow engine automatically triggers three parallel tracks the same
   day:
   - **HR track:** system-generated digital welcome packet, e-signature tax
     forms (W-4, I-9) and benefits enrollment sent to the employee's
     personal email, due before day one.
   - **IT track:** automated ticket created in the IT provisioning system
     with role-based access templates; laptop shipped and accounts
     provisioned within 2 business days, tracked to completion in the
     dashboard.
   - **Finance track:** payroll setup record created automatically from the
     HRIS entry; no manual form walked to Finance.
3. Employee completes all forms digitally via e-signature before their start
   date; digital forms are stored directly in the document management
   system (no physical filing, no re-keying).
4. Compliance training is auto-assigned in the Learning Management System
   (LMS) with due dates and automated reminders; completion is tracked and
   reportable for audit purposes.
5. First-week meetings and shadowing sessions are auto-scheduled based on a
   role-based onboarding template and synced to calendars; the hiring
   manager can customize the template per new hire.
6. HR, IT, Finance, and the hiring manager all see the same real-time
   onboarding status dashboard, eliminating status-check emails.
7. Any exceptions (e.g., missing I-9 documentation) automatically escalate
   to the responsible party via the workflow engine rather than relying on
   someone noticing.

## Expected Outcomes
- Time-to-productive (offer acceptance to full system access) reduced from
  5-10 business days to 1-2 business days.
- Elimination of paper forms and physical filing.
- Full audit trail of compliance training completion.
- Single shared source of truth for onboarding status across HR, IT,
  Finance, and hiring managers.
