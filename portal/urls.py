from django.urls import path

from .views import DashboardView, check_user_details, license_consume, log_payments

app_name = "portal"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard", DashboardView.as_view()),
    path("api/checkuserdetails/", check_user_details, name="checkuserdetails"),
    path("api/checkuserdetails", check_user_details),
    path("api/logpayments/", log_payments, name="logpayments"),
    path("api/logpayments", log_payments),  # allow no trailing slash (webhooks)
    path("api/licenseconsume/", license_consume, name="licenseconsume"),
    path("api/licenseconsume", license_consume),
]
