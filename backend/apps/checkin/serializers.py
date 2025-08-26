from rest_framework import serializers
from django.utils import timezone
from .models import CheckIn, RoomKey


class RoomKeySerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.number', read_only=True)
    room_type = serializers.CharField(source='room.room_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RoomKey
        fields = [
            'id', 'room', 'room_number', 'room_type', 'key_code',
            'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CheckInSerializer(serializers.ModelSerializer):
    reservation_number = serializers.CharField(source='reservation.reservation_number', read_only=True)
    guest_name = serializers.CharField(source='reservation.guest.full_name', read_only=True)
    guest_email = serializers.CharField(source='reservation.guest.email', read_only=True)
    guest_phone = serializers.CharField(source='reservation.guest.phone', read_only=True)
    room_assignments = serializers.SerializerMethodField()
    keys_assigned = serializers.SerializerMethodField()
    total_keys = serializers.SerializerMethodField()
    nights_stayed = serializers.SerializerMethodField()
    
    class Meta:
        model = CheckIn
        fields = [
            'id', 'reservation', 'reservation_number', 'guest_name', 'guest_email',
            'guest_phone', 'check_in_time', 'check_out_time', 'actual_checkout_time',
            'early_checkout', 'late_checkout', 'special_requests', 'notes',
            'created_at', 'updated_at', 'room_assignments', 'keys_assigned',
            'total_keys', 'nights_stayed'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_room_assignments(self, obj):
        """Get room assignments for this check-in"""
        rooms = []
        for room_reservation in obj.reservation.rooms.all():
            rooms.append({
                'room_id': room_reservation.room.id,
                'room_number': room_reservation.room.number,
                'room_type': room_reservation.room.room_type.name,
                'floor': room_reservation.room.floor,
                'rate': float(room_reservation.rate),
                'status': room_reservation.room.status
            })
        return rooms

    def get_keys_assigned(self, obj):
        """Get keys assigned for this check-in"""
        keys = []
        for room_reservation in obj.reservation.rooms.all():
            room_keys = RoomKey.objects.filter(
                room=room_reservation.room,
                status='ACTIVE'
            )
            for key in room_keys:
                keys.append({
                    'key_id': key.id,
                    'key_code': key.key_code,
                    'room_number': key.room.number,
                    'status': key.status
                })
        return keys

    def get_total_keys(self, obj):
        """Get total number of keys assigned"""
        total = 0
        for room_reservation in obj.reservation.rooms.all():
            total += RoomKey.objects.filter(
                room=room_reservation.room,
                status='ACTIVE'
            ).count()
        return total

    def get_nights_stayed(self, obj):
        """Calculate nights stayed"""
        if obj.check_out_time and obj.check_in_time:
            delta = obj.check_out_time.date() - obj.check_in_time.date()
            return delta.days
        elif obj.check_in_time:
            # If still checked in, calculate from check-in to today
            delta = timezone.now().date() - obj.check_in_time.date()
            return delta.days
        return 0


class CheckInListSerializer(serializers.ModelSerializer):
    """Simplified serializer for check-in listings"""
    reservation_number = serializers.CharField(source='reservation.reservation_number', read_only=True)
    guest_name = serializers.CharField(source='reservation.guest.full_name', read_only=True)
    room_count = serializers.SerializerMethodField()
    checkout_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CheckIn
        fields = [
            'id', 'reservation_number', 'guest_name', 'check_in_time',
            'check_out_time', 'early_checkout', 'late_checkout',
            'room_count', 'checkout_status'
        ]

    def get_room_count(self, obj):
        """Get number of rooms in reservation"""
        return obj.reservation.rooms.count()

    def get_checkout_status(self, obj):
        """Get checkout status"""
        if obj.check_out_time:
            return 'CHECKED_OUT'
        elif obj.early_checkout:
            return 'EARLY_CHECKOUT'
        elif obj.late_checkout:
            return 'LATE_CHECKOUT'
        else:
            return 'CHECKED_IN'


class CheckInCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating check-ins"""
    room_preferences = serializers.JSONField(required=False, help_text="Room preferences as JSON")
    
    class Meta:
        model = CheckIn
        fields = [
            'reservation', 'special_requests', 'notes', 'room_preferences'
        ]

    def validate(self, data):
        """Validate check-in data"""
        reservation = data['reservation']
        
        # Check if reservation can be checked in
        if reservation.status != 'CONFIRMED':
            raise serializers.ValidationError(
                f"Cannot check in reservation with status: {reservation.get_status_display()}"
            )
        
        # Check if already checked in
        if CheckIn.objects.filter(reservation=reservation).exists():
            raise serializers.ValidationError("This reservation is already checked in")
        
        # Check if check-in date is today or past
        today = timezone.now().date()
        if reservation.check_in_date > today:
            raise serializers.ValidationError(
                f"Cannot check in before check-in date: {reservation.check_in_date}"
            )
        
        return data

    def create(self, validated_data):
        """Create check-in and assign room keys"""
        room_preferences = validated_data.pop('room_preferences', {})
        
        # Create check-in record
        checkin = CheckIn.objects.create(
            check_in_time=timezone.now(),
            **validated_data
        )
        
        # Update reservation status
        reservation = checkin.reservation
        reservation.status = 'CHECKED_IN'
        reservation.actual_check_in = timezone.now()
        reservation.save(update_fields=['status', 'actual_check_in', 'updated_at'])
        
        # Update room statuses and create/activate room keys
        for room_reservation in reservation.rooms.all():
            room = room_reservation.room
            room.status = 'OCCUPIED'
            room.save(update_fields=['status', 'updated_at'])
            
            # Create or activate room key
            key, created = RoomKey.objects.get_or_create(
                room=room,
                defaults={'status': 'ACTIVE'}
            )
            if not created and key.status != 'ACTIVE':
                key.status = 'ACTIVE'
                key.save(update_fields=['status', 'updated_at'])
        
        return checkin


class CheckOutSerializer(serializers.Serializer):
    """Serializer for check-out process"""
    checkout_time = serializers.DateTimeField(required=False, help_text="Custom checkout time, defaults to now")
    room_inspection = serializers.JSONField(required=False, help_text="Room inspection results as JSON")
    damage_notes = serializers.CharField(max_length=1000, required=False)
    additional_charges = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    guest_feedback = serializers.CharField(max_length=1000, required=False)
    
    def validate(self, data):
        """Validate checkout data"""
        checkout_time = data.get('checkout_time', timezone.now())
        
        # Ensure checkout time is not in the future
        if checkout_time > timezone.now():
            raise serializers.ValidationError("Checkout time cannot be in the future")
        
        return data


class RoomKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating room keys"""
    class Meta:
        model = RoomKey
        fields = ['room', 'key_code', 'status']

    def validate(self, data):
        """Validate room key data"""
        room = data['room']
        key_code = data['key_code']
        
        # Check if key code already exists for this room
        if RoomKey.objects.filter(room=room, key_code=key_code).exists():
            raise serializers.ValidationError(
                f"Key with code {key_code} already exists for room {room.number}"
            )
        
        return data


class CheckInStatsSerializer(serializers.Serializer):
    """Serializer for check-in statistics"""
    total_checkins = serializers.IntegerField()
    total_checkouts = serializers.IntegerField()
    currently_checked_in = serializers.IntegerField()
    early_checkouts = serializers.IntegerField()
    late_checkouts = serializers.IntegerField()
    average_stay_duration = serializers.FloatField()
    occupancy_rate = serializers.FloatField()


class GuestStayHistorySerializer(serializers.Serializer):
    """Serializer for guest stay history"""
    checkin_id = serializers.IntegerField()
    reservation_number = serializers.CharField()
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    nights_stayed = serializers.IntegerField()
    rooms_stayed = serializers.ListField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    special_requests = serializers.CharField()
    guest_feedback = serializers.CharField()


class RoomOccupancySerializer(serializers.Serializer):
    """Serializer for room occupancy data"""
    room_id = serializers.IntegerField()
    room_number = serializers.CharField()
    room_type = serializers.CharField()
    floor = serializers.IntegerField()
    current_status = serializers.CharField()
    guest_name = serializers.CharField()
    check_in_time = serializers.DateTimeField()
    expected_checkout = serializers.DateTimeField()
    nights_staying = serializers.IntegerField()
    key_status = serializers.CharField()


class CheckInActivitySerializer(serializers.Serializer):
    """Serializer for check-in activity logs"""
    activity_type = serializers.CharField()  # CHECK_IN, CHECK_OUT, KEY_ISSUED, etc.
    timestamp = serializers.DateTimeField()
    guest_name = serializers.CharField()
    room_numbers = serializers.ListField()
    performed_by = serializers.CharField()  # Staff member
    notes = serializers.CharField()