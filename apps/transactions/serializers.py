from rest_framework import serializers
from apps.transactions.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    receiver_email = serializers.EmailField(source='receiver.email', read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'id', 'sender_email', 'receiver_email', 'amount', 
            'status', 'transaction_type', 'reference_id', 
            'failure_reason', 'created_at'
        )
        read_only_fields = fields

class DepositRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=0.01)
    idempotency_key = serializers.CharField(required=False, max_length=255)

class TransferRequestSerializer(serializers.Serializer):
    receiver_email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=0.01)
    idempotency_key = serializers.CharField(required=False, max_length=255)
