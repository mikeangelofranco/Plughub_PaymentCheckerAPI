from zoneinfo import ZoneInfo

from django import forms
from django.utils import timezone

from .models import CustomerSubscription, PaymentRecord

PH_TZ = ZoneInfo("Asia/Manila")


class CustomerForm(forms.ModelForm):
    last_login = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "control",
                "placeholder": "2025-01-22T09:00",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = CustomerSubscription
        fields = [
            "external_id",
            "product",
            "email",
            "username",
            "last_login",
            "subscription_type",
            "status",
        ]
        widgets = {
            "external_id": forms.TextInput(
                attrs={"class": "control", "placeholder": "INV-2045"}
            ),
            "product": forms.TextInput(
                attrs={"class": "control", "placeholder": "PlugHub Inventory"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "control", "placeholder": "fleet.ops@plughub.com"}
            ),
            "username": forms.TextInput(
                attrs={"class": "control", "placeholder": "fleet-ops"}
            ),
            "subscription_type": forms.TextInput(
                attrs={"class": "control", "placeholder": "Yearly"}
            ),
            "status": forms.Select(attrs={"class": "control"}),
        }
        labels = {
            "external_id": "Customer ID",
            "product": "Product",
            "email": "Email",
            "username": "Username",
            "last_login": "Last login (PH time)",
            "subscription_type": "Subscription type",
            "status": "Status",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk and instance.last_login:
            localized = instance.last_login.astimezone(PH_TZ)
            self.initial["last_login"] = localized.strftime("%Y-%m-%dT%H:%M")

    def clean_external_id(self):
        external_id = self.cleaned_data["external_id"]
        return external_id.strip()

    def clean_last_login(self):
        value = self.cleaned_data.get("last_login")
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value, PH_TZ)
        return value


class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentRecord
        fields = [
            "name",
            "email",
            "amount",
            "reference_number",
            "payment_id",
            "status",
            "used",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "control", "placeholder": "Payment Owner"}),
            "email": forms.EmailInput(attrs={"class": "control", "placeholder": "payer@example.com"}),
            "amount": forms.NumberInput(attrs={"class": "control", "placeholder": "1200.00", "step": "0.01"}),
            "reference_number": forms.TextInput(attrs={"class": "control", "placeholder": "PM-REF-1234"}),
            "payment_id": forms.TextInput(attrs={"class": "control", "placeholder": "paymongo-id"}),
            "status": forms.TextInput(attrs={"class": "control", "placeholder": "Paid"}),
            "used": forms.CheckboxInput(attrs={"class": "control checkbox"}),
        }
        labels = {
            "name": "Name",
            "email": "Email",
            "amount": "Amount",
            "reference_number": "Reference Number",
            "payment_id": "Payment ID",
            "status": "Status",
            "used": "Used",
        }
