from decimal import Decimal

from django.db import models

from transaction.models import TransactionModel


class PaymentSlipModel(models.Model):
    # ===============================
    # IDENTIFICATION
    # ===============================
    barcode = models.CharField(max_length=44, unique=True)
    digitable_line = models.CharField(max_length=54, unique=True)

    our_number = models.CharField(max_length=20, unique=True)
    document_number = models.CharField(max_length=64, unique=True)

    bank_code = models.CharField(max_length=3, default="120")

    currency_code = models.CharField(max_length=1, default="9")  # Real FEBRABAN

    external_id = models.CharField(max_length=100, null=True, blank=True)

    # ===============================
    # DATE AND VALUES
    # ===============================
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    due_date = models.DateField(db_index=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    processing_date = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    interest_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    fine_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # ===============================
    # BENEFICIARY
    # ===============================
    beneficiary_name = models.CharField(
        max_length=100, default="beneficiary enterprise name"
    )
    beneficiary_document = models.CharField(max_length=18, default="doc number")
    beneficiary_agency = models.CharField(max_length=10, default="9918")
    beneficiary_account = models.CharField(max_length=20, default="99999918")

    # ===============================
    # PAYER
    # ===============================
    payer_name = models.CharField(max_length=100)
    payer_document = models.CharField(max_length=18, default="000000")
    payer_address = models.CharField(max_length=200, default="some address")
    payer_city = models.CharField(max_length=100, default="Gramado")
    payer_state = models.CharField(max_length=2, default="RS")
    payer_zipcode = models.CharField(max_length=9, default="95670-000")

    # ===============================
    # STATUS
    # ===============================
    STATUS_OPTIONS = [
        ("PENDING", "Pendente"),
        ("PROCESSING", "Processando"),
        ("PAID", "Pago"),
        ("EXPIRED", "Expirado"),
        ("CANCELLED", "Cancelado"),
    ]

    status = models.CharField(
        max_length=12, choices=STATUS_OPTIONS, default="PENDING", db_index=True
    )

    # ===============================
    # INSTRUCTIONS
    # ===============================
    instructions = models.TextField(blank=True)

    # ===============================
    # RELATIONSHIP
    # ===============================
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.CASCADE, null=True, blank=True
    )

    # ===============================
    # CONTROL
    # ===============================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

    def __str__(self):
        return f"{self.barcode} | {self.document_number}"
