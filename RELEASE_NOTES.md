# Subscriber Directory – Release Notes

## v1.0.0
- New dual-tab dashboard for Customers and Payments with inline edit/insert modals and pagination.
- Postgres-backed models with seed customers and PayMongo payment records (includes `used` + `date_consumed` flags).
- Secure APIs:
  - `/api/checkuserdetails/` (lookup/add customer).
  - `/api/logpayments/` (accepts PayMongo webhooks or custom schema; HMAC signature validation for PayMongo).
  - `/api/licenseconsume/` (consumes payment reference, marks used, updates/creates Gmail add-on subscription to Paid).
- API key enforcement plus rate limiting; PayMongo webhook signature verification.
- Responsive UI styling updates, gradient page header (“Subscriber Directory”), and payments table shows date consumed.
- Deployment-ready configuration via `.env.example` (DB, API keys, webhook secret, allowed hosts).
