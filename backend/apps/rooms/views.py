from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import date

from .models import RoomType, Room
from .serializers import (
    RoomTypeSerializer, RoomSerializer, RoomListSerializer, 
    RoomAvailabilitySerializer
)


class RoomTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing room types"""
    queryset = RoomType.objects.filter(is_active=True)
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['max_occupancy', 'is_active']
    ordering_fields = ['name', 'base_price', 'max_occupancy']
    ordering = ['base_price']

    @action(detail=True, methods=['get'])
    def available_rooms(self, request, pk=None):
        """Get all available rooms for this room type"""
        room_type = self.get_object()
        available_rooms = room_type.room_set.filter(
            status='AVAILABLE', 
            is_active=True
        )
        serializer = RoomListSerializer(available_rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for all room types"""
        room_types = self.get_queryset()
        summary_data = []
        
        for room_type in room_types:
            total_rooms = room_type.room_set.count()
            available_rooms = room_type.room_set.filter(status='AVAILABLE', is_active=True).count()
            occupied_rooms = room_type.room_set.filter(status='OCCUPIED').count()
            
            summary_data.append({
                'id': room_type.id,
                'name': room_type.name,
                'base_price': room_type.base_price,
                'total_rooms': total_rooms,
                'available_rooms': available_rooms,
                'occupied_rooms': occupied_rooms,
                'occupancy_rate': round((occupied_rooms / total_rooms) * 100, 1) if total_rooms > 0 else 0
            })
        
        return Response(summary_data)


class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual rooms"""
    queryset = Room.objects.select_related('room_type')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room_type', 'floor', 'status', 'is_active']
    search_fields = ['number', 'room_type__name']
    ordering_fields = ['number', 'floor', 'room_type__base_price']
    ordering = ['number']

    def get_serializer_class(self):
        if self.action == 'list':
            return RoomListSerializer
        return RoomSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available rooms"""
        available_rooms = self.get_queryset().filter(
            status='AVAILABLE',
            is_active=True
        )
        serializer = RoomListSerializer(available_rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def check_availability(self, request):
        """Check room availability for given dates"""
        serializer = RoomAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        check_in = data['check_in_date']
        check_out = data['check_out_date']
        room_type_id = data.get('room_type')
        adults = data['adults']
        children = data['children']
        
        # Base queryset for available rooms
        available_rooms = Room.objects.filter(
            status='AVAILABLE',
            is_active=True
        ).select_related('room_type')
        
        # Filter by room type if specified
        if room_type_id:
            available_rooms = available_rooms.filter(room_type_id=room_type_id)
        
        # Filter by occupancy capacity
        total_guests = adults + children
        available_rooms = available_rooms.filter(room_type__max_occupancy__gte=total_guests)
        
        # TODO: Add logic to check for conflicting reservations
        # This would require checking the reservations table for overlapping dates
        
        serializer = RoomListSerializer(available_rooms, many=True)
        
        response_data = {
            'check_in_date': check_in,
            'check_out_date': check_out,
            'nights': (check_out - check_in).days,
            'adults': adults,
            'children': children,
            'available_rooms': serializer.data,
            'total_available': len(serializer.data)
        }
        
        return Response(response_data)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change room status"""
        room = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Room.ROOM_STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status. Valid choices: ' + ', '.join(dict(Room.ROOM_STATUS_CHOICES).keys())},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room.status = new_status
        room.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Room {room.number} status changed to {room.get_status_display()}',
            'room': RoomSerializer(room).data
        })

    @action(detail=False, methods=['get'])
    def floor_summary(self, request):
        """Get room summary by floor"""
        from django.db.models import Count
        
        floor_data = Room.objects.values('floor').annotate(
            total_rooms=Count('id'),
            available_rooms=Count('id', filter=Q(status='AVAILABLE')),
            occupied_rooms=Count('id', filter=Q(status='OCCUPIED')),
            maintenance_rooms=Count('id', filter=Q(status='MAINTENANCE')),
            out_of_order_rooms=Count('id', filter=Q(status='OUT_OF_ORDER'))
        ).order_by('floor')
        
        return Response(list(floor_data))