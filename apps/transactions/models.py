import uuid
from django.db import models
from django.conf import settings

class Transaction(models.Model):
    """
    An immutable record of a financial event (Deposit, Transfer, or Withdrawal).
    
    This model serves as the system's ledger. Once a record is COMPLETED or FAILED, 
    it should never be modified. It includes idempotency tracking to prevent 
    duplicate processing in distributed environments.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class Type(models.TextChoices):
        DEPOSIT = 'deposit', 'Deposit'
        TRANSFER = 'transfer', 'Transfer'
        WITHDRAWAL = 'withdrawal', 'Withdrawal'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sent_transactions',
        null=True, # Null for deposits
        blank=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='received_transactions',
        null=True, # Null for withdrawals
        blank=True
    )

    # Core Data
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=Type.choices
    )
    
    # Integrity & Traceability
    reference_id = models.CharField(
        max_length=100, 
        unique=True, 
        default=uuid.uuid4,
        db_index=True
    )
    idempotency_key = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        db_index=True
    )
    failure_reason = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'transaction_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type.upper()} | {self.amount} | {self.status}"
