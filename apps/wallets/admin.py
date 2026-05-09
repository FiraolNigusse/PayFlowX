from django.contrib import admin
from apps.wallets.models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Admin configuration for Wallet management.
    """
    list_display = ('id', 'owner', 'balance', 'currency', 'created_at', 'updated_at')
    search_fields = ('owner__email',)
    list_filter = ('currency',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        # Optimization: select_related to avoid N+1 queries for owner email
        return super().get_queryset(request).select_related('owner')
