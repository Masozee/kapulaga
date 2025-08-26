from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.urls import reverse
from .models import Guest, GuestDocument


class GuestDocumentInline(admin.TabularInline):
    model = GuestDocument
    extra = 1
    fields = ('document_type', 'document_number', 'issuing_country', 'issue_date', 'expiry_date', 'is_verified')
    readonly_fields = ('created_at',)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'nationality', 'loyalty_level', 'total_visits', 'total_spent', 'last_visit', 'is_vip')
    list_filter = ('nationality', 'gender', 'created_at', 'loyalty_points')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'total_visits', 'total_spent', 'last_visit', 'loyalty_level')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender', 'nationality')
        }),
        ('Address', {
            'fields': ('address', 'city', 'country', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Loyalty & Preferences', {
            'fields': ('loyalty_points', 'loyalty_level', 'preferences', 'is_vip'),
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_visits', 'total_spent', 'last_visit'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [GuestDocumentInline]
    actions = ['add_loyalty_points', 'reset_loyalty_points', 'mark_as_vip']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Annotate with reservation statistics
        queryset = queryset.annotate(
            _total_visits=Count('reservations', distinct=True),
            _total_spent=Sum('reservations__bill__total_amount')
        ).select_related()
        return queryset
    
    def total_visits(self, obj):
        count = getattr(obj, '_total_visits', 0)
        if count > 0:
            try:
                url = reverse('admin:reservations_reservation_changelist')
                return format_html(
                    '<a href="{}?guest={}">{} visits</a>',
                    str(url),
                    obj.id,
                    count
                )
            except (ValueError, TypeError, AttributeError):
                return f'{count} visits'
        return '0 visits'
    total_visits.admin_order_field = '_total_visits'
    total_visits.short_description = 'Total Visits'
    
    def total_spent(self, obj):
        amount = getattr(obj, '_total_spent', None)
        if amount is not None and amount > 0:
            try:
                return format_html('<strong>${:,.2f}</strong>', float(amount))
            except (ValueError, TypeError):
                return '$0.00'
        return '$0.00'
    total_spent.admin_order_field = '_total_spent'
    total_spent.short_description = 'Total Spent'
    
    def last_visit(self, obj):
        last_reservation = obj.reservations.order_by('-check_in_date').first()
        if last_reservation:
            try:
                url = reverse('admin:reservations_reservation_change', args=[last_reservation.id])
                date_str = last_reservation.check_in_date.strftime('%Y-%m-%d')
                return format_html(
                    '<a href="{}">{}</a>',
                    str(url),
                    str(date_str)
                )
            except (ValueError, TypeError, AttributeError):
                return str(last_reservation.check_in_date.strftime('%Y-%m-%d'))
        return 'Never'
    last_visit.short_description = 'Last Visit'
    
    def loyalty_level(self, obj):
        points = obj.loyalty_points
        if points >= 1000:
            level = "Platinum"
            color = "purple"
        elif points >= 500:
            level = "Gold"
            color = "gold"
        elif points >= 100:
            level = "Silver"
            color = "silver"
        else:
            level = "Bronze"
            color = "brown"
        
        try:
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span> ({}pts)',
                str(color), str(level), points
            )
        except (ValueError, TypeError):
            return f'{level} ({points}pts)'
    loyalty_level.short_description = 'Loyalty Level'
    
    def is_vip(self, obj):
        # VIP if they have >= 5 visits or spent >= $5000 or loyalty points >= 500
        visits = getattr(obj, '_total_visits', 0)
        spent = getattr(obj, '_total_spent', 0) or 0
        
        if visits >= 5 or spent >= 5000 or obj.loyalty_points >= 500:
            try:
                return format_html('<span style="color: gold;">⭐ VIP</span>')
            except (ValueError, TypeError):
                return '⭐ VIP'
        return '—'
    is_vip.short_description = 'VIP Status'
    
    def add_loyalty_points(self, request, queryset):
        for guest in queryset:
            guest.loyalty_points += 50
            guest.save()
        self.message_user(request, f'Added 50 loyalty points to {queryset.count()} guests.')
    add_loyalty_points.short_description = 'Add 50 loyalty points'
    
    def reset_loyalty_points(self, request, queryset):
        queryset.update(loyalty_points=0)
        self.message_user(request, f'Reset loyalty points for {queryset.count()} guests.')
    reset_loyalty_points.short_description = 'Reset loyalty points'
    
    def mark_as_vip(self, request, queryset):
        for guest in queryset:
            if guest.loyalty_points < 500:
                guest.loyalty_points = 500
                guest.save()
        self.message_user(request, f'Marked {queryset.count()} guests as VIP.')
    mark_as_vip.short_description = 'Mark as VIP (set 500+ points)'


@admin.register(GuestDocument)
class GuestDocumentAdmin(admin.ModelAdmin):
    list_display = ('guest', 'document_type', 'document_number', 'issue_date', 'expiry_date', 'is_expired', 'created_at')
    list_filter = ('document_type', 'issue_date', 'expiry_date', 'issuing_country')
    search_fields = ('guest__first_name', 'guest__last_name', 'document_number', 'issuing_country')
    readonly_fields = ('created_at', 'updated_at', 'is_expired')
    
    fieldsets = (
        ('Document Information', {
            'fields': ('guest', 'document_type', 'document_number', 'issuing_country', 'is_verified')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date', 'is_expired')
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        try:
            if obj.is_expired():
                return format_html('<span style="color: red;">⚠️ Expired</span>')
            elif obj.expiry_date and (obj.expiry_date - obj.expiry_date.today()).days <= 30:
                return format_html('<span style="color: orange;">⚠️ Expires Soon</span>')
            return format_html('<span style="color: green;">✅ Valid</span>')
        except (ValueError, TypeError, AttributeError):
            if hasattr(obj, 'is_expired') and callable(obj.is_expired):
                if obj.is_expired():
                    return '⚠️ Expired'
                elif obj.expiry_date:
                    return '✅ Valid'
            return 'Unknown'
    is_expired.short_description = 'Status'
