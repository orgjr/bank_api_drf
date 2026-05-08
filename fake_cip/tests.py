import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

# Create your tests here.
from fake_cip.services.cip_registry_service import CIPPaymentSlipRegistryService
from payment_slip.models import PaymentSlipModel
from payment_slip.services.payment_slip_services import PaymentSlipService


# Create your tests here.
class CIPExpiredStatusCase(TestCase):
    def setUp(self):
        payload = {
            "payer_name": "Brenda",
            "amount": "225.54",
        }
        pay_model = PaymentSlipService.generate(payload)
        pay_model = PaymentSlipModel.objects.create(**pay_model)
        pay_model.due_date = datetime.date(2026, 5, 1)
        pay_model.save()

        pay_obj = CIPPaymentSlipRegistryService().cip_register(
            barcode=pay_model.barcode,
            digitable_line=pay_model.digitable_line,
            bank_code=pay_model.barcode[:3],
            amount=pay_model.amount,
            name=pay_model.payer_name,
            due_date=pay_model.due_date,
        )
        pay_obj.due_date = datetime.date(2026, 5, 1)
        pay_obj.save()

    def test_cip_payment_slip_change_status_with_get(self):
        pay_model = PaymentSlipModel.objects.get(payer_name="Brenda")
        barcode = pay_model.barcode
        cip_payment_slip = CIPPaymentSlipRegistryService().get_by_barcode(barcode)
        self.assertEqual(cip_payment_slip.status, "EXPIRED")


class CIPPendingStatusErrorCase(TestCase):
    def setUp(self):
        payload = {
            "payer_name": "Brenda",
            "amount": "225.54",
        }
        pay_model = PaymentSlipService.generate(payload)
        pay_model = PaymentSlipModel.objects.create(**pay_model)
        pay_model.due_date = datetime.date(2026, 5, 1)  # expired status ok
        pay_model.save()

        pay_obj = CIPPaymentSlipRegistryService().cip_register(
            barcode=pay_model.barcode,
            digitable_line=pay_model.digitable_line,
            bank_code=pay_model.barcode[:3],
            amount=pay_model.amount,
            name=pay_model.payer_name,
            due_date=pay_model.due_date,
        )
        pay_obj.due_date = datetime.date(2026, 5, 1)  # expired status ok
        pay_obj.save()

    def test_cip_payment_slip_change_status_with_get(self):
        pay_model = PaymentSlipModel.objects.get(payer_name="Brenda")
        barcode = pay_model.barcode

        with self.assertRaises(ValidationError) as context:
            CIPPaymentSlipRegistryService().update_status(barcode, "PENDING")

        self.assertEqual(
            str(context.exception.message),
            'The status provided is invalid. Only "PAID", "CANCELED", and "EXPIRED" are accepted.',
        )


class CIPTransitionStatusErrorCase(TestCase):
    def setUp(self):
        payload = {
            "payer_name": "Brenda",
            "amount": "225.54",
        }
        pay_model = PaymentSlipService.generate(payload)
        pay_model = PaymentSlipModel.objects.create(**pay_model)
        pay_model.status = "CANCELLED"
        pay_model.save()

        pay_obj = CIPPaymentSlipRegistryService().cip_register(
            barcode=pay_model.barcode,
            digitable_line=pay_model.digitable_line,
            bank_code=pay_model.barcode[:3],
            amount=pay_model.amount,
            name=pay_model.payer_name,
            due_date=pay_model.due_date,
        )
        pay_obj.status = "CANCELLED"
        pay_obj.save()

    def test_cip_payment_slip_change_status_with_get(self):
        pay_model = PaymentSlipModel.objects.get(payer_name="Brenda")
        barcode = pay_model.barcode

        with self.assertRaises(ValidationError) as context:
            CIPPaymentSlipRegistryService().update_status(
                barcode=barcode, status="EXPIRED"
            )

        self.assertEqual(context.exception.message, "Invalid status transition.")
