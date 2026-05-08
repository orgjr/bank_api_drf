from decimal import Decimal

from django.db import models


# Create your models here.
class CIPPaymentSlipRegistryModel(models.Model):
    OPTIONS = [
        ("PENDING", "Pendente"),
        ("PAID", "Pago"),
        ("EXPIRED", "Expirado"),
        ("CANCELLED", "Cancelado"),
    ]
    beneficiary_name = models.CharField(max_length=200)
    barcode = models.CharField(max_length=44, unique=True)
    digitable_line = models.CharField(max_length=54, unique=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(max_length=10, choices=OPTIONS, default="PENDING")

    BANK_OPTIONS = [
        # some example options
        ("120", "skbank"),
        ("001", "Banco do Brasil S.A."),
        ("237", "Bradesco S.A"),
        ("077", "Banco Inter S.A"),
    ]
    bank_code = models.CharField(max_length=3, choices=BANK_OPTIONS)
    external_id = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="amount_positive",
            )
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
