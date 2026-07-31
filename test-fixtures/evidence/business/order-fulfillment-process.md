# Order Fulfillment — Process Overview

## Actors and roles

- **Customer** — places orders through the storefront.
- **Order Desk Clerk** (role) — handles manually-flagged orders that fail
  automated validation.

## Process: Order Fulfillment

1. Customer submits an order via the storefront.
2. The **Order Fulfillment** business process validates the order and
   hands off to payment authorization.
3. On successful payment, the process triggers shipment handoff.
4. On failed payment, the order is flagged for the Order Desk Clerk.

## Business Service: Payment Authorization Service

A business-level service, exposed to the Order Fulfillment process, that
represents "authorize a customer's payment for an order" as a black-box
capability — independent of which underlying application implements it
today.

## Business Object: Order

An Order carries a customer reference, line items, and a payment status
(pending / authorized / failed).
