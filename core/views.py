from django.contrib.auth import login, logout
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from core.serializers import (
    AccountSerializer,
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
        user = request.user
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


class PaymentSlipViewSet(ViewSet):
    def create(self, request):
        serializer = PaymentSlipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = PaymentSlipService.generate(serializer.validated_data)
        payment_slip = PaymentSlipModel.objects.create(**data)

        return Response(PaymentSlipSerializer(payment_slip).data)
