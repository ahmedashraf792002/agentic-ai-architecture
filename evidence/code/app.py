# Payment Service

class PaymentService:
    def process_payment(self, amount, currency, customer_id):
        if not self.validate_payment(amount, currency):
            return {"error": "invalid payment"}
        fraud_result = self.fraud_service.check(amount, customer_id)
        if fraud_result["risk"] > 0.8:
            return {"error": "payment rejected"}
        return self.banking_adapter.charge(amount, currency, customer_id)

    def validate_payment(self, amount, currency):
        return amount > 0 and currency in ["USD", "EUR"]

class FraudDetectionService:
    def check(self, amount, customer_id):
        return {"risk": 0.1, "reason": "low amount"}

class CoreBankingAdapter:
    def charge(self, amount, currency, customer_id):
        return {"status": "success", "transaction_id": "txn_12345"}
