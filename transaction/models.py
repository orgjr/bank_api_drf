from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from products.models import AccountModel

# Create your models here.


class TransactionModel(models.Model):
    TRANSACTION_TYPE = [
        ("TF", "Transfer"),
        ("DP", "Deposit"),
        ("WD", "Withdraw"),
        ("PM", "Payment"),
    ]

    sender = models.ForeignKey(
        AccountModel,
        related_name="transactions",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    recipient = models.ForeignKey(
        AccountModel, null=True, blank=True, on_delete=models.SET_NULL
    )

    transaction_type = models.CharField(
        max_length=2,
        choices=TRANSACTION_TYPE,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        null=False,
        blank=False,
    )

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sender: {self.sender.number} {'to ' + str(self.recipient if self.recipient is not None else '')}, Transaction: {self.transaction_type}"

    def clean(self):
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

        if self.amount is None or self.amount <= 0:
            raise ValidationError("Amount is required and must be greater than zero")

        if self.transaction_type == "TF" and not self.recipient:
            raise ValidationError("Transfer must have recipient")

        if self.transaction_type in ["DP", "WD", "PM"] and self.recipient:
            raise ValidationError("This transaction should not have recipient")

    def debits_to_account(self):
        if self.amount > self.sender.balance:
            raise ValidationError("Insufficient funds.")
        self.sender.balance = F("balance") - self.amount

    def deposit(self):
        self.sender.balance = F("balance") + self.amount
        return self.transaction_type

    def transfer(self, recipient):
        if not recipient:
            raise ValidationError("Recipient is required for a transfer transaction")
        self.debits_to_account()
        recipient.balance = F("balance") + self.amount
        return self.transaction_type

    def withdraw(self):
        self.debits_to_account()
        return self.transaction_type

    def payment(self):
        self.debits_to_account()
        return self.transaction_type

    @transaction.atomic
    def submit(self):
        self.full_clean()
        if self.transaction_type == "TF":
            self.transfer(self.recipient)
        elif self.transaction_type == "DP":
            self.deposit()
        elif self.transaction_type == "WD":
            self.withdraw()
        elif self.transaction_type == "PM":
            self.payment()
        else:
            raise ValidationError("Invalid transaction type")

        self.sender.save()

        if self.recipient:
            self.recipient.save()

        super().save()
