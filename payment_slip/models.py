from decimal import Decimal

from django.db import models

from transaction.models import TransactionModel

# Create your models here.
### realistic payment slip simulation according to FEBRABAN standards


class PaymentSlipModel(models.Model):
    # identification
    barcode = models.CharField(max_length=44, unique=True)
    digitable_line = models.CharField(max_length=50, unique=True)
    our_number = models.CharField(max_length=10)
    document_number = models.CharField(max_length=64)
    bank_code = models.CharField(max_length=3, default="120")
    external_id = models.CharField(max_length=100, null=True, blank=True)
    currency_code = models.CharField(max_length=3, default="BRL")

    # values and dates
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    due_date = models.DateField()
    issue_date = models.DateTimeField(auto_now_add=True)
    processing_date = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    interest_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), blank=True, null=True
    )
    fine_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), blank=True, null=True
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), blank=True, null=True
    )

    # beneficiary
    beneficiary_name = models.CharField(
        max_length=100, default="beneficiary enterprise name"
    )  # beneficiary simulation
    beneficiary_document = models.CharField(
        max_length=20, default="beneficiary document"
    )  # beneficiary simulation
    beneficiary_agency = models.CharField(
        max_length=4, default="9918"
    )  # beneficiary simulation
    beneficiary_account = models.CharField(
        max_length=16, default="99999918"
    )  # beneficiary simulation

    # payer
    payer_name = models.CharField(max_length=100)
    payer_document = models.CharField(max_length=14, default="000000")  # for instance
    payer_address = models.CharField(max_length=200, default="some address")
    payer_city = models.CharField(max_length=50, default="San Francisco")
    payer_state = models.CharField(max_length=50, default="California")
    payer_zipcode = models.CharField(max_length=9, default="999999")

    # status
    STATUS_OPTIONS = [
        ("PENDING", "pending"),
        ("PROCESSING", "processing"),
        ("PAID", "paid"),
        ("EXPIRED", "EXPIRED"),
    ]
    status = models.CharField(max_length=12, choices=STATUS_OPTIONS, default="PENDING")

    # instructions
    instructions = models.TextField(
        blank=True, default="Pay at the bank or other financial store"
    )

    # transaction
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.CASCADE, blank=True, null=True
    )

    # control
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

    def __str__(self):
        return f"barcode: {self.barcode}, number: {self.document_number}"
