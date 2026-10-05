# New Process: PagerRelay Incident Management

## Overview
Incidents are detected, escalated and tracked in PagerRelay. Monitoring alerts
create incidents automatically, a rotating incident commander owns each serious
incident, and every SEV1 and SEV2 ends with a written postmortem. The change is
designed to cut acknowledgement and resolution times sharply.

## Severity Levels
- SEV1 is a customer-facing outage or data loss.
- SEV2 is degraded service where customers are affected but can still work.
- SEV3 is a minor issue with no customer impact.
Each level has a written definition so that two people classify the same issue the
same way.

## Steps
1. A monitoring alert creates an incident in PagerRelay with a proposed severity.
   There is no need to phone the service desk.
2. The on-call engineer is paged through the mobile app, then by SMS, then by
   phone call, until someone responds.
3. The on-call engineer must acknowledge within 5 minutes. If there is no
   acknowledgement, the page escalates automatically to the secondary on-call and
   then to the engineering manager.
4. For SEV1 and SEV2, PagerRelay opens a dedicated chat channel named after the
   incident and assigns an incident commander from a rotating roster. The commander
   coordinates the work and does not make the technical changes.
5. During a SEV1, the communications lead updates the public status page every
   30 minutes until the incident is resolved.
6. When the incident is resolved, the commander marks it closed in PagerRelay and
   confirms that monitoring has returned to normal.

## Postmortems
A blameless postmortem is required within 5 business days for every SEV1 and SEV2.
The postmortem uses a standard template stored in the engineering wiki and is
reviewed at the weekly reliability meeting. Action items are tracked in Jira with
a named owner and a due date.

## On-Call
On-call duty rotates weekly across the whole engineering team. Engineers receive an
on-call stipend of $350 per week, and the rota is published a month ahead.

## Targets
- Mean time to acknowledge under 5 minutes.
- Mean time to resolve a SEV1 under 1 hour.
- Every SEV1 and SEV2 postmortem completed within 5 business days.
