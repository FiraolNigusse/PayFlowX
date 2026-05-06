from django.db import transaction
from apps.users.models import User
from apps.wallets.services import WalletService
import logging

logger = logging.getLogger(__name__)

class IdentityService:
    """
    Manages user identity lifecycle and initial financial provisioning.
    """

    @staticmethod
    @transaction.atomic
    def register_user(email, password, first_name='', last_name='', role=User.Role.USER):
        """
        Orchestrates the creation of a new User and their associated Wallet.
        
        This operation is wrapped in a database transaction to ensure that 
        we never have a 'zombie user' (a user without a wallet).
        
        Returns:
            User: The newly created and provisioned user instance.
        """
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # Provisioning the primary financial account (Wallet)
        WalletService.create_wallet(user=user)
        
        logger.info(f"System Onboarding Success | Email: {email} | Role: {role}")
        return user
