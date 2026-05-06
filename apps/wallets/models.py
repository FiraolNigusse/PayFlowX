from django.db import models
from django.conf import settings
from django.db.models import CheckConstraint, Q
from decimal import Decimal

class Wallet(models.Model):
    """
    Represents a user's digital financial account.
    
    Includes a database-level CheckConstraint to ensure that the balance 
    can never drop below zero, providing an extra layer of safety 
    beyond the application's service logic.
    """
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0.00')
    )
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(balance__gte=0),
                name='balance_cannot_be_negative'
            )
        ]

    def __str__(self):
        return f"{self.owner.email}'s Wallet ({self.balance} {self.currency})"
