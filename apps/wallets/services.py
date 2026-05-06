from django.db import transaction
from django.core.exceptions import ValidationError
from apps.wallets.models import Wallet
from decimal import Decimal

class WalletService:
    """
    Handles core ledger balance adjustments with high-concurrency safety.
    """

    @staticmethod
    def create_wallet(user, currency='USD'):
        """
        Provision a new financial account for a user.
        
        Args:
            user (User): The account owner.
            currency (str): Three-letter ISO currency code.
        """
        wallet, created = Wallet.objects.get_or_create(
            owner=user,
            defaults={'balance': Decimal('0.00'), 'currency': currency}
        )
        return wallet

    @staticmethod
    @transaction.atomic
    def update_balance(wallet_id, amount):
        """
        Safely modifies a wallet balance using row-level pessimistic locking.
        
        This method uses `select_for_update` to prevent the 'Lost Update' problem 
        in high-concurrency environments. The database row is locked until 
         the transaction is committed or rolled back.
        
        Raises:
            ValidationError: If the resulting balance would be negative.
        """
        # CRITICAL: Row-level lock acquisition
        wallet = Wallet.objects.select_for_update().get(id=wallet_id)
        
        new_balance = wallet.balance + amount
        
        if new_balance < 0:
            raise ValidationError(f"Insufficient funds for wallet ID: {wallet_id}")
            
        wallet.balance = new_balance
        wallet.save()
        
        return wallet
