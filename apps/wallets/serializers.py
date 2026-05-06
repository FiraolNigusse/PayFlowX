from rest_framework import serializers
from apps.wallets.models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('id', 'balance', 'currency', 'updated_at')
        read_only_fields = fields
