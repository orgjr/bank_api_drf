import random
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from user.models import UserModel

# Create your models here.


class AccountModel(models.Model):
    ACCOUNT_TYPE = [
        ("CA", "Checking Accounts"),
        ("SA", "Saving Accounts"),
    ]
    client = models.OneToOneField(
        UserModel, related_name="account", on_delete=models.CASCADE
    )
    agency = models.CharField(max_length=4, default="1201")
    number = models.CharField(max_length=7, primary_key=True)
    account_type = models.CharField(max_length=2, choices=ACCOUNT_TYPE)
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Agency: {self.agency}, Number: {self.number}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.generate_account_number()
            self.set_account_balance()
        super().save(*args, **kwargs)

    def generate_account_number(self):
        self.number = str(random.choice(range(1000000, 10000000)))

    def set_account_balance(self):
        self.balance = str(random.randint(2000, 20000))


class MortgageModel(models.Model):
    # type of mortgage x client score
    MORTGAGE_TYPE = [
        ("FHAL", "FHA Loan"),
        ("VALN", "VA Loans"),
        ("CVTL", "Conventional Loan"),
        ("JUBL", "Jumbo Loan"),
        ("UDAL", "USDA Loan"),
    ]

    DUE_DATES = [
        ("10", "ten"),
        ("05", "five"),
        ("17", "seventeen"),
        ("25", "twenty-five"),
    ]

    client = models.ForeignKey(
        UserModel, related_name="mortgage", on_delete=models.CASCADE
    )

    account = models.ForeignKey(
        AccountModel, related_name="mortgage", on_delete=models.CASCADE
    )

    mortgage_type = models.CharField(max_length=4, choices=MORTGAGE_TYPE)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    installment_price = models.DecimalField(max_digits=12, decimal_places=2)
    installment = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(12), MaxValueValidator(84)]
    )
    due_date = models.CharField(max_length=2, choices=DUE_DATES, default="25")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("client", "account"), name="one_client_account"
            )
        ]

    def save(self, *args, **kwargs):
        self.validate_loan()
        super().save(*args, **kwargs)

    def validate_loan(self):
        if self.client.score >= 580 and self.client.score < 600:
            self.mortgage = "FHAL"

        elif self.client.score >= 600 and self.client.score < 650:
            self.mortgage = "VALN"

        elif self.client.score >= 650 and self.client.score < 700:
            self.mortgage = "CVTL"

        elif self.client.score >= 700 and self.client.score < 900:
            self.mortgage = "JUBL"

        elif self.client.score >= 900 and self.client.score < 1000:
            self.mortgage = "UDAL"

        else:
            raise ValidationError("The loan is not available at this time.")
