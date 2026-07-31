"""
OrderService — coordinates order creation and hands off to payment
authorization. Deliberately tiny fixture service, not real production code.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    customer_id: str
    amount_cents: int
    status: str = "pending"


class OrderService:
    """Application Component: creates and tracks orders, and calls out to
    the Payment Authorization Service (see payment-service/main.py) to
    authorize payment before marking an order as fulfilled."""

    def __init__(self, payment_interface_url: str) -> None:
        self.payment_interface_url = payment_interface_url
        self._orders: dict[str, Order] = {}

    def create_order(self, order_id: str, customer_id: str, amount_cents: int) -> Order:
        """Application Service: Order Creation."""
        order = Order(order_id=order_id, customer_id=customer_id, amount_cents=amount_cents)
        self._orders[order_id] = order
        return order

    def submit_for_payment(self, order_id: str, card_token: str) -> Order:
        """Application Service: Order Submission.

        Calls out to the Payment Authorization Service (PaymentInterface,
        see payment-service/main.py) over HTTP at self.payment_interface_url.
        This is the code-level evidence for the cross-component relationship
        that integration-mapper (E5) should later pick up from the API spec.
        """
        order = self._orders[order_id]
        # POST {self.payment_interface_url}/authorize -- see api-spec.yaml
        order.status = "awaiting_payment"
        return order
