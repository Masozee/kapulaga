from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from datetime import date, datetime, timedelta
from .models import CheckIn, CheckOut, RoomKey


class RoomKeyInline(admin.TabularInline):
    model = RoomKey
    extra = 0
    fields = ('key_type', 'key_code', 'is_active', 'deactivated_at')
    readonly_fields = ('deactivated_at',)


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('reservation_link', 'guest_name', 'room_numbers', 'actual_time', 'status_badge', 'verified_by', 'deposit_paid')
    list_filter = ('actual_check_in_time', 'identity_verified', 'created_at')
    search_fields = ('reservation__reservation_number', 'reservation__guest__first_name', 'reservation__guest__last_name', 'verified_by')
    readonly_fields = ('created_at', 'updated_at', 'guest_name', 'room_numbers', 'status_badge', 'check_in_duration')
    date_hierarchy = 'actual_check_in_time'
    
    fieldsets = (
        ('Check-in Information', {
            'fields': ('reservation', 'actual_check_in_time', 'adults_count', 'children_count')
        }),
        ('Guest & Room Details', {
            'fields': ('guest_name', 'room_numbers'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('verified_by', 'check_in_duration', 'status_badge')
        }),
        ('Deposit & Verification', {
            'fields': ('deposit_paid', 'identity_verified', 'early_checkin_charge', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [RoomKeyInline]
    actions = ['process_check_in', 'verify_deposits']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reservation', 'reservation__guest').prefetch_related('reservation__rooms__room', 'keys')
    
    def reservation_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:reservations_reservation_change', args=[obj.reservation.id]),
            obj.reservation.reservation_number
        )
    reservation_link.short_description = 'Reservation'
    reservation_link.admin_order_field = 'reservation__reservation_number'
    
    def guest_name(self, obj):
        guest = obj.reservation.guest
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:guests_guest_change', args=[guest.id]),
            guest.full_name
        )
    guest_name.short_description = 'Guest'
    guest_name.admin_order_field = 'reservation__guest__first_name'
    
    def room_numbers(self, obj):
        rooms = [room.room.number for room in obj.reservation.rooms.all()]
        return ', '.join(rooms)
    room_numbers.short_description = 'Rooms'
    
    
    def actual_time(self, obj):
        if obj.actual_check_in_time:
            return obj.actual_check_in_time.strftime('%Y-%m-%d %H:%M')
        return '—'
    actual_time.short_description = 'Actual'
    actual_time.admin_order_field = 'actual_check_in_time'
    
    def status_badge(self, obj):
        if obj.actual_check_in_time:
            if obj.deposit_paid and obj.identity_verified:
                return format_html('<span style="color: green;">✅ Completed</span>')
            else:
                return format_html('<span style="color: orange;">⚠️ Incomplete</span>')
        else:
            return format_html('<span style="color: blue;">📅 Pending</span>')
    status_badge.short_description = 'Status'
    
    def check_in_duration(self, obj):
        if obj.actual_check_in_time:
            return obj.actual_check_in_time.strftime('%H:%M')
        return '—'
    check_in_duration.short_description = 'Check-in Time'
    
    def process_check_in(self, request, queryset):
        now = datetime.now()
        updated = 0
        for checkin in queryset.filter(actual_check_in_time__isnull=True):
            checkin.actual_check_in_time = now
            checkin.save()
            updated += 1
        self.message_user(request, f'Processed check-in for {updated} reservations.')
    process_check_in.short_description = 'Process check-in'
    
    def verify_deposits(self, request, queryset):
        updated = queryset.update(deposit_paid=True, identity_verified=True)
        self.message_user(request, f'Verified deposits for {updated} check-ins.')
    verify_deposits.short_description = 'Mark deposits as verified'


@admin.register(CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    list_display = ('reservation_link', 'guest_name', 'room_numbers', 'actual_time', 'status_badge', 'processed_by', 'final_bill_amount')
    list_filter = ('actual_check_out_time', 'payment_status', 'created_at')
    search_fields = ('check_in__reservation__reservation_number', 'check_in__reservation__guest__first_name', 'check_in__reservation__guest__last_name', 'processed_by')
    readonly_fields = ('created_at', 'updated_at', 'guest_name', 'room_numbers', 'status_badge', 'is_late', 'late_hours')
    date_hierarchy = 'actual_check_out_time'
    
    fieldsets = (
        ('Check-out Information', {
            'fields': ('check_in', 'actual_check_out_time')
        }),
        ('Guest & Room Details', {
            'fields': ('guest_name', 'room_numbers'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processed_by', 'status_badge', 'is_late', 'late_hours')
        }),
        ('Charges', {
            'fields': ('final_bill_amount', 'late_checkout_charge', 'damage_charge', 'payment_status', 'room_condition', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['process_check_out', 'apply_late_fees']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('check_in', 'check_in__reservation', 'check_in__reservation__guest').prefetch_related('check_in__reservation__rooms__room')
    
    def reservation_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:reservations_reservation_change', args=[obj.check_in.reservation.id]),
            obj.check_in.reservation.reservation_number
        )
    reservation_link.short_description = 'Reservation'
    reservation_link.admin_order_field = 'check_in__reservation__reservation_number'
    
    def guest_name(self, obj):
        guest = obj.check_in.reservation.guest
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:guests_guest_change', args=[guest.id]),
            guest.full_name
        )
    guest_name.short_description = 'Guest'
    guest_name.admin_order_field = 'check_in__reservation__guest__first_name'
    
    def room_numbers(self, obj):
        rooms = [room.room.number for room in obj.check_in.reservation.rooms.all()]
        return ', '.join(rooms)
    room_numbers.short_description = 'Rooms'
    
    def actual_time(self, obj):
        if obj.actual_check_out_time:
            return obj.actual_check_out_time.strftime('%Y-%m-%d %H:%M')
        return '—'
    actual_time.short_description = 'Actual'
    actual_time.admin_order_field = 'actual_check_out_time'
    
    def status_badge(self, obj):
        if obj.actual_check_out_time:
            if obj.late_checkout_charge > 0:
                return format_html('<span style="color: orange;">⏰ Late Check-out</span>')
            else:
                return format_html('<span style="color: green;">✅ Completed</span>')
        else:
            return format_html('<span style="color: blue;">📅 Scheduled</span>')
    status_badge.short_description = 'Status'
    
    def is_late(self, obj):
        return obj.late_checkout_charge > 0
    is_late.short_description = 'Late?'
    is_late.boolean = True
    
    def late_hours(self, obj):
        if obj.late_checkout_charge > 0:
            return format_html('<strong>${:.2f}</strong>', obj.late_checkout_charge)
        return '—'
    late_hours.short_description = 'Late Charge'
    
    def process_check_out(self, request, queryset):
        now = datetime.now()
        updated = 0
        for checkout in queryset.filter(actual_check_out_time__isnull=True):
            checkout.actual_check_out_time = now
            if checkout.scheduled_check_out_time and now > checkout.scheduled_check_out_time:
                checkout.late_checkout = True
                checkout.late_checkout_fee = 50.00  # Default late fee
            checkout.save()
            updated += 1
        self.message_user(request, f'Processed check-out for {updated} reservations.')
    process_check_out.short_description = 'Process check-out'
    
    def apply_late_fees(self, request, queryset):
        updated = 0
        for checkout in queryset.filter(late_checkout=True, late_checkout_fee__isnull=True):
            checkout.late_checkout_fee = 50.00
            checkout.save()
            updated += 1
        self.message_user(request, f'Applied late fees to {updated} check-outs.')
    apply_late_fees.short_description = 'Apply late checkout fees'


@admin.register(RoomKey)
class RoomKeyAdmin(admin.ModelAdmin):
    list_display = ('check_in_link', 'room_number', 'key_type', 'key_code', 'is_active', 'issued_date', 'deactivated_at')
    list_filter = ('key_type', 'is_active', 'issued_at', 'deactivated_at')
    search_fields = ('key_code', 'check_in__reservation__reservation_number', 'check_in__reservation__guest__first_name')
    readonly_fields = ('check_in_link', 'room_number', 'issued_date')
    
    fieldsets = (
        ('Key Information', {
            'fields': ('check_in', 'room', 'key_type', 'key_code', 'is_active')
        }),
        ('Status', {
            'fields': ('check_in_link', 'room_number', 'issued_date', 'deactivated_at')
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['deactivate_keys', 'reactivate_keys']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('check_in', 'check_in__reservation', 'check_in__reservation__guest').prefetch_related('check_in__reservation__rooms__room')
    
    def check_in_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:checkin_checkin_change', args=[obj.check_in.id]),
            obj.check_in.reservation.reservation_number
        )
    check_in_link.short_description = 'Check-in'
    
    def room_number(self, obj):
        rooms = [room.room.number for room in obj.check_in.reservation.rooms.all()]
        return ', '.join(rooms)
    room_number.short_description = 'Room(s)'
    
    def issued_date(self, obj):
        return obj.issued_at.strftime('%Y-%m-%d %H:%M')
    issued_date.short_description = 'Issued'
    issued_date.admin_order_field = 'issued_at'
    
    def deactivate_keys(self, request, queryset):
        now = datetime.now()
        updated = queryset.filter(is_active=True).update(is_active=False, deactivated_at=now)
        self.message_user(request, f'Deactivated {updated} room keys.')
    deactivate_keys.short_description = 'Deactivate selected keys'
    
    def reactivate_keys(self, request, queryset):
        updated = queryset.filter(is_active=False).update(is_active=True, deactivated_at=None)
        self.message_user(request, f'Reactivated {updated} room keys.')
    reactivate_keys.short_description = 'Reactivate selected keys'
