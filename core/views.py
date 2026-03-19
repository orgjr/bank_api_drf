from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from core.serializer import (
    AccountSerializer,
    LoginSerializer,
    MortgageSerializer,
    TransactionSerializer,
    TransactionTransferSerializer,
    UserCreationSerializer,
)
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


class TransactionViewSet(ModelViewSet):
    queryset = TransactionModel.objects.all()
    serializer_class = TransactionSerializer


class TransactionTransferViewSet(ModelViewSet):
    queryset = TransactionModel.objects.all()
    serializer_class = TransactionTransferSerializer


class AuthViewSet(ViewSet):
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid email or password")

        login(request, user)
        return Response({"message": f"user {email} logged in."})

    @action(detail=False, methods=["post"])
    def logout(self, request):
        user = request.user
        logout(request)
        return Response({"message": f"{user.email} logged out of the system."})


class UserCreationViewSet(ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserCreationSerializer
