from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from django.urls import reverse
from decimal import Decimal
from .models import PaymentMethod, Bill, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('payment_method', 'amount', 'status', 'transaction_id', 'payment_date')
    readonly_fields = ('transaction_id', 'payment_date')
    ordering = ('-payment_date',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'processing_fee_percentage', 'total_transactions', 'total_amount', 'avg_transaction', 'is_active', 'created_at')
    list_filter = ('is_active', 'processing_fee_percentage', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at', 'total_transactions', 'total_amount', 'avg_transaction')
    
    fieldsets = (
        ('Payment Method Information', {
            'fields': ('name', 'code', 'description', 'processing_fee_percentage', 'is_active')
        }),
        ('Transaction Statistics', {
            'fields': ('total_transactions', 'total_amount', 'avg_transaction'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_methods', 'deactivate_methods', 'update_processing_fees']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _total_transactions=Count('payment', distinct=True),
            _total_amount=Sum('payment__amount'),
            _avg_transaction=Avg('payment__amount')
        )
    
    def total_transactions(self, obj):
        count = getattr(obj, '_total_transactions', 0)
        if count > 0:
            try:
                url = reverse('admin:payments_payment_changelist')
                return format_html(
                    '<a href="{}?payment_method={}">{} transactions</a>',
                    str(url),
                    obj.id,
                    count
                )
            except (ValueError, TypeError, AttributeError):
                return f'{count} transactions'
        return '0 transactions'
    total_transactions.admin_order_field = '_total_transactions'
    total_transactions.short_description = 'Transactions'
    
    def total_amount(self, obj):
        amount = getattr(obj, '_total_amount', None)
        if amount is not None and amount > 0:
            try:
                return format_html('<strong>${:,.2f}</strong>', float(amount))
            except (ValueError, TypeError):
                return '$0.00'
        return '$0.00'
    total_amount.admin_order_field = '_total_amount'
    total_amount.short_description = 'Total Amount'
    
    def avg_transaction(self, obj):
        avg = getattr(obj, '_avg_transaction', None)
        if avg is not None and avg > 0:
            try:
                return format_html('${:,.2f}', float(avg))
            except (ValueError, TypeError):
                return '$0.00'
        return '$0.00'
    avg_transaction.admin_order_field = '_avg_transaction'
    avg_transaction.short_description = 'Avg Transaction'
    
    def activate_methods(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Activated {updated} payment methods.')
    activate_methods.short_description = 'Activate selected payment methods'
    
    def deactivate_methods(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {updated} payment methods.')
    deactivate_methods.short_description = 'Deactivate selected payment methods'
    
    def update_processing_fees(self, request, queryset):
        self.message_user(request, f'Processing fee update functionality can be implemented for {queryset.count()} methods.')
    update_processing_fees.short_description = 'Update processing fees'


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'reservation_link', 'guest_name', 'subtotal', 'tax_amount', 'service_charge', 'total_amount', 'payment_status_badge', 'balance_due', 'created_at')
    list_filter = ('status', 'tax_rate', 'service_charge_rate', 'created_at')
    search_fields = ('bill_number', 'reservation__reservation_number', 'reservation__guest__first_name', 'reservation__guest__last_name')
    readonly_fields = ('bill_number', 'created_at', 'updated_at', 'payment_status_badge', 'amount_paid', 'balance_due')
    
    fieldsets = (
        ('Bill Information', {
            'fields': ('bill_number', 'reservation', 'status')
        }),
        ('Amount Breakdown', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'service_charge_rate', 'service_charge', 'discount_amount', 'total_amount')
        }),
        ('Payment Status', {
            'fields': ('payment_status_badge', 'amount_paid', 'balance_due')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PaymentInline]
    actions = ['mark_paid', 'apply_discount', 'send_invoice']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reservation', 'reservation__guest')
    
    def reservation_link(self, obj):
        try:
            url = reverse('admin:reservations_reservation_change', args=[obj.reservation.id])
            return format_html(
                '<a href="{}">{}</a>',
                str(url),
                str(obj.reservation.reservation_number)
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.reservation.reservation_number) if obj.reservation else 'No Reservation'
    reservation_link.short_description = 'Reservation'
    reservation_link.admin_order_field = 'reservation__reservation_number'
    
    def guest_name(self, obj):
        try:
            guest = obj.reservation.guest
            url = reverse('admin:guests_guest_change', args=[guest.id])
            return format_html(
                '<a href="{}">{}</a>',
                str(url),
                str(guest.full_name)
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.reservation.guest.full_name) if obj.reservation and obj.reservation.guest else 'No Guest'
    guest_name.short_description = 'Guest'
    guest_name.admin_order_field = 'reservation__guest__first_name'
    
    def payment_status_badge(self, obj):
        try:
            status = obj.payment_status
            colors = {
                'PENDING': 'red',
                'PARTIAL': 'orange',
                'PAID': 'green'
            }
            icons = {
                'PENDING': '❌',
                'PARTIAL': '⚠️',
                'PAID': '✅'
            }
            color = colors.get(status, 'gray')
            icon = icons.get(status, '💵')
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {}</span>',
                str(color), str(icon), str(status.replace('_', ' ').title())
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.payment_status) if hasattr(obj, 'payment_status') else 'Unknown'
    payment_status_badge.short_description = 'Payment Status'
    
    def balance_due(self, obj):
        try:
            balance = obj.balance_due
            if balance > 0:
                return format_html('<strong style="color: red;">${:,.2f}</strong>', float(balance))
            return '$0.00'
        except (ValueError, TypeError, AttributeError):
            return '$0.00'
    balance_due.short_description = 'Balance Due'
    
    def mark_paid(self, request, queryset):
        # This would typically create payment records
        pending_bills = queryset.exclude(status='PAID')
        self.message_user(request, f'{pending_bills.count()} bills can be marked as paid.')
    mark_paid.short_description = 'Mark as paid'
    
    def apply_discount(self, request, queryset):
        # Placeholder for discount functionality
        self.message_user(request, f'Discount functionality can be applied to {queryset.count()} bills.')
    apply_discount.short_description = 'Apply discount'
    
    def send_invoice(self, request, queryset):
        # Placeholder for invoice sending functionality
        self.message_user(request, f'Invoice sending functionality for {queryset.count()} bills.')
    send_invoice.short_description = 'Send invoice'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'bill_link', 'guest_name', 'payment_method', 'amount', 'processing_fee', 'status_badge', 'processed_by', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date', 'processed_by')
    search_fields = ('transaction_id', 'bill__bill_number', 'bill__reservation__guest__first_name', 'reference_number')
    readonly_fields = ('transaction_id', 'payment_date', 'created_at', 'updated_at', 'bill_link', 'guest_name')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('transaction_id', 'bill', 'payment_method', 'amount', 'processing_fee')
        }),
        ('Status & Processing', {
            'fields': ('status', 'processed_by')
        }),
        ('References', {
            'fields': ('reference_number', 'bill_link', 'guest_name'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_failed', 'refund_payments']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bill', 'bill__reservation', 'bill__reservation__guest', 'payment_method')
    
    def bill_link(self, obj):
        try:
            url = reverse('admin:payments_bill_change', args=[obj.bill.id])
            return format_html(
                '<a href="{}">{}</a>',
                str(url),
                str(obj.bill.bill_number)
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.bill.bill_number) if obj.bill else 'No Bill'
    bill_link.short_description = 'Bill'
    bill_link.admin_order_field = 'bill__bill_number'
    
    def guest_name(self, obj):
        try:
            guest = obj.bill.reservation.guest
            url = reverse('admin:guests_guest_change', args=[guest.id])
            return format_html(
                '<a href="{}">{}</a>',
                str(url),
                str(guest.full_name)
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.bill.reservation.guest.full_name) if obj.bill and obj.bill.reservation and obj.bill.reservation.guest else 'No Guest'
    guest_name.short_description = 'Guest'
    guest_name.admin_order_field = 'bill__reservation__guest__first_name'
    
    def status_badge(self, obj):
        try:
            colors = {
                'PENDING': 'orange',
                'COMPLETED': 'green',
                'FAILED': 'red',
                'CANCELLED': 'gray',
                'REFUNDED': 'purple'
            }
            icons = {
                'PENDING': '🔄',
                'COMPLETED': '✅',
                'FAILED': '❌',
                'CANCELLED': '⛔',
                'REFUNDED': '↩️'
            }
            color = colors.get(obj.status, 'black')
            icon = icons.get(obj.status, '💳')
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {}</span>',
                str(color), str(icon), str(obj.get_status_display())
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.get_status_display()) if hasattr(obj, 'get_status_display') else str(obj.status) if hasattr(obj, 'status') else 'Unknown'
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='COMPLETED')
        self.message_user(request, f'Marked {updated} payments as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_failed(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='FAILED')
        self.message_user(request, f'Marked {updated} payments as failed.')
    mark_failed.short_description = 'Mark as failed'
    
    def refund_payments(self, request, queryset):
        completed_payments = queryset.filter(status='COMPLETED')
        self.message_user(request, f'{completed_payments.count()} payments can be refunded.')
    refund_payments.short_description = 'Process refunds'
