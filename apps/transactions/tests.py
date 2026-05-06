import pytest
from decimal import Decimal
from apps.users.models import User
from apps.wallets.services import WalletService
from apps.transactions.services import PaymentService
from apps.transactions.models import Transaction
from apps.transactions.tasks import process_transfer_task

@pytest.mark.django_db
class TestTransactionEngine:
    @pytest.fixture
    def user_a(self):
        from apps.users.services import IdentityService
        user = IdentityService.register_user(email="userA@example.com", password="password123")
        WalletService.update_balance(user.wallet.id, Decimal('100.00'))
        return user

    @pytest.fixture
    def user_b(self):
        from apps.users.services import IdentityService
        return IdentityService.register_user(email="userB@example.com", password="password123")

    def test_successful_transfer_initiation(self, user_a, user_b):
        txn = PaymentService.transfer(
            sender=user_a,
            receiver_email=user_b.email,
            amount=Decimal('50.00')
        )
        assert txn.status == Transaction.Status.PENDING
        assert txn.amount == Decimal('50.00')

    def test_insufficient_funds_failure(self, user_a, user_b):
        # We process the task directly to test the business logic
        txn = Transaction.objects.create(
            sender=user_a,
            receiver=user_b,
            amount=Decimal('200.00'), # More than user_a has
            transaction_type=Transaction.Type.TRANSFER,
            status=Transaction.Status.PENDING
        )
        
        # Manually trigger task logic without the delay
        process_transfer_task(txn.id)
        
        txn.refresh_from_db()
        assert txn.status == Transaction.Status.FAILED
        assert "Insufficient funds" in txn.failure_reason

    def test_idempotency_prevents_duplicate_initiation(self, user_a, user_b):
        key = "unique-transfer-123"
        
        # First call
        txn1 = PaymentService.transfer(user_a, user_b.email, Decimal('10.00'), idempotency_key=key)
        
        # Second call with same key
        txn2 = PaymentService.transfer(user_a, user_b.email, Decimal('10.00'), idempotency_key=key)
        
        assert txn1.id == txn2.id
        assert Transaction.objects.filter(idempotency_key=key).count() == 1
