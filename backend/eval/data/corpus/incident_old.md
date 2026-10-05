# Old Process: Phone-Tree Incident Response

## Overview
When a production system fails, the response depends on whoever notices first and
on a printed phone tree kept by the service desk. There is no tool that tracks the
incident from detection to resolution, and no fixed owner while it is being fixed.

## Steps
1. Anyone who notices an outage calls the service desk. Monitoring tools raise
   alarms on a wall display, but they do not create tickets.
2. The service desk agent logs a ticket by hand and classifies it as major or
   minor based on personal judgement, because there are no written severity
   definitions.
3. For a major incident, the agent follows the printed phone tree and calls the
   on-call engineer's mobile phone. If there is no answer after 10 minutes, the
   agent calls the next engineer on the list.
4. There is no incident commander. The engineers who join the call decide among
   themselves who leads the technical work.
5. Updates go out by email to the all-it distribution list. They are sent about
   every hour when someone remembers, and there is no public status page for
   customers.
6. When the problem is fixed, the engineer closes the ticket with a short
   free-text note describing the fix.

## Postmortems
A written postmortem is required only when an outage lasts longer than 8 hours.
The postmortem is written in a Word document and usually stays within the
engineering team. Most incidents under 8 hours are never reviewed, so the same
failures repeat.

## On-Call
Engineers on the on-call list receive no allowance and no formal rota. The same
few senior engineers answer most calls, which has led to burnout and two
resignations in the last year.

## Known Issues
- The mean time to acknowledge an incident is 38 minutes.
- The mean time to resolve an incident is 5.5 hours.
- Customers learn about outages from social media before they hear from the
  company.
- Action items from the few postmortems that are written are not tracked and
  are rarely completed.
