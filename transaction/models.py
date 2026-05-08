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

    def debits_to_account(self, sender):
        if self.amount > sender.balance:
            raise ValidationError("Insufficient funds.")
        sender.balance = F("balance") - self.amount

    def deposit(self, sender):
        sender.balance = F("balance") + self.amount
        return self.transaction_type

    def transfer(self, sender, recipient):
        if not recipient:
            raise ValidationError("Recipient is required for a transfer transaction")
        self.debits_to_account(sender)
        recipient.balance = F("balance") + self.amount
        return self.transaction_type

    def withdraw(self, sender):
        self.debits_to_account(sender)
        return self.transaction_type

    def payment(self, sender):
        self.debits_to_account(sender)
        return self.transaction_type

    @transaction.atomic
    def submit(self):
        self.full_clean()

        # protection against deadlock
        account_ids = [self.sender_id]
        if self.recipient_id:
            account_ids.append(self.recipient_id)

        # accounts lock by order
        account_ids = sorted(account_ids)
        accounts = AccountModel.objects.select_for_update().filter(pk__in=account_ids)
        accounts_map = {acc.pk: acc for acc in accounts}

        sender = accounts_map[self.sender_id]
        recipient = accounts_map.get(self.recipient_id)

        # business rules
        if self.transaction_type == "TF":
            self.transfer(sender, recipient)
        elif self.transaction_type == "DP":
            self.deposit(sender)
        elif self.transaction_type == "WD":
            self.withdraw(sender)
        elif self.transaction_type == "PM":
            self.payment(sender)
        else:
            raise ValidationError("Invalid transaction type")

        sender.save()

        if recipient is not None:
            recipient.save()

        super().save()
