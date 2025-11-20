# PlugHub Payment Checker API - Django Shell

Base scaffolding for the PlugHub Payment Checker experience, mirroring the stack used for Inventory and Queueing (Django auth + custom templates).

## Features
- Postgres-backed customer directory with seeded dummy data across Inventory, Queueing, and Payment Checker SKUs.
- Responsive login screen with shared dark theme styling.
- Authenticated dashboard shell with search, inline edit buttons, and an Insert Customer modal.
- Pre-wired Django admin plus logout route so you can jump into `/admin/` whenever you add staff users.
- Protected API endpoint `/api/checkuserdetails/` that requires an API key header and rate-limits requests.

## Getting Started
```bash
# 1. (Optional) recreate the virtualenv
python -m venv .venv

# 2. Activate it, then install dependencies
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Set Postgres credentials (reuse the same ones as PlugHub IMS/Queue)
#    Update values in .env at the repo root; these are the defaults:
#    PLUGHUB_DB_NAME=plughub_paymentchecker
#    PLUGHUB_DB_USER=plughub_admin
#    PLUGHUB_DB_PASSWORD=plughub_admin
#    PLUGHUB_DB_HOST=127.0.0.1
#    PLUGHUB_DB_PORT=5432
#    PLUGHUB_API_KEY_DEV=<dev-api-key>
#    PLUGHUB_API_KEY_PROD=<prod-api-key>

# 4. Apply migrations (creates tables + seeds dummy customers)
python manage.py migrate

# 5. Create a superuser for login
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

API usage example (include API key):
```http
POST /api/checkuserdetails/
Header: X-Api-Key: <your-api-key>
Body: { "data": { "email": "user@example.com", "product": "gmail-addon-cleaner" } }
```

Visit `http://localhost:8000/` to see the login screen. After signing in you will land on `/dashboard/`, which now renders live records from Postgres.

## Project Layout Highlights
- `plughub_paymentchecker/settings.py` - Django config with Postgres connection variables and auth redirects.
- `portal/models.py` - CustomerSubscription model and status choices.
- `portal/views.py` & `portal/urls.py` - Login + dashboard views and URL wiring.
- `portal/templates/portal/dashboard.html` - Admin dashboard with inline edit/insert modal.
- `templates/registration/login.html` - Responsive login layout.
- `static/css/main.css` - Shared styling tokens for both the login and dashboard experiences.

## Next Steps
1. Hook the login view to your preferred identity provider if you are not using Django's built-in auth.
2. Replace the seeded data with your production Payment Checker endpoint once available.
3. Add additional apps (e.g., `payments`, `reconciliations`) as the backend solidifies.
