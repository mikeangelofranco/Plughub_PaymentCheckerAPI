# PlugHub Payment Checker API – Django Shell

Base scaffolding for the PlugHub Payment Checker experience, mirroring the stack we used for the Inventory and Queueing systems (Django + Django auth + custom templates).

## Features
- Responsive hero-style login screen with glassmorphism styling and static assets under `static/css`.
- Custom `PortalLoginView` leveraging Django's auth workflow, with redirects wired into a branded dashboard stub.
- Authenticated dashboard shell ready for future API data, including stat cards and panels for reconciliation streams.
- Pre-wired Django admin plus logout route, so you can jump into `/admin/` whenever you add staff users.

## Getting Started
```bash
# 1. (Optional) recreate the virtualenv
python -m venv .venv

# 2. Activate it, then install dependencies
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Apply default migrations
python manage.py migrate

# 4. Create a superuser for login
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

Visit `http://localhost:8000/` to see the login screen. After signing in you’ll land on `/dashboard/`, which currently surfaces placeholder content so you can integrate real PaymentCheckerAPI data later.

## Project Layout Highlights
- `plughub_paymentchecker/settings.py` – Django config with template/static directories plus auth redirects.
- `portal/views.py` & `portal/urls.py` – Login + dashboard views and URL wiring.
- `templates/registration/login.html` – Responsive login layout.
- `portal/templates/portal/dashboard.html` – Admin dashboard stub.
- `static/css/main.css` – Shared styling tokens for both the login and dashboard experiences.

## Next Steps
1. Hook the login view to your preferred identity provider if you are not using Django’s built-in auth.
2. Replace the hard-coded statistics in `dashboard.html` with live data from future Payment Checker endpoints.
3. Add additional apps (e.g., `payments`, `reconciliations`) as the backend solidifies.
