from rest_framework import serializers
from decimal import Decimal
from .models import Reservation, ReservationRoom
from apps.guests.serializers import GuestSerializer
from apps.rooms.serializers import RoomSerializer


class ReservationRoomSerializer(serializers.ModelSerializer):
    room_details = RoomSerializer(source='room', read_only=True)
    room_number = serializers.CharField(source='room.number', read_only=True)
    room_type_name = serializers.CharField(source='room.room_type.name', read_only=True)
    total_amount = serializers.ReadOnlyField()
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = ReservationRoom
        fields = [
            'id', 'room', 'room_details', 'room_number', 'room_type_name',
            'rate', 'discount_amount', 'extra_charges', 'total_amount',
            'nights', 'notes', 'created_at'
        ]
        read_only_fields = ['total_amount', 'created_at']

    def get_nights(self, obj):
        """Get number of nights for this reservation"""
        return obj.reservation.nights


class ReservationSerializer(serializers.ModelSerializer):
    guest_details = GuestSerializer(source='guest', read_only=True)
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    booking_source_display = serializers.CharField(source='get_booking_source_display', read_only=True)
    rooms = ReservationRoomSerializer(many=True, read_only=True)
    nights = serializers.ReadOnlyField()
    total_rooms = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    can_cancel = serializers.ReadOnlyField()
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'reservation_number', 'guest', 'guest_details', 'guest_name',
            'check_in_date', 'check_out_date', 'nights', 'adults', 'children',
            'special_requests', 'total_amount', 'deposit_amount', 'status',
            'status_display', 'booking_source', 'booking_source_display',
            'notes', 'created_at', 'updated_at', 'rooms', 'total_rooms',
            'can_cancel'
        ]
        read_only_fields = ['reservation_number', 'created_at', 'updated_at', 'nights', 'can_cancel']

    def get_total_rooms(self, obj):
        """Get total number of rooms in reservation"""
        return obj.rooms.count()

    def get_total_amount(self, obj):
        """Get total amount from all rooms"""
        return float(obj.calculate_total_amount())


class ReservationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for reservation listings"""
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_rooms = serializers.SerializerMethodField()
    nights = serializers.ReadOnlyField()
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'reservation_number', 'guest_name', 'check_in_date',
            'check_out_date', 'nights', 'adults', 'children', 'status',
            'status_display', 'booking_source', 'total_rooms', 'created_at'
        ]

    def get_total_rooms(self, obj):
        """Get total number of rooms in reservation"""
        return obj.rooms.count()


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reservations"""
    room_assignments = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="List of room assignments with room_id, rate, discount_amount, extra_charges"
    )
    
    class Meta:
        model = Reservation
        fields = [
            'guest', 'check_in_date', 'check_out_date', 'adults', 'children',
            'special_requests', 'booking_source', 'notes', 'room_assignments'
        ]

    def validate(self, data):
        """Validate reservation data"""
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        
        if not data.get('room_assignments'):
            raise serializers.ValidationError("At least one room assignment is required")
        
        return data

    def create(self, validated_data):
        """Create reservation with room assignments"""
        room_assignments = validated_data.pop('room_assignments')
        
        # Create reservation
        reservation = Reservation.objects.create(**validated_data)
        
        # Create room assignments
        from apps.rooms.models import Room
        for assignment in room_assignments:
            room = Room.objects.get(id=assignment['room_id'])
            ReservationRoom.objects.create(
                reservation=reservation,
                room=room,
                rate=assignment.get('rate', room.room_type.base_price),
                discount_amount=assignment.get('discount_amount', Decimal('0.00')),
                extra_charges=assignment.get('extra_charges', Decimal('0.00')),
                notes=assignment.get('notes', '')
            )
        
        # Update total amount
        reservation.update_total_amount()
        
        return reservation


class ReservationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reservations"""
    class Meta:
        model = Reservation
        fields = [
            'check_in_date', 'check_out_date', 'adults', 'children',
            'special_requests', 'status', 'notes'
        ]

    def validate(self, data):
        """Validate reservation update"""
        instance = self.instance
        check_in = data.get('check_in_date', instance.check_in_date)
        check_out = data.get('check_out_date', instance.check_out_date)
        
        if check_out <= check_in:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        
        # Prevent certain changes for checked-in guests
        if instance.status == 'CHECKED_IN':
            if 'check_in_date' in data or 'check_out_date' in data:
                raise serializers.ValidationError("Cannot change dates for checked-in reservations")
        
        return data


class CheckAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking room availability"""
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    adults = serializers.IntegerField(min_value=1, default=1)
    children = serializers.IntegerField(min_value=0, default=0)
    room_type = serializers.IntegerField(required=False, help_text="Filter by room type ID")

    def validate(self, data):
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        return data