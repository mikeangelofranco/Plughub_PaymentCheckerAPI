from django.urls import path

from .views import DashboardView, check_user_details, license_consume, log_payments
from django.views.generic import TemplateView

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
    path("emailcleaner/", TemplateView.as_view(template_name="email_cleaner_home.html"), name="emailcleaner_home"),
    path("emailcleaner", TemplateView.as_view(template_name="email_cleaner_home.html")),
    path("emailcleaner/support/", TemplateView.as_view(template_name="support.html"), name="emailcleaner_support"),
    path("emailcleaner/support", TemplateView.as_view(template_name="support.html")),
    path("emailcleaner/privacypolicy/", TemplateView.as_view(template_name="privacy_policy.html"), name="emailcleaner_privacypolicy"),
    path("emailcleaner/privacypolicy", TemplateView.as_view(template_name="privacy_policy.html")),
    path("emailcleaner/termsofservice/", TemplateView.as_view(template_name="terms_of_service.html"), name="emailcleaner_termsofservice"),
    path("emailcleaner/termsofservice", TemplateView.as_view(template_name="terms_of_service.html")),
]
