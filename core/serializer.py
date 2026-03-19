from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        fields = ["recipient", "transaction_type", "amount"]

    def create(self, validated_data):
        request = self.context["request"]
        transaction_type = validated_data.get("transaction_type")
        if transaction_type != "TF":
            raise ValidationError(
                {"error": "Not a transfer transaction. Try it in /bank/transaction/"}
            )
        sender = request.user.account

        transaction = TransactionModel(sender=sender, **validated_data)
        transaction.submit()
        return transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionModel
        fields = ["transaction_type", "amount"]

    def create(self, validated_data):
        request = self.context["request"]
        transaction_type = validated_data.get("transaction_type")
        if transaction_type == "TF":
            raise ValidationError(
                {
                    "error": "Not a valid transaction. Try it in /bank/transaction_transfer/"
                }
            )
        sender = request.user.account

        transaction = TransactionModel(sender=sender, **validated_data)
        transaction.submit()
        return transaction


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
