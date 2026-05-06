from django.urls import path
from apps.wallets.views import WalletDetailView

urlpatterns = [
    path('me/', WalletDetailView.as_view(), name='wallet-detail'),
]
