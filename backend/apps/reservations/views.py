from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Reservation, ReservationRoom
from .serializers import (
    ReservationSerializer, ReservationListSerializer, ReservationCreateSerializer,
    ReservationUpdateSerializer, ReservationRoomSerializer, CheckAvailabilitySerializer
)


class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reservations"""
    queryset = Reservation.objects.select_related('guest').prefetch_related('rooms__room__room_type')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'booking_source', 'guest', 'check_in_date', 'check_out_date']
    search_fields = ['reservation_number', 'guest__first_name', 'guest__last_name', 'guest__email']
    ordering_fields = ['check_in_date', 'check_out_date', 'created_at', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservationListSerializer
        elif self.action == 'create':
            return ReservationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReservationUpdateSerializer
        return ReservationSerializer

    @action(detail=False, methods=['post'])
    def check_availability(self, request):
        """Check room availability for reservation"""
        serializer = CheckAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        check_in = data['check_in_date']
        check_out = data['check_out_date']
        adults = data['adults']
        children = data['children']
        room_type_id = data.get('room_type')
        
        # Get available rooms
        from apps.rooms.models import Room
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
        
        # Check for conflicting reservations
        conflicting_reservations = Reservation.objects.filter(
            status__in=['CONFIRMED', 'CHECKED_IN'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        ).values_list('rooms__room', flat=True)
        
        available_rooms = available_rooms.exclude(id__in=conflicting_reservations)
        
        # Prepare response
        from apps.rooms.serializers import RoomListSerializer
        room_serializer = RoomListSerializer(available_rooms, many=True)
        
        return Response({
            'check_in_date': check_in,
            'check_out_date': check_out,
            'nights': (check_out - check_in).days,
            'adults': adults,
            'children': children,
            'available_rooms': room_serializer.data,
            'total_available': len(room_serializer.data)
        })

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a reservation"""
        reservation = self.get_object()
        
        if reservation.status != 'PENDING':
            return Response({
                'error': f'Cannot confirm reservation with status: {reservation.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reservation.status = 'CONFIRMED'
        reservation.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Reservation {reservation.reservation_number} confirmed',
            'reservation': ReservationSerializer(reservation).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()
        
        if not reservation.can_cancel:
            return Response({
                'error': f'Cannot cancel reservation with status: {reservation.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cancellation reason
        reason = request.data.get('reason', 'Customer request')
        
        reservation.status = 'CANCELLED'
        reservation.notes = f"{reservation.notes}\nCancelled: {reason}" if reservation.notes else f"Cancelled: {reason}"
        reservation.save(update_fields=['status', 'notes', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Reservation {reservation.reservation_number} cancelled',
            'reason': reason,
            'reservation': ReservationSerializer(reservation).data
        })

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a guest"""
        reservation = self.get_object()
        
        if reservation.status != 'CONFIRMED':
            return Response({
                'error': f'Cannot check in reservation with status: {reservation.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if check-in date is today or in the past
        today = timezone.now().date()
        if reservation.check_in_date > today:
            return Response({
                'error': f'Cannot check in before check-in date: {reservation.check_in_date}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reservation.status = 'CHECKED_IN'
        reservation.actual_check_in = timezone.now()
        reservation.save(update_fields=['status', 'actual_check_in', 'updated_at'])
        
        # Update room status to occupied
        for reservation_room in reservation.rooms.all():
            reservation_room.room.status = 'OCCUPIED'
            reservation_room.room.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Guest {reservation.guest.full_name} checked in for reservation {reservation.reservation_number}',
            'check_in_time': reservation.actual_check_in,
            'reservation': ReservationSerializer(reservation).data
        })

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Check out a guest"""
        reservation = self.get_object()
        
        if reservation.status != 'CHECKED_IN':
            return Response({
                'error': f'Cannot check out reservation with status: {reservation.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reservation.status = 'CHECKED_OUT'
        reservation.actual_check_out = timezone.now()
        reservation.save(update_fields=['status', 'actual_check_out', 'updated_at'])
        
        # Update room status to available
        for reservation_room in reservation.rooms.all():
            reservation_room.room.status = 'AVAILABLE'
            reservation_room.room.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Guest {reservation.guest.full_name} checked out for reservation {reservation.reservation_number}',
            'check_out_time': reservation.actual_check_out,
            'reservation': ReservationSerializer(reservation).data
        })

    @action(detail=False, methods=['get'])
    def today_arrivals(self, request):
        """Get today's arriving guests"""
        today = timezone.now().date()
        arrivals = self.get_queryset().filter(
            check_in_date=today,
            status='CONFIRMED'
        )
        serializer = ReservationListSerializer(arrivals, many=True)
        return Response({
            'date': today,
            'total_arrivals': arrivals.count(),
            'reservations': serializer.data
        })

    @action(detail=False, methods=['get'])
    def today_departures(self, request):
        """Get today's departing guests"""
        today = timezone.now().date()
        departures = self.get_queryset().filter(
            check_out_date=today,
            status='CHECKED_IN'
        )
        serializer = ReservationListSerializer(departures, many=True)
        return Response({
            'date': today,
            'total_departures': departures.count(),
            'reservations': serializer.data
        })

    @action(detail=False, methods=['get'])
    def occupancy_summary(self, request):
        """Get occupancy summary"""
        today = timezone.now().date()
        
        # Current occupancy
        current_occupancy = self.get_queryset().filter(
            status='CHECKED_IN',
            check_in_date__lte=today,
            check_out_date__gt=today
        ).count()
        
        # Today's arrivals/departures
        arrivals = self.get_queryset().filter(
            check_in_date=today,
            status='CONFIRMED'
        ).count()
        
        departures = self.get_queryset().filter(
            check_out_date=today,
            status='CHECKED_IN'
        ).count()
        
        # Total rooms
        from apps.rooms.models import Room
        total_rooms = Room.objects.filter(is_active=True).count()
        
        return Response({
            'date': today,
            'current_occupancy': current_occupancy,
            'total_rooms': total_rooms,
            'occupancy_rate': round((current_occupancy / total_rooms) * 100, 1) if total_rooms > 0 else 0,
            'today_arrivals': arrivals,
            'today_departures': departures,
            'expected_occupancy': current_occupancy + arrivals - departures
        })

    @action(detail=False, methods=['get'])
    def monthly_stats(self, request):
        """Get monthly reservation statistics"""
        # Get month from query params, default to current month
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if month and year:
            target_date = datetime(int(year), int(month), 1).date()
        else:
            target_date = timezone.now().date().replace(day=1)
        
        # Calculate month range
        if target_date.month == 12:
            next_month = target_date.replace(year=target_date.year + 1, month=1)
        else:
            next_month = target_date.replace(month=target_date.month + 1)
        
        monthly_reservations = self.get_queryset().filter(
            created_at__gte=target_date,
            created_at__lt=next_month
        )
        
        stats = {
            'month': target_date.strftime('%B %Y'),
            'total_reservations': monthly_reservations.count(),
            'confirmed_reservations': monthly_reservations.filter(status='CONFIRMED').count(),
            'cancelled_reservations': monthly_reservations.filter(status='CANCELLED').count(),
            'checked_in_reservations': monthly_reservations.filter(status='CHECKED_IN').count(),
            'checked_out_reservations': monthly_reservations.filter(status='CHECKED_OUT').count(),
            'total_revenue': float(monthly_reservations.filter(
                status__in=['CHECKED_OUT', 'CHECKED_IN']
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0),
            'average_stay_length': monthly_reservations.aggregate(
                avg_nights=Sum('nights')
            )['avg_nights'] / monthly_reservations.count() if monthly_reservations.count() > 0 else 0
        }
        
        return Response(stats)

    @action(detail=True, methods=['post'])
    def add_room(self, request, pk=None):
        """Add a room to existing reservation"""
        reservation = self.get_object()
        
        if reservation.status not in ['PENDING', 'CONFIRMED']:
            return Response({
                'error': f'Cannot modify reservation with status: {reservation.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        room_id = request.data.get('room_id')
        rate = request.data.get('rate')
        discount_amount = request.data.get('discount_amount', 0)
        extra_charges = request.data.get('extra_charges', 0)
        notes = request.data.get('notes', '')
        
        if not room_id:
            return Response({'error': 'room_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from apps.rooms.models import Room
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if room is available
        if room.status != 'AVAILABLE':
            return Response({
                'error': f'Room {room.number} is not available (status: {room.get_status_display()})'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create room assignment
        reservation_room = ReservationRoom.objects.create(
            reservation=reservation,
            room=room,
            rate=rate or room.room_type.base_price,
            discount_amount=discount_amount,
            extra_charges=extra_charges,
            notes=notes
        )
        
        # Update total amount
        reservation.update_total_amount()
        
        return Response({
            'success': True,
            'message': f'Room {room.number} added to reservation {reservation.reservation_number}',
            'room_assignment': ReservationRoomSerializer(reservation_room).data,
            'reservation': ReservationSerializer(reservation).data
        })

    @action(detail=True, methods=['delete'])
    def remove_room(self, request, pk=None):
        """Remove a room from reservation"""
        reservation = self.get_object()
        
        if reservation.status not in ['PENDING', 'CONFIRMED']:
            return Response({
                'error': f'Cannot modify reservation with status: {reservation.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        room_id = request.data.get('room_id')
        if not room_id:
            return Response({'error': 'room_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reservation_room = reservation.rooms.get(room_id=room_id)
            room_number = reservation_room.room.number
            reservation_room.delete()
            
            # Update total amount
            reservation.update_total_amount()
            
            return Response({
                'success': True,
                'message': f'Room {room_number} removed from reservation {reservation.reservation_number}',
                'reservation': ReservationSerializer(reservation).data
            })
        except ReservationRoom.DoesNotExist:
            return Response({'error': 'Room not found in this reservation'}, status=status.HTTP_400_BAD_REQUEST)


class ReservationRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual room assignments in reservations"""
    queryset = ReservationRoom.objects.select_related('reservation', 'room__room_type')
    serializer_class = ReservationRoomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reservation', 'room', 'reservation__status']
    ordering = ['reservation__check_in_date', 'room__number']

    @action(detail=True, methods=['post'])
    def update_rate(self, request, pk=None):
        """Update room rate for this assignment"""
        reservation_room = self.get_object()
        new_rate = request.data.get('rate')
        
        if not new_rate:
            return Response({'error': 'rate is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        reservation_room.rate = new_rate
        reservation_room.save(update_fields=['rate', 'updated_at'])
        
        # Update reservation total
        reservation_room.reservation.update_total_amount()
        
        return Response({
            'success': True,
            'message': f'Rate updated for room {reservation_room.room.number}',
            'room_assignment': ReservationRoomSerializer(reservation_room).data
        })
