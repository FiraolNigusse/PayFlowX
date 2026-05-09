from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from drf_spectacular.utils import extend_schema
from apps.transactions.models import Transaction
from apps.transactions.serializers import (
    TransactionSerializer, DepositRequestSerializer, TransferRequestSerializer
)
from apps.transactions.services import PaymentService

class TransactionHistoryView(generics.ListAPIView):
    """
    Returns a paginated list of transactions.
    Supports RBAC: Admins see all; Users see only their own history.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Transaction.objects.all()
        return Transaction.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )

class DepositView(views.APIView):
    """
    Endpoint for simulating external fund injections.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DepositRequestSerializer,
        responses={201: TransactionSerializer},
    )
    def post(self, request):
        serializer = DepositRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            txn = PaymentService.deposit(
                user=request.user,
                **serializer.validated_data
            )
            return Response(
                TransactionSerializer(txn).data,
                status=status.HTTP_201_CREATED
            )
        except (DjangoValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TransferView(views.APIView):
    """
    Initiates an asynchronous peer-to-peer fund transfer.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TransferRequestSerializer,
        responses={201: TransactionSerializer},
    )
    def post(self, request):
        serializer = TransferRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            txn = PaymentService.transfer(
                sender=request.user,
                **serializer.validated_data
            )
            return Response(
                TransactionSerializer(txn).data,
                status=status.HTTP_201_CREATED
            )
        except (DjangoValidationError, DRFValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
