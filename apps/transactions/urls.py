from django.urls import path
from apps.transactions.views import TransactionHistoryView, DepositView, TransferView

urlpatterns = [
    path('', TransactionHistoryView.as_view(), name='transaction-history'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('transfer/', TransferView.as_view(), name='transfer'),
]
