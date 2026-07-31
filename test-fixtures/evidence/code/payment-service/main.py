"""
PaymentService — handles payment authorization for the Order Platform.

This is a deliberately tiny fixture service, not real production code.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PaymentResult:
    order_id: str
    authorized: bool
    reason: str | None = None


class PaymentService:
    """Application Component: authorizes payments against a stored card
    token. Exposes authorize_payment as its main entry point — this is
    the Application Service a code-analyzer subagent should identify."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def authorize_payment(self, order_id: str, amount_cents: int, card_token: str) -> PaymentResult:
        """Application Service: Payment Authorization.

        Authorizes a payment for the given order against the payments
        database. Returns a PaymentResult indicating success/failure.
        """
        if amount_cents <= 0:
            return PaymentResult(order_id=order_id, authorized=False, reason="invalid amount")
        # Real implementation would call out to a card processor here.
        return PaymentResult(order_id=order_id, authorized=True)


class PaymentInterface:
    """Application Interface: the HTTP surface PaymentService exposes to
    other components (e.g. OrderService) for payment authorization."""

    def __init__(self, service: PaymentService) -> None:
        self.service = service

    def post_authorize(self, order_id: str, amount_cents: int, card_token: str) -> dict:
        result = self.service.authorize_payment(order_id, amount_cents, card_token)
        return {"order_id": result.order_id, "authorized": result.authorized}
