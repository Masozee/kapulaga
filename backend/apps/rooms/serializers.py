from rest_framework import serializers
from .models import RoomType, Room


class RoomTypeSerializer(serializers.ModelSerializer):
    occupancy_percentage = serializers.SerializerMethodField()
    available_rooms_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'description', 'base_price', 'max_occupancy', 
            'size_sqm', 'amenities', 'is_active', 'created_at', 'updated_at',
            'occupancy_percentage', 'available_rooms_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_occupancy_percentage(self, obj):
        """Calculate occupancy percentage for this room type"""
        total_rooms = obj.room_set.count()
        if total_rooms == 0:
            return 0
        occupied_rooms = obj.room_set.filter(status__in=['OCCUPIED', 'RESERVED']).count()
        return round((occupied_rooms / total_rooms) * 100, 1)
    
    def get_available_rooms_count(self, obj):
        """Get count of available rooms for this room type"""
        return obj.room_set.filter(status='AVAILABLE', is_active=True).count()


class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    current_price = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'number', 'room_type', 'room_type_name', 'floor', 'status', 
            'status_display', 'notes', 'is_active', 'created_at', 'updated_at',
            'current_price'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_current_price(self, obj):
        """Get current price for the room"""
        return obj.get_current_price()


class RoomListSerializer(serializers.ModelSerializer):
    """Simplified serializer for room listings"""
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'number', 'room_type_name', 'floor', 'status', 
            'status_display', 'is_active'
        ]


class RoomAvailabilitySerializer(serializers.Serializer):
    """Serializer for room availability checks"""
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    room_type = serializers.IntegerField(required=False, help_text="Room type ID for filtering")
    adults = serializers.IntegerField(default=1, min_value=1)
    children = serializers.IntegerField(default=0, min_value=0)

    def validate(self, data):
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        return data