# Strategic Goals — Order Platform Modernization

## Background

The Order Platform (internally "Legacy Order System") has run on the same
architecture since 2015. The board has approved a modernization initiative
for FY26.

## Drivers

- **D1 — Rising operational cost.** The current hosting footprint costs
  40% more per transaction than comparable competitors.
- **D2 — Compliance pressure.** PCI-DSS 4.0 requires payment data isolation
  that the current monolithic payment flow does not support.

## Goals

- **G1 — Reduce cost-per-transaction by 25% within 18 months.**
- **G2 — Achieve PCI-DSS 4.0 compliance for the payment flow by Q3.**

## Principles

- **P1 — Payment processing must be isolated from order management.**
  Rationale: directly supports G2 and limits PCI scope.

## Constraints

- **C1 — No downtime migrations.** The platform processes orders 24/7;
  any migration must be zero-downtime.

## Stakeholders

- **Head of Engineering** — sponsors the modernization initiative.
- **Compliance Officer** — owns the PCI-DSS 4.0 deadline (G2).
