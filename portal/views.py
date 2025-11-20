import json
import secrets
import string

import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from .forms import CustomerForm, PaymentForm
from .models import CustomerSubscription, PaymentRecord


ALLOWED_PRODUCTS = {
    "gmail-addon-cleaner",
    "plughub-ims",
    "plughub-queueing",
}

logger = logging.getLogger(__name__)

# Simple throttle: limit requests per IP per minute for the public API.
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60


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

    def get_queryset(self):
        query = self.request.GET.get("q")
        subscriptions = CustomerSubscription.objects.all()
        if query:
            subscriptions = subscriptions.filter(
                Q(external_id__icontains=query)
                | Q(product__icontains=query)
                | Q(email__icontains=query)
                | Q(username__icontains=query)
                | Q(subscription_type__icontains=query)
                | Q(status__icontains=query)
            )
        return subscriptions.order_by("external_id")

    def get_payment_queryset(self):
        query = self.request.GET.get("pay_q")
        payments = PaymentRecord.objects.all()
        if query:
            payments = payments.filter(
                Q(name__icontains=query)
                | Q(email__icontains=query)
                | Q(reference_number__icontains=query)
                | Q(payment_id__icontains=query)
                | Q(status__icontains=query)
            )
        return payments

    def get_page_obj(self, queryset, page_param, per_page=5):
        paginator = Paginator(queryset, per_page)
        page_number = self.request.GET.get(page_param) or 1
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return paginator, page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_tab = self.request.GET.get("tab", "customers")
        context["current_tab"] = current_tab

        sub_queryset = self.get_queryset()
        sub_paginator, sub_page_obj = self.get_page_obj(sub_queryset, "page")

        pay_queryset = self.get_payment_queryset()
        pay_paginator, pay_page_obj = self.get_page_obj(pay_queryset, "pay_page")

        params = self.request.GET.copy()
        params.pop("page", None)
        context["querystring"] = params.urlencode()

        pay_params = self.request.GET.copy()
        pay_params.pop("pay_page", None)
        context["pay_querystring"] = pay_params.urlencode()

        context["paginator"] = sub_paginator
        context["page_obj"] = sub_page_obj
        context["subscriptions"] = sub_page_obj.object_list
        context["form"] = kwargs.get("form") or CustomerForm()
        context["active_customer_id"] = kwargs.get("active_customer_id")
        context["form_mode"] = kwargs.get("form_mode") or "create"
        context["query"] = self.request.GET.get("q", "")
        context["open_modal"] = kwargs.get("open_modal", False)

        context["payments"] = pay_page_obj.object_list
        context["payment_paginator"] = pay_paginator
        context["payment_page_obj"] = pay_page_obj
        context["payment_form"] = kwargs.get("payment_form") or PaymentForm()
        context["active_payment_id"] = kwargs.get("active_payment_id")
        context["payment_form_mode"] = kwargs.get("payment_form_mode") or "create"
        context["payment_query"] = self.request.GET.get("pay_q", "")
        context["open_payment_modal"] = kwargs.get("open_payment_modal", False)
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type", "customer")
        if form_type == "payment":
            payment_pk = request.POST.get("payment_pk")
            instance = PaymentRecord.objects.filter(pk=payment_pk).first() if payment_pk else None
            payment_form = PaymentForm(request.POST, instance=instance)
            if payment_form.is_valid():
                payment_form.save()
                action = "updated" if instance else "added"
                messages.success(request, f"Payment {action} successfully.")
                return redirect(reverse("portal:dashboard") + "?tab=payments")

            context = {
                "payment_form": payment_form,
                "active_payment_id": payment_pk,
                "payment_form_mode": "edit" if instance else "create",
                "open_payment_modal": True,
                "current_tab": "payments",
            }
            return self.render_to_response(self.get_context_data(**context))

        customer_id = request.POST.get("customer_id")
        instance = CustomerSubscription.objects.filter(pk=customer_id).first() if customer_id else None
        form = CustomerForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            action = "updated" if instance else "added"
            messages.success(request, f"Customer {action} successfully.")
            return redirect("portal:dashboard")

        context = {
            "form": form,
            "active_customer_id": customer_id,
            "form_mode": "edit" if instance else "create",
            "open_modal": True,
            "current_tab": "customers",
        }
        return self.render_to_response(self.get_context_data(**context))


def portal_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been signed out.")
    return redirect("login")


def _generate_external_id(product: str) -> str:
    parts = [p for p in product.split("-") if p]
    prefix = "".join(p[0].upper() for p in parts)[:3] or product[:3].upper() or "PHB"
    if len(prefix) < 3:
        prefix = prefix.ljust(3, "X")
    while True:
        suffix = "".join(secrets.choice(string.digits) for _ in range(4))
        candidate = f"{prefix}-{suffix}"
        if not CustomerSubscription.objects.filter(external_id=candidate).exists():
            return candidate


def _subscription_type_for_product(product: str) -> str:
    if product == "gmail-addon-cleaner":
        return "One-time"
    return "Monthly"


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _check_rate_limit(request):
    ip = _client_ip(request)
    cache_key = f"throttle:checkuser:{ip}"
    current = cache.get(cache_key)
    if current and current >= RATE_LIMIT_REQUESTS:
        return False
    if current is None:
        cache.set(cache_key, 1, timeout=RATE_LIMIT_WINDOW_SECONDS)
    else:
        cache.incr(cache_key)
    return True


def _check_api_key(request):
    supplied = request.headers.get("X-Api-Key") or request.META.get("HTTP_X_API_KEY")
    if not supplied:
        return False
    allowed = getattr(settings, "PLUGHUB_ALLOWED_API_KEYS", [])
    return supplied in allowed


@csrf_exempt
@require_POST
def check_user_details(request):
    if not _check_api_key(request):
        logger.warning("Unauthorized API call to check_user_details", extra={"ip": _client_ip(request)})
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if not _check_rate_limit(request):
        logger.warning("Rate limit exceeded for check_user_details", extra={"ip": _client_ip(request)})
        return JsonResponse({"error": "Rate limit exceeded"}, status=429)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    data = payload.get("data") if isinstance(payload, dict) else None
    if data is None and isinstance(payload, dict):
        data = payload

    email = (data.get("email") or "").strip().lower() if isinstance(data, dict) else ""
    product = (data.get("product") or "").strip().lower() if isinstance(data, dict) else ""

    if not email or not product:
        return JsonResponse({"error": "Both email and product are required."}, status=400)

    if ALLOWED_PRODUCTS and product not in ALLOWED_PRODUCTS:
        return JsonResponse({"error": "Unsupported product."}, status=400)

    existing = CustomerSubscription.objects.filter(
        product__iexact=product,
        email__iexact=email,
    ).first()

    if existing:
        return JsonResponse({"data": {"status": existing.status.upper()}})

    new_record = CustomerSubscription.objects.create(
        external_id=_generate_external_id(product),
        product=product,
        email=email,
        username="",
        last_login=timezone.now(),
        subscription_type=_subscription_type_for_product(product),
        status=CustomerSubscription.Status.FREE,
    )

    return JsonResponse({"data": {"status": new_record.status.upper()}}, status=201)


@csrf_exempt
@require_POST
def log_payments(request):
    if not _check_api_key(request):
        logger.warning("Unauthorized API call to log_payments", extra={"ip": _client_ip(request)})
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if not _check_rate_limit(request):
        logger.warning("Rate limit exceeded for log_payments", extra={"ip": _client_ip(request)})
        return JsonResponse({"error": "Rate limit exceeded"}, status=429)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    data = payload.get("data") if isinstance(payload, dict) else None
    if data is None and isinstance(payload, dict):
        data = payload

    required_fields = ["Name", "Email", "Amount", "Reference", "PaymentID", "Status"]
    if not isinstance(data, dict):
        return JsonResponse({"error": "Missing data object"}, status=400)

    missing = [field for field in required_fields if not str(data.get(field, "")).strip()]
    if missing:
        return JsonResponse({"error": f"Missing fields: {', '.join(missing)}"}, status=400)

    try:
        amount_val = Decimal(str(data.get("Amount"))).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        return JsonResponse({"error": "Amount must be a valid number"}, status=400)

    record = PaymentRecord.objects.create(
        name=data.get("Name", "").strip(),
        email=data.get("Email", "").strip().lower(),
        amount=amount_val,
        reference_number=data.get("Reference", "").strip(),
        payment_id=data.get("PaymentID", "").strip(),
        status=data.get("Status", "").strip(),
        used=False,
    )

    return JsonResponse(
        {
            "data": {
                "id": record.id,
                "reference": record.reference_number,
                "status": record.status,
                "used": record.used,
            }
        },
        status=201,
    )
