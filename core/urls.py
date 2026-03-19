from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import (
    AccountViewSet,
    AuthViewSet,
    IndexAPIView,
    MortgageViewSet,
    TransactionTransferViewSet,
    TransactionViewSet,
    UserCreationViewSet,
)

router = DefaultRouter()
router.register(r"account", AccountViewSet, basename="author")
router.register(r"mortgage", MortgageViewSet, basename="mortgage")
router.register(r"transaction", TransactionViewSet, basename="transaction")
router.register(
    r"transaction_transfer", TransactionTransferViewSet, basename="transaction_transfer"
)
router.register(r"user_creation", UserCreationViewSet, basename="user_creation")
router.register(r"auth", AuthViewSet, basename="auth")


urlpatterns = [
    path("", IndexAPIView.as_view(), name="index"),
    path("bank/", include(router.urls)),
]
