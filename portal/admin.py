from django.contrib import admin

from .models import CustomerSubscription, PaymentRecord


@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "external_id",
        "product",
        "email",
        "username",
        "subscription_type",
        "status",
        "last_login",
    )
    search_fields = (
        "external_id",
        "product",
        "email",
        "username",
        "subscription_type",
        "status",
    )
    list_filter = ("status", "product")


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "payment_id",
        "name",
        "email",
        "amount",
        "status",
        "used",
        "date_consumed",
    )
    search_fields = (
        "reference_number",
        "payment_id",
        "name",
        "email",
        "status",
    )
    list_filter = ("status", "used")
