from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.db.models import Count
from .models import RoomType, Room


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'max_occupancy', 'total_rooms', 'available_rooms', 'occupied_rooms', 'is_active', 'created_at')
    list_filter = ('is_active', 'max_occupancy', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'total_rooms', 'available_rooms', 'occupied_rooms')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'base_price', 'max_occupancy', 'is_active')
        }),
        ('Room Statistics', {
            'fields': ('total_rooms', 'available_rooms', 'occupied_rooms'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _total_rooms=Count('room', distinct=True),
            _available_rooms=Count('room', filter=models.Q(room__status='AVAILABLE'), distinct=True),
            _occupied_rooms=Count('room', filter=models.Q(room__status='OCCUPIED'), distinct=True)
        )
        return queryset
    
    def total_rooms(self, obj):
        return getattr(obj, '_total_rooms', 0)
    total_rooms.admin_order_field = '_total_rooms'
    total_rooms.short_description = 'Total Rooms'
    
    def available_rooms(self, obj):
        try:
            count = getattr(obj, '_available_rooms', 0)
            return format_html('<span style="color: green;">{}</span>', str(count))
        except (ValueError, TypeError, AttributeError):
            return '0'
    available_rooms.admin_order_field = '_available_rooms'
    available_rooms.short_description = 'Available'
    
    def occupied_rooms(self, obj):
        try:
            count = getattr(obj, '_occupied_rooms', 0)
            return format_html('<span style="color: red;">{}</span>', str(count))
        except (ValueError, TypeError, AttributeError):
            return '0'
    occupied_rooms.admin_order_field = '_occupied_rooms'
    occupied_rooms.short_description = 'Occupied'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'room_type', 'floor', 'status_badge', 'is_available', 'current_guest', 'created_at')
    list_filter = ('status', 'room_type', 'floor', 'created_at')
    search_fields = ('number', 'room_type__name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'current_guest', 'is_available')
    list_editable = ()
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'room_type', 'floor', 'status', 'notes')
        }),
        ('Current Status', {
            'fields': ('is_available', 'current_guest'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_available', 'mark_maintenance', 'mark_out_of_order']
    
    def status_badge(self, obj):
        try:
            colors = {
                'AVAILABLE': 'green',
                'OCCUPIED': 'red',
                'MAINTENANCE': 'orange',
                'OUT_OF_ORDER': 'darkred',
                'RESERVED': 'blue'
            }
            color = colors.get(obj.status, 'gray')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                str(color),
                str(obj.get_status_display())
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.status) if hasattr(obj, 'status') else 'Unknown'
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def current_guest(self, obj):
        try:
            # Get current reservation for this room
            current_reservation = obj.reservationroom_set.filter(
                reservation__status__in=['CONFIRMED', 'CHECKED_IN']
            ).first()
            
            if current_reservation:
                guest = current_reservation.reservation.guest
                return format_html(
                    '<a href="/admin/guests/guest/{}/change/">{}</a>',
                    str(guest.id),
                    str(guest.full_name)
                )
            return 'No guest'
        except (ValueError, TypeError, AttributeError):
            return 'No guest'
    current_guest.short_description = 'Current Guest'
    
    def mark_available(self, request, queryset):
        updated = queryset.update(status='AVAILABLE')
        self.message_user(request, f'{updated} rooms marked as available.')
    mark_available.short_description = 'Mark selected rooms as available'
    
    def mark_maintenance(self, request, queryset):
        updated = queryset.update(status='MAINTENANCE')
        self.message_user(request, f'{updated} rooms marked for maintenance.')
    mark_maintenance.short_description = 'Mark selected rooms for maintenance'
    
    def mark_out_of_order(self, request, queryset):
        updated = queryset.update(status='OUT_OF_ORDER')
        self.message_user(request, f'{updated} rooms marked as out of order.')
    mark_out_of_order.short_description = 'Mark selected rooms as out of order'


# Custom admin site configuration
admin.site.site_header = 'Hotel Management System'
admin.site.site_title = 'Hotel Admin'
admin.site.index_title = 'Hotel Administration'
