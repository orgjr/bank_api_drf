from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import (
    AccountViewSet,
    AuthViewSet,
    IndexAPIView,
    MortgageViewSet,
    PaymentSlipViewSet,
    TransactionViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"account", AccountViewSet, basename="author")
router.register(r"mortgage", MortgageViewSet, basename="mortgage")
router.register(r"transaction", TransactionViewSet, basename="transaction")
router.register(r"user", UserViewSet, basename="user")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"payment_slip", PaymentSlipViewSet, basename="payment_slip")


urlpatterns = [
    path("", IndexAPIView.as_view(), name="index"),
    path("bank/", include(router.urls)),
]
