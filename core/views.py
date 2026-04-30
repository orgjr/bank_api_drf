import datetime as dt

from django.contrib.auth import login, logout
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from core.serializers import (
    AccountSerializer,
    GetPaymentSlipSerializer,
    GetTransactionSerializer,
    LoginSerializer,
    MortgageSerializer,
    PaymentSlipSerializer,
    TransactionSerializer,
    TransactionTransferSerializer,
    UserCreationSerializer,
)
from payment_slip.models import PaymentSlipModel
from payment_slip.services.payment_slip_services import PaymentSlipService
from products.models import AccountModel, MortgageModel
from transaction.models import TransactionModel
from user.models import UserModel


# Create your views here.
class IndexAPIView(APIView):
    def get(self, request):
        return Response({"message": "Hello, from my bank API!"}, status=200)


class AccountViewSet(ModelViewSet):
    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer


class MortgageViewSet(ModelViewSet):
    queryset = MortgageModel.objects.all()
    serializer_class = MortgageSerializer


class TransactionViewSet(ViewSet):
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def transfer(self, request):
        serializer = TransactionTransferSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["transaction_type"] = "TF"
        transfer = serializer.save()
        return Response({"transfer": TransactionSerializer(transfer).data})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def payment(self, request):
        serializer = TransactionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["transaction_type"] = "PM"
        payment = serializer.save()
        return Response({"payment": TransactionSerializer(payment).data})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def withdraw(self, request):
        serializer = TransactionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["transaction_type"] = "WD"
        withdraw = serializer.save()
        return Response({"withdraw": TransactionSerializer(withdraw).data})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def deposit(self, request):
        serializer = TransactionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["transaction_type"] = "DP"
        deposit = serializer.save()
        return Response({"deposit": TransactionSerializer(deposit).data})

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def extract(self, request):
        serializer = GetTransactionSerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # converted to aware datetime for database query compatibility
        start_datetime = timezone.make_aware(
            dt.datetime.combine(serializer.validated_data["start_date"], dt.time.min)
        )

        end_datetime = timezone.make_aware(
            dt.datetime.combine(serializer.validated_data["end_date"], dt.time.max)
        )

        user_account = request.user.account.number

        transactions = TransactionModel.objects.filter(
            sender_id=user_account,
            date__range=[start_datetime, end_datetime],
        ).order_by("-date")

        if not transactions.exists():
            return Response(
                {"detail": "Client does not have any transactions."},
                status=200,
            )

        TYPE_MAP = {
            "WD": "withdraw",
            "PM": "payment",
            "DP": "deposit",
            "TF": "transfer",
        }
        data = [
            {
                "transaction_number": t.id,
                "sender": t.sender_id,
                "recipient": t.recipient_id,
                "type": TYPE_MAP.get(t.transaction_type, t.transaction_type),
                "amount": t.amount,
                "date": t.date,
            }
            for t in transactions
        ]

        return Response({"transactions": data})


class AuthViewSet(ViewSet):
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response({"message": "Logged in successfully."})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response({"message": "You logged out of the system."})


class UserViewSet(ViewSet):
    def create(self, request):
        serializer = UserCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user": user.email})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = get_object_or_404(UserModel, pk=request.user.pk)

        # support for users without an account
        try:
            if user.account:
                return Response(
                    {
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "agency": user.account.agency,
                        "account": user.account.number,
                        "balance": user.account.balance,
                    },
                    status=200,
                )

        except UserModel.account.RelatedObjectDoesNotExist:
            return Response(
                {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                }
            )


class PaymentSlipViewSet(ViewSet):
    def create(self, request):
        serializer = PaymentSlipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = PaymentSlipService.generate(serializer.validated_data)
        payment_slip = PaymentSlipModel.objects.create(**data)

        return Response(
            {
                "barcode": data["barcode"],
                "payer_name": payment_slip.payer_name,
                "amount": payment_slip.amount,
            },
            status=200,
        )

    @action(detail=False, methods=["GET"])
    def get(self, request):
        serializer = GetPaymentSlipSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payment_slip_number = serializer.validated_data["payment_slip_number"]

        payment_slip = PaymentSlipModel.objects.get(Q(barcode=payment_slip_number))

        if not payment_slip:
            return Response({"detail": "Payment slip not found."}, status=404)

        response_data = {
            # ===============================
            # IDENTIFICATION
            # ===============================
            "barcode": payment_slip.barcode,
            "digitable_line": payment_slip.digitable_line,
            "bank_code": payment_slip.bank_code,
            "currency_code": payment_slip.currency_code,
            "our_number": payment_slip.our_number,
            "document_number": payment_slip.document_number,
            # ===============================
            # VALUES AND DATES
            # ===============================
            "amount": payment_slip.amount,
            "due_date": payment_slip.due_date,
            "issue_date": payment_slip.issue_date,
            "processing_date": payment_slip.processing_date,
            "payment_date": payment_slip.payment_date,
            "discount_amount": payment_slip.discount_amount,
            "fine_amount": payment_slip.fine_amount,
            "interest_amount": payment_slip.interest_amount,
            # ===============================
            # BENEFICIARY
            # ===============================
            "beneficiary_name": payment_slip.beneficiary_name,
            "beneficiary_document": payment_slip.beneficiary_document,
            "beneficiary_agency": payment_slip.beneficiary_agency,
            "beneficiary_account": payment_slip.beneficiary_account,
            # ===============================
            # PAYER
            # ===============================
            "payer_name": payment_slip.payer_name,
            "payer_document": payment_slip.payer_document,
            "payer_address": payment_slip.payer_address,
            "payer_city": payment_slip.payer_city,
            "payer_state": payment_slip.payer_state,
            "payer_zipcode": payment_slip.payer_zipcode,
            # ===============================
            # STATUS AND CONTROL
            # ===============================
            "status": payment_slip.status,
            "instructions": payment_slip.instructions,
            "external_id": payment_slip.external_id,
            # ===============================
            # RELATIONSHIP
            # ===============================
            "transaction": payment_slip.transaction_id,
            # ===============================
            # CONTROL
            # ===============================
            "created_at": payment_slip.created_at,
            "updated_at": payment_slip.updated_at,
        }

        return Response({"detail": response_data}, status=200)
