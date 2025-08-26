from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from datetime import date, timedelta
from .models import Reservation, ReservationRoom


class ReservationRoomInline(admin.TabularInline):
    model = ReservationRoom
    extra = 1
    fields = ('room', 'rate', 'discount_amount', 'extra_charges', 'total_amount')
    readonly_fields = ('total_amount',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('room', 'room__room_type')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_number', 'guest_link', 'status_badge', 'check_in_date', 'check_out_date', 'nights', 'total_rooms', 'total_amount', 'booking_source', 'created_at')
    list_filter = ('status', 'booking_source', 'check_in_date', 'check_out_date', 'created_at')
    search_fields = ('reservation_number', 'guest__first_name', 'guest__last_name', 'guest__email')
    readonly_fields = ('reservation_number', 'created_at', 'updated_at', 'nights', 'total_rooms', 'total_amount')
    date_hierarchy = 'check_in_date'
    
    fieldsets = (
        ('Reservation Details', {
            'fields': ('reservation_number', 'guest', 'status', 'booking_source')
        }),
        ('Stay Information', {
            'fields': ('check_in_date', 'check_out_date', 'nights', 'adults', 'children')
        }),
        ('Summary', {
            'fields': ('total_rooms', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReservationRoomInline]
    actions = ['confirm_reservations', 'cancel_reservations', 'check_in_reservations']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('guest').prefetch_related('rooms')
    
    def guest_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:guests_guest_change', args=[obj.guest.id]),
            obj.guest.full_name
        )
    guest_link.short_description = 'Guest'
    guest_link.admin_order_field = 'guest__first_name'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'CONFIRMED': 'blue',
            'CHECKED_IN': 'green',
            'CHECKED_OUT': 'gray',
            'CANCELLED': 'red',
            'NO_SHOW': 'darkred'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def nights(self, obj):
        if obj.check_in_date and obj.check_out_date:
            nights = (obj.check_out_date - obj.check_in_date).days
            return f"{nights} nights"
        return "—"
    nights.short_description = 'Nights'
    
    def total_rooms(self, obj):
        count = obj.rooms.count()
        if count > 1:
            return format_html('<strong>{} rooms</strong>', count)
        return f"{count} room"
    total_rooms.short_description = 'Rooms'
    
    def total_amount(self, obj):
        total = obj.rooms.aggregate(total=Sum('total_amount'))['total'] or 0
        return format_html('<strong>${:,.2f}</strong>', total)
    total_amount.short_description = 'Total Amount'
    total_amount.admin_order_field = 'rooms__total_amount'
    
    def confirm_reservations(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='CONFIRMED')
        self.message_user(request, f'{updated} reservations confirmed.')
    confirm_reservations.short_description = 'Confirm selected reservations'
    
    def cancel_reservations(self, request, queryset):
        updated = queryset.exclude(status__in=['CANCELLED', 'CHECKED_OUT']).update(status='CANCELLED')
        self.message_user(request, f'{updated} reservations cancelled.')
    cancel_reservations.short_description = 'Cancel selected reservations'
    
    def check_in_reservations(self, request, queryset):
        today = date.today()
        updated = queryset.filter(
            status='CONFIRMED',
            check_in_date__lte=today
        ).update(status='CHECKED_IN')
        self.message_user(request, f'{updated} reservations checked in.')
    check_in_reservations.short_description = 'Check in selected reservations'
    
    # Custom filters
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Add summary statistics
        total_reservations = self.get_queryset(request).count()
        today = date.today()
        
        extra_context.update({
            'total_reservations': total_reservations,
            'todays_checkins': self.get_queryset(request).filter(
                check_in_date=today,
                status__in=['CONFIRMED', 'CHECKED_IN']
            ).count(),
            'todays_checkouts': self.get_queryset(request).filter(
                check_out_date=today,
                status='CHECKED_IN'
            ).count(),
            'pending_confirmations': self.get_queryset(request).filter(
                status='PENDING'
            ).count(),
        })
        
        return super().changelist_view(request, extra_context)


@admin.register(ReservationRoom)
class ReservationRoomAdmin(admin.ModelAdmin):
    list_display = ('reservation_link', 'room_link', 'reservation_dates', 'nights', 'rate', 'total_amount', 'status')
    list_filter = ('reservation__check_in_date', 'reservation__check_out_date', 'room__room_type', 'reservation__status')
    search_fields = ('reservation__reservation_number', 'room__number', 'reservation__guest__first_name', 'reservation__guest__last_name')
    readonly_fields = ('total_amount', 'nights', 'status')
    date_hierarchy = 'reservation__check_in_date'
    
    fieldsets = (
        ('Reservation Room Details', {
            'fields': ('reservation', 'room', 'rate')
        }),
        ('Pricing', {
            'fields': ('discount_amount', 'extra_charges', 'nights')
        }),
        ('Summary', {
            'fields': ('total_amount', 'status'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reservation', 'reservation__guest', 'room', 'room__room_type')
    
    def reservation_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:reservations_reservation_change', args=[obj.reservation.id]),
            obj.reservation.reservation_number
        )
    reservation_link.short_description = 'Reservation'
    reservation_link.admin_order_field = 'reservation__reservation_number'
    
    def room_link(self, obj):
        return format_html(
            '<a href="{}">{} ({})</a>',
            reverse('admin:rooms_room_change', args=[obj.room.id]),
            obj.room.number,
            obj.room.room_type.name
        )
    room_link.short_description = 'Room'
    room_link.admin_order_field = 'room__number'
    
    def reservation_dates(self, obj):
        return f"{obj.reservation.check_in_date} to {obj.reservation.check_out_date}"
    reservation_dates.short_description = 'Dates'
    reservation_dates.admin_order_field = 'reservation__check_in_date'
    
    def nights(self, obj):
        nights = obj.reservation.nights
        return f"{nights} nights"
    nights.short_description = 'Nights'
    
    def status(self, obj):
        return obj.reservation.get_status_display()
    status.short_description = 'Reservation Status'
    status.admin_order_field = 'reservation__status'
