import datetime as dt
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone

from fake_cip.models import CIPPaymentSlipRegistryModel


class CIPPaymentSlipRegistryService:
    def validate_input(self, barcode, digitable_line, bank_code, amount):
        if len(barcode) != 44 or not barcode.isdigit():
            raise ValidationError("Barcode must have exactly 44 numeric digits")

        if barcode[:3] != bank_code:
            raise ValidationError("Bank code mismatch with barcode")

        clean_line = "".join(filter(str.isdigit, digitable_line))
        if len(clean_line) not in (47, 48):
            raise ValidationError("Invalid digitable line format")

        amount = Decimal(amount)

        if amount <= 0:
            raise ValidationError("Amount must be positive")

        valid_bank_codes = {
            # some examples.
            "120",  # skbank
            "001",  # Banco do Brasil S.A.
            "237",  # Bradesco S.A
            "077",  # Banco Inter S.A
        }

        if bank_code not in valid_bank_codes:
            raise ValidationError("bank code informed does not exists")

    def cip_register(self, barcode, digitable_line, bank_code, amount, name, due_date):
        self.validate_input(barcode, digitable_line, bank_code, amount)
        if CIPPaymentSlipRegistryModel.objects.filter(barcode=barcode).exists():
            raise ValidationError("Payment slip already registered")

        return CIPPaymentSlipRegistryModel.objects.create(
            barcode=barcode,
            digitable_line=digitable_line,
            bank_code=bank_code,
            amount=amount,
            beneficiary_name=name,
            due_date=due_date,
            status="PENDING",
        )

    def expire_if_needed(self, payment_slip):
        if payment_slip.status == "PENDING" and payment_slip.due_date < dt.date.today():
            payment_slip.status = "EXPIRED"
            payment_slip.save(update_fields=["status"])

    def get_by_barcode(self, barcode):
        try:
            payment_slip = CIPPaymentSlipRegistryModel.objects.get(barcode=barcode)
            self.expire_if_needed(payment_slip)

            return payment_slip

        except CIPPaymentSlipRegistryModel.DoesNotExist:
            raise ObjectDoesNotExist("Payment slip not found")

    def update_status(self, barcode, status, payment_date=None):
        ALLOWED_TRANSITIONS = {
            "PENDING": ["PAID", "EXPIRED", "CANCELLED"],
            "PAID": [],
            "EXPIRED": ["PAID"],
            "CANCELLED": [],
        }
        valid_status = ["PAID", "EXPIRED", "CANCELLED"]
        if not status or status not in valid_status:
            raise ValidationError(
                'The status provided is invalid. Only "PAID", "CANCELLED", and "EXPIRED" are accepted'
            )

        payment_slip = self.get_by_barcode(barcode)
        if payment_slip.status == "PAID" and status == "PAID":
            return payment_slip

        if payment_slip.status == "PAID":
            raise ValidationError("Payment slip already paid.")

        if status not in ALLOWED_TRANSITIONS[payment_slip.status]:
            raise ValidationError("Invalid status transition")

        if status == "PAID":
            if not payment_date:
                raise ValidationError(
                    "Payment date must be provided with format YYYY-MM-DD"
                )
            if payment_date > timezone.now().date():
                raise ValidationError("Future payment date")
            payment_slip.payment_date = dt.datetime.combine(payment_date, dt.time.min)

        payment_slip.status = status
        payment_slip.save()

        return payment_slip
