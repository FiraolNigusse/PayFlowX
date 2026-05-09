from django.contrib import admin
from apps.transactions.models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Transaction Audit Trail.
    """
    list_display = (
        'id', 'sender', 'receiver', 'amount', 
        'transaction_type', 'status', 'reference_id', 'created_at'
    )
    list_filter = ('status', 'transaction_type', 'created_at')
    search_fields = ('sender__email', 'receiver__email', 'reference_id', 'idempotency_key')
    ordering = ('-created_at',)
    
    # Make transactions read-only to preserve audit integrity
    readonly_fields = (
        'id', 'sender', 'receiver', 'amount', 'status', 
        'transaction_type', 'reference_id', 'idempotency_key', 
        'failure_reason', 'created_at', 'updated_at'
    )

    def has_add_permission(self, request):
        # Prevent manual transaction creation in admin to force use of the engine
        return False

    def get_queryset(self, request):
        # Optimization: select_related for both sender and receiver
        return super().get_queryset(request).select_related('sender', 'receiver')
