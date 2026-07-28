# Interview Transcript: Head of Payments

Q: What is the main payment flow?
A: Customers initiate payment through the web portal. The payment service validates the request,
   calls the fraud detection service, then processes through the core banking adapter.

Q: Who is involved?
A: The Customer uses the web portal. Payment Operations team monitors failed transactions.
   The Finance team reconciles settlements daily.

Q: What systems handle this?
A: Payment Service is the main application component. It talks to Fraud Detection Service
   and the Core Banking Adapter.
