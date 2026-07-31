# J1 — Synthetic Demo Evidence Set

A small, deliberately simple fictional legacy system: the **Order
Platform** (`system_id = legacy-system`), an e-commerce order/payment
system being modernized. This is the fixture the whole team tests
against throughout Epics E–J. Everything in here is fictional and
minimal by design — the point is coverage of edge cases, not realism.

## Layout and which subagent reads what

| Folder | Read by | Contents |
|---|---|---|
| `evidence/motivation/` | `strategy-analyst` (E1) | Strategic goals, drivers, principles, constraints, stakeholders |
| `evidence/strategy/` | `strategy-analyst` (E1) | Capabilities, resources, course of action |
| `evidence/business/` | `business-analyst` (E2) | Process doc + one interview transcript |
| `evidence/code/` | `code-analyzer` (E3) | Two tiny services + a DB schema |
| `evidence/infra/` | `infra-analyzer` (E4) | One Terraform snippet + one CMDB export |
| `evidence/integration/` | `integration-mapper` (E5) | A lightweight integration/API description |

This matches the intake folder convention from the MVP task
descriptions (`/evidence/<source_type>/`).

## What each file is expected to yield

- **`motivation/strategic-goals.md`** — Stakeholder, Driver (×2), Goal
  (×2), Principle, Constraint.
- **`strategy/business-case.md`** — Capability (×2), Resource (×2),
  Course of Action.
- **`business/order-fulfillment-process.md`** — Business Actor, Business
  Role, Business Process, Business Service, Business Object.
- **`business/interview-transcript-ops-manager.txt`** — reinforces the
  Order Desk Clerk role and the manual-review pain point; low-confidence/
  "inferred" material is expected here since it's conversational, not a
  spec.
- **`code/payment-service/main.py`** — Application Component
  (PaymentService), Application Service (authorize_payment), Application
  Interface (PaymentInterface).
- **`code/order-service/main.py`** — Application Component
  (OrderService), Application Service (×2: order creation, order
  submission).
- **`code/schema.sql`** — Data Object (×2: Order, Payment Authorization
  Record).
- **`infra/main.tf`** — Node (×3: payment database, order API server,
  payment API server), System Software.
- **`infra/cmdb-export.csv`** — Node (×3, see intentional near-duplicate
  below), Technology Service implied by "Database Server" / "Application
  Server" asset types.
- **`integration/api-spec.yaml`** — one valid cross-component
  relationship, one intentionally invalid one (see below).

## Intentional edge case #1 — near-duplicate (for F1)

`infra/main.tf`'s `aws_db_instance.payment_database` and
`infra/cmdb-export.csv`'s `Payment-Database` row describe **the same
physical database** under two different naming conventions:

- Terraform: `payment_database` / `payment-database` (snake_case /
  hyphenated)
- CMDB: `Payment-Database` (Title-Case-with-hyphens)

Both should be extracted by `infra-analyzer` (E4) as a `Node` in the
technology layer. After normalization (lowercase, strip
whitespace/punctuation — see F1's `normalize_name`), both collapse to
`paymentdatabase`, so the reconciler should merge them into one element
retaining evidence from both files. This tests F1's DoD directly: "given
a sample set with at least one intentional near-duplicate, produces a
single merged element retaining evidence from both sources."

## Intentional edge case #2 — invalid reference (for E5 / F2)

`integration/api-spec.yaml` includes a second "integration" from
`OrderService` to `legacy-billing-service`. **`legacy-billing-service`
does not appear anywhere else in this evidence set** — not in `code/`,
not in `infra/`, not in `business/`. No ingestion subagent should ever
produce an element with this name from the other evidence files.

This tests two things:
1. **E5's own DoD** — `integration-mapper` must not invent a
   relationship to an id that doesn't exist among already-written
   elements; its `add_relationship` tool call for this pair should be
   rejected (see `agents/tools.py`'s `add_relationship`), and it should
   report this as a gap rather than silently proceeding.
2. **F2's DoD** — if a broken reference were ever written anyway (e.g.
   a future bug), the `validator` must flag it as a violation
   referencing an unknown id, not silently pass it.

## Reproducibility

This fixture is checked into `test-fixtures/` and is intentionally small
and static — every developer running Epic E's subagents against it
should get substantially the same element counts (exact wording may
vary between LLM runs; the underlying facts claimed should not, per
each ingestion subagent's own Reproducibility quality attribute).

## Known limitations of this fixture (by design, for MVP scope)

- The "interview transcript" is pre-written text, not a live interview —
  matches the MVP note in E2 that live SME interviewing is out of scope
  for the business-analyst subagent itself.
- The near-duplicate is deliberately easy (exact match after
  normalization) since F1's MVP reconciler is a normalized-name exact
  match, not fuzzy matching — see F1's task description for why.
