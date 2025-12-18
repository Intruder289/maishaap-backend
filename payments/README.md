# Payments API

This document describes the payments module API endpoints and how the Flutter app should interact with them.

Base API prefix: `/api/v1/payments/` (see `Maisha_backend/urls.py` which includes `payments.api_urls`)

Authentication
- Uses JWT (Simple JWT). Include header: `Authorization: Bearer <access_token>`

Endpoints (DRF router)
- `GET /api/v1/payments/providers/` - list payment providers
- `GET /api/v1/payments/invoices/` - list invoices (tenants see only their invoices)
- `POST /api/v1/payments/invoices/` - create invoice (staff only)
- `GET /api/v1/payments/payments/` - list payments
- `POST /api/v1/payments/payments/` - create a payment record (tenant)
- `POST /api/v1/payments/payments/{id}/initiate/` - initiate payment transaction for a payment
- `GET /api/v1/payments/transactions/` - list transactions

Payload examples

Create Payment (tenant):
{
  "invoice": 12,
  "tenant": 5,
  "provider": 1,
  "amount": "120.00"
}

Initiate Transaction (POST to `/payments/{id}/initiate/`):
{
  "request_payload": {
    "phone": "+2557xxxxxxx",
    "amount": "120.00",
    "callback_url": "https://your.domain/api/v1/payments/transactions/callback/"
  }
}

Notes for Flutter
- Use the project's auth endpoints to log in and obtain a JWT access token.
- Pass the token in `Authorization` header for all requests.
- For payment flows, create a `Payment` record first, then call the `initiate` action to create a transaction on the backend.
- Backend will persist `PaymentTransaction` and return details the Flutter app can use to redirect the user, poll status, or show a confirmation.

Web Templates
- Simple templates exist at `payments/templates/payments/invoice_list.html` and `payment_list.html`; they extend the main site `accounts/base.html`.
