# New Process: SpendFlow Expense Reimbursement

## Overview
Expense claims are now submitted, checked, approved and paid inside the SpendFlow
mobile and web app. Accounts Payable (AP) no longer keys claims by hand and acts
only on exceptions. The goal is to cut the reimbursement cycle from 30 to 40 days
down to 3 to 5 days.

## Steps
1. The employee photographs each receipt in the SpendFlow app. Optical character
   recognition reads the amount, date and vendor and fills in the claim line.
2. Each line is checked against policy rules at submission. The meal limit is $75
   per person per day and the hotel cap is $220 per night. A line that breaks a
   rule is flagged and the employee must add a justification before submitting.
3. Claims under $200 with no policy flags are approved automatically with no
   manager involvement.
4. Claims from $200 to $2,000 go to the line manager, who has 3 business days to
   respond. If the manager does not respond, the claim escalates automatically to
   the department head.
5. Claims over $2,000 need approval from both the line manager and the finance
   controller.
6. Mileage is calculated from the GPS trace recorded by the app at $0.50 per
   mile. Employees no longer enter odometer readings.
7. Foreign currency expenses are converted at the daily rate from the central
   bank feed on the date of the transaction.
8. Approved claims are paid by direct deposit within 3 business days of final
   approval, instead of waiting for the monthly payroll run.

## Lost Receipts
An employee can attest to a lost receipt inside the app. The line is marked for
audit, and each employee is limited to 3 attested lost receipts per quarter.
Beyond that limit the claim is routed to the finance controller.

## Controls
- A duplicate detector screens every claim against the previous 12 months by
  amount, date and vendor before it reaches an approver.
- Finance samples 2% of auto-approved claims each month for manual review,
  replacing the old quarterly 5% sample.
- Every approval, edit and payment is logged with a timestamp and the identity of
  the person who acted.

## Employee Experience
Employees see the status of every claim in the app: submitted, flagged, awaiting
manager, approved or paid. The app sends a push notification at each change, so
there is no need to email AP. Paper receipts no longer have to be kept, because
the stored image is accepted as the record for the seven year retention period.

## Expected Outcomes
- Reimbursement time falls from 30 to 40 days to 3 to 5 days.
- Returned claims fall from about 12% to under 3%, because arithmetic and policy
  checks happen before submission.
- AP effort shifts from data entry to exception handling.
