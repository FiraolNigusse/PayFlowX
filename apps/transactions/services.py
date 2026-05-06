from django.db import transaction
from django.core.exceptions import ValidationError
from apps.transactions.models import Transaction
from apps.wallets.services import WalletService
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """
    Orchestrates financial fund movements.
    
    This service ensures all operations are atomic and idempotent. 
    Business logic (validation) is performed before state transitions.
    """

    @staticmethod
    def deposit(user, amount, idempotency_key=None):
        """
        Processes a direct fund injection into a user's wallet.
        
        Args:
            user (User): The recipient of the funds.
            amount (Decimal): Magnitude of the deposit.
            idempotency_key (str): Client-provided unique request identifier.
            
        Returns:
            Transaction: The finalized record of the deposit.
        """
        if idempotency_key:
            existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                logger.info(f"Idempotent hit for deposit: {idempotency_key}")
                return existing

        with transaction.atomic():
            # Ledger Entry (COMPLETED for synchronous deposits)
            txn = Transaction.objects.create(
                receiver=user,
                amount=amount,
                transaction_type=Transaction.Type.DEPOSIT,
                status=Transaction.Status.COMPLETED,
                idempotency_key=idempotency_key
            )
            
            # Balance Projection Update
            WalletService.update_balance(user.wallet.id, amount)
            
            logger.info(f"Deposit successful | User: {user.email} | Amount: {amount}")
            return txn

    @staticmethod
    def transfer(sender, receiver_email, amount, idempotency_key=None):
        """
        Initiates an asynchronous peer-to-peer transfer.
        
        The transfer is created in a PENDING state to ensure the API 
        remains non-blocking. The actual fund movement is offloaded 
        to a Celery worker.
        """
        # 1. Validation & Discovery
        receiver = User.objects.filter(email=receiver_email).first()
        if not receiver:
            logger.error(f"Transfer failed: Receiver {receiver_email} not found.")
            raise ValidationError("Target account not found.")
            
        if sender == receiver:
            raise ValidationError("Self-transfers are not permitted.")

        # 2. Strict Idempotency Validation
        if idempotency_key:
            existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                logger.warning(f"Duplicate transfer attempt blocked: {idempotency_key}")
                return existing

        # 3. Intent Persistence (Atomic)
        try:
            with transaction.atomic():
                txn = Transaction.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    transaction_type=Transaction.Type.TRANSFER,
                    status=Transaction.Status.PENDING,
                    idempotency_key=idempotency_key
                )
            
            # 4. Async Dispatch
            from apps.transactions.tasks import process_transfer_task
            process_transfer_task.delay(txn.id)
            
            logger.info(f"Transfer {txn.id} enqueued for processing.")
            return txn
            
        except Exception as e:
            # Handle race conditions where two threads might try to create the same key
            if "unique constraint" in str(e).lower() or "already exists" in str(e).lower():
                return Transaction.objects.get(idempotency_key=idempotency_key)
            raise e
