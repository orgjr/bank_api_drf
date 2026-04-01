from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from products.models import AccountModel

# Create your models here.
# todo refactor separation of responsibilities


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
        AccountModel, null=True, blank=True, on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=2,
        choices=TRANSACTION_TYPE,
        null=True,
        blank=True,
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
        return f"Sender: {self.sender.number} to {self.recipient}, Transaction: {self.transaction_type}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sender.save()

    def clean(self):
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

    def debits_to_account(self, amount):
        if amount > self.sender.balance:
            raise ValidationError("Insufficient funds.")
        self.sender.balance -= amount
        return self.transaction_type

    def deposit(self, amount):
        self.sender.balance += amount
        return self.transaction_type

    def transfer(self, recipient, amount):
        if not recipient:
            raise ValidationError("Recipient required for transfer")
        self.debits_to_account(amount)
        recipient.balance += amount
        recipient.save()
        return self.transaction_type

    def withdraw(self, amount):
        self.debits_to_account(amount)
        return self.transaction_type

    def payment(self, amount):
        self.debits_to_account(amount)
        return self.transaction_type

    def validate_transaction(self):
        amount = self.amount
        transaction_type = self.transaction_type
        if transaction_type == "TF":
            if not self.recipient:
                raise ValidationError("Transfer requires a recipient")
            recipient = self.recipient
            return self.transfer(recipient, amount)
        elif transaction_type == "DP":
            deposit = self.deposit(amount)
            return deposit
        elif transaction_type == "WD":
            withdraw = self.withdraw(amount)
            return withdraw
        elif transaction_type == "PM":
            payment = self.payment(amount)
            return payment
        else:
            raise ValidationError("transaction not completed")

    def submit(self):
        self.full_clean()
        validate_transaction = self.validate_transaction()
        self.save()
        return validate_transaction
