from django.urls import path

from .views import DashboardView, check_user_details, log_payments

app_name = "portal"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/checkuserdetails/", check_user_details, name="checkuserdetails"),
    path("api/logpayments/", log_payments, name="logpayments"),
]
