# API Integration Spec

## Payment Service → Fraud Detection Service
- Type: REST/HTTP
- Endpoint: POST /fraud/check
- Data flow: payment amount and customer ID sent; risk score returned.

## Payment Service → Core Banking Adapter
- Type: REST/HTTP
- Endpoint: POST /banking/charge
- Data flow: amount, currency, customer ID sent; transaction result returned.

## Web Portal → Payment Service
- Type: REST/HTTP
- Endpoint: POST /payments
- Data flow: customer initiates payment from web UI.
