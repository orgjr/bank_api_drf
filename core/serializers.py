import datetime as dt

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from payment_slip.models import PaymentSlipModel
from products.models import AccountModel, MortgageModel
from transaction.models import TransactionModel
from user.models import UserModel


class AccountSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    class Meta:
        model = AccountModel
        fields = ["account_type", "info"]
        extra_kwargs = {"account_type": {"write_only": True}}

    def create(self, validated_data):
        request = self.context["request"]
        client = request.user
        account = AccountModel.objects.create(client=client, **validated_data)
        return account

    def get_info(self, obj):
        return {
            "Client": obj.client.email,
            "Agency": obj.agency,
            "Number": obj.number,
            "Balance": obj.balance,
            "Score": obj.client.score,
        }


class MortgageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MortgageModel
        fields = [
            "client",
            "account",
            "mortgage_type",
            "total_price",
            "installment",
            "due_date",
        ]


class TransactionTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionModel
        fields = ["recipient", "amount"]

    def create(self, validated_data):
        request = self.context["request"]
        transaction_type = validated_data.pop("transaction_type")

        transaction = TransactionModel(
            sender=request.user.account,
            transaction_type=transaction_type,
            **validated_data,
        )
        transaction.submit()
        return transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionModel
        fields = ["amount"]

    def create(self, validated_data):
        request = self.context["request"]
        transaction_type = validated_data.pop("transaction_type")

        transaction = TransactionModel(
            sender=request.user.account,
            transaction_type=transaction_type,
            **validated_data,
        )
        transaction.submit()
        return transaction


class GetTransactionSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    def validate(self, data):
        today = timezone.localdate()
        deadline = today - dt.timedelta(days=90)
        start_date = data["start_date"]
        end_date = data["end_date"]

        # Filtered transactions with a max interval of 90 days
        # only for local test
        # maybe will be improved
        if start_date < deadline or end_date < deadline:
            raise serializers.ValidationError("Max range is 90 days.")

        if start_date > today or end_date > today:
            raise serializers.ValidationError("Dates cannot be in the future.")

        if start_date > end_date:
            raise serializers.ValidationError("start_date must be before end_date.")

        return data


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])

        if user is None:
            raise serializers.ValidationError("invalid credentials")

        data["user"] = user
        return data


class PaymentSlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSlipModel
        fields = ["payer_name", "amount"]


class GetPaymentSlipSerializer(serializers.Serializer):
    payment_slip_number = serializers.CharField(max_length=51)

    def validate_payment_slip_number(self, value):
        if not value.isdigit():
            raise ValidationError("Only numeric values are allowed.")

        if len(value) not in [44, 51]:
            raise ValidationError("Use digitable line as payment slip identification.")

        return value
