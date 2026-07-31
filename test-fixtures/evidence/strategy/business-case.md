# Business Case — Order Platform Modernization

## Capability assessment

The organization currently has a **Payment Processing capability**,
delivered today by a single tightly-coupled service. Post-modernization,
this capability will be delivered by an isolated, independently
deployable service (see G2, P1 in strategic-goals.md).

The organization also has an established **Order Fulfillment capability**,
which coordinates order creation, payment authorization, and shipment
handoff.

## Resources

- **Engineering team** — 6 backend engineers allocated to the
  modernization initiative for FY26.
- **Cloud budget** — pre-approved incremental cloud spend of $40k for
  the migration period.

## Course of Action

- **Isolate Payment Processing.** Extract payment authorization into a
  dedicated service with its own datastore, satisfying constraint C1
  (no-downtime) via a strangler-fig migration pattern.
