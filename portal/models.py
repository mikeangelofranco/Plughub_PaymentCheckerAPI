from django.db import models


class CustomerSubscription(models.Model):
    class Status(models.TextChoices):
        PAID = "Paid", "Paid"
        FREE = "Free", "Free"
        IN_ARREARS = "In Arrears", "In arrears"

    external_id = models.CharField(max_length=50, unique=True)
    product = models.CharField(max_length=120)
    email = models.EmailField()
    username = models.CharField(max_length=120)
    last_login = models.DateTimeField(blank=True, null=True)
    subscription_type = models.CharField(max_length=60)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PAID,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["external_id"]
        verbose_name = "customer subscription"
        verbose_name_plural = "customer subscriptions"

    def __str__(self):
        return f"{self.external_id} ({self.product})"


class PaymentRecord(models.Model):
    name = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=80, unique=True)
    payment_id = models.CharField(max_length=120, unique=True)
    status = models.CharField(max_length=40)
    used = models.BooleanField(default=False)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "payment record"
        verbose_name_plural = "payment records"

    def __str__(self):
        return f"{self.reference_number} ({self.status})"
