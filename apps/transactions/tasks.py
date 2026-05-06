import time
import logging
from celery import shared_task
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.transactions.models import Transaction
from apps.wallets.services import WalletService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def process_transfer_task(self, transaction_id):
    """
    Executes the financial 'Double-Entry' logic for a pending transfer.
    
    This task is the heart of the asynchronous engine. It ensures that 
    money is atomically moved from the sender to the receiver while 
    maintaining high availability of the main API.
    
    Retry Strategy:
        Uses exponential backoff for transient failures (e.g., DB deadlocks).
    
    Lifecycle:
        PENDING -> PROCESSING -> COMPLETED | FAILED
    """
    logger.info(f"Worker processing Task: {transaction_id}")
    
    try:
        with transaction.atomic():
            # Acquire exclusive lock on the transaction record
            txn = Transaction.objects.select_for_update().get(id=transaction_id)
            
            if txn.status != Transaction.Status.PENDING:
                logger.warning(f"Task skipped: Transaction {transaction_id} is in {txn.status} state.")
                return
                
            txn.status = Transaction.Status.PROCESSING
            txn.save()

            # SIMULATION: Artificial latency to demonstrate non-blocking architecture
            time.sleep(3)

            sender = txn.sender
            receiver = txn.receiver

            # DOUBLE-ENTRY ATOMICITY
            try:
                # Debit Phase
                WalletService.update_balance(sender.wallet.id, -txn.amount)
                # Credit Phase
                WalletService.update_balance(receiver.wallet.id, txn.amount)
                
                txn.status = Transaction.Status.COMPLETED
                txn.save()
                logger.info(f"Ledger reconciliation successful for TXN: {transaction_id}")
                
            except ValidationError as ve:
                # Non-retryable logic error (e.g., Insufficient funds found at execution time)
                txn.status = Transaction.Status.FAILED
                txn.failure_reason = str(ve)
                txn.save()
                logger.error(f"Financial validation failed for TXN {transaction_id}: {str(ve)}")
                
    except Transaction.DoesNotExist:
        logger.error(f"Critical Error: Transaction {transaction_id} vanished from DB.")
    except Exception as exc:
        logger.warning(f"Transient system failure for TXN {transaction_id}. Scheduling retry.")
        # Triggers autoretry_for logic
        raise exc
