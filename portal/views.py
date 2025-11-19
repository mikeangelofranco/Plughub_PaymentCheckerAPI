from datetime import datetime
from zoneinfo import ZoneInfo

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

PH_TZ = ZoneInfo("Asia/Manila")


class PortalLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("portal:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("page_title", "PlugHub Payment Checker")
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "portal/dashboard.html"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        raw_subscriptions = [
            {
                "id": "INV-2045",
                "product": "PlugHub Inventory",
                "email": "fleet.ops@plughub.com",
                "username": "fleet-ops",
                "last_login": "2025-01-14T14:33:00+08:00",
                "subscription_type": "Yearly",
                "status": "Paid",
            },
            {
                "id": "QMS-9934",
                "product": "PlugHub Queueing",
                "email": "queues@plughub.com",
                "username": "queue-master",
                "last_login": "2025-01-20T10:05:00+08:00",
                "subscription_type": "Monthly",
                "status": "Paid",
            },
            {
                "id": "PCX-5533",
                "product": "Payment Checker",
                "email": "finance.audit@plughub.com",
                "username": "audit-team",
                "last_login": "2025-01-22T08:12:00+08:00",
                "subscription_type": "Pilot",
                "status": "Free",
            },
            {
                "id": "INV-8721",
                "product": "PlugHub Inventory",
                "email": "warehouse@plughub.com",
                "username": "wh-admin",
                "last_login": "2025-01-18T19:52:00+08:00",
                "subscription_type": "One-time",
                "status": "Paid",
            },
        ]
        for record in raw_subscriptions:
            last_login_str = record.get("last_login")
            if last_login_str:
                try:
                    parsed = datetime.fromisoformat(last_login_str)
                    record["last_login"] = parsed.astimezone(PH_TZ)
                except ValueError:
                    record["last_login"] = None
        context["subscriptions"] = raw_subscriptions
        return context


def portal_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been signed out.")
    return redirect("login")
