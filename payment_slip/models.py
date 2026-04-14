from django.db import models
from transaction.models import TransactionModel
from user.models import UserModel
from decimal import Decimal

# Create your models here.

class PaymentSlipModel(models.Model):
    # identification
    barcode = models.CharField(max_length=64, unique=True)
    digitable_line = models.CharField(max_length=100, unique=True)
    our_number = models.CharField(max_length=64)
    document_number = models.CharField(max_length=64)
    bank_code = models.CharField(max_length=4)
    external_id = models.CharField(max_length=100, null=True, blank=True)
    currency_code = models.CharField(max_length=3, default='BRL')

    # values and dates
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateTimeField()
    issue_date = models.DateTimeField(auto_now_add=True)
    processing_date = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))


    # beneficiary
    beneficiary_name = models.CharField(max_length=100)
    beneficiary_document = models.CharField(max_length=14)
    beneficiary_agency = models.CharField(max_length=4)
    beneficiary_account = models.CharField(max_length=16)


    # payer
    payer_name = models.CharField(max_length=100)
    payer_document = models.CharField(max_length=14)
    payer_address = models.CharField(max_length=200)
    payer_city = models.CharField(max_length=50)
    payer_state = models.CharField(max_length=50)
    payer_zipcode = models.CharField(max_length=9)

    # status
    STATUS_OPTIONS = [
        ('PENDING', 'pending'),
        ('PROCESSING', 'processing'),
        ('PAID', 'paid'),
        ('EXPIRED', 'EXPIRED')
    ]
    status = models.CharField(max_length=12, choices=STATUS_OPTIONS, default='PENDING')

    # instructions
    instructions = models.TextField(blank=True)

    # transaction
    transaction = models.ForeignKey(TransactionModel, on_delete=models.CASCADE)

    # control
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
