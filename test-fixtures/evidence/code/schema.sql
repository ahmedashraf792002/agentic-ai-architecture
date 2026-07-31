-- Order Platform database schema (fixture, deliberately minimal)

CREATE TABLE orders (
    order_id      VARCHAR(36) PRIMARY KEY,
    customer_id   VARCHAR(36) NOT NULL,
    amount_cents  INTEGER NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at    TIMESTAMP NOT NULL DEFAULT now()
);
-- Data Object: Order — mirrors the Order business object from
-- order-fulfillment-process.md, now at the application/data level.

CREATE TABLE payment_authorizations (
    authorization_id VARCHAR(36) PRIMARY KEY,
    order_id          VARCHAR(36) NOT NULL REFERENCES orders(order_id),
    authorized        BOOLEAN NOT NULL,
    authorized_at     TIMESTAMP NOT NULL DEFAULT now()
);
-- Data Object: Payment Authorization Record.
