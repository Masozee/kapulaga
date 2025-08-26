from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import CheckIn, RoomKey
from .serializers import (
    CheckInSerializer, CheckInListSerializer, CheckInCreateSerializer,
    CheckOutSerializer, RoomKeySerializer, RoomKeyCreateSerializer,
    CheckInStatsSerializer, GuestStayHistorySerializer, RoomOccupancySerializer
)


class CheckInViewSet(viewsets.ModelViewSet):
    """ViewSet for managing check-ins"""
    queryset = CheckIn.objects.select_related('reservation__guest').order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reservation', 'early_checkout', 'late_checkout']
    search_fields = [
        'reservation__reservation_number', 
        'reservation__guest__first_name', 
        'reservation__guest__last_name',
        'reservation__guest__email'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CheckInListSerializer
        elif self.action == 'create':
            return CheckInCreateSerializer
        return CheckInSerializer

    @action(detail=False, methods=['get'])
    def current_checkins(self, request):
        """Get all currently checked-in guests"""
        current_checkins = self.get_queryset().filter(check_out_time__isnull=True)
        serializer = CheckInListSerializer(current_checkins, many=True)
        
        return Response({
            'total_current_checkins': current_checkins.count(),
            'checkins': serializer.data
        })

    @action(detail=False, methods=['get'])
    def todays_checkins(self, request):
        """Get today's check-ins"""
        today = timezone.now().date()
        todays_checkins = self.get_queryset().filter(check_in_time__date=today)
        serializer = CheckInListSerializer(todays_checkins, many=True)
        
        return Response({
            'date': today,
            'total_checkins_today': todays_checkins.count(),
            'checkins': serializer.data
        })

    @action(detail=False, methods=['get'])
    def todays_checkouts(self, request):
        """Get today's check-outs"""
        today = timezone.now().date()
        todays_checkouts = self.get_queryset().filter(check_out_time__date=today)
        serializer = CheckInListSerializer(todays_checkouts, many=True)
        
        return Response({
            'date': today,
            'total_checkouts_today': todays_checkouts.count(),
            'checkouts': serializer.data
        })

    @action(detail=False, methods=['get'])
    def expected_checkouts(self, request):
        """Get expected check-outs for today"""
        today = timezone.now().date()
        
        # Find check-ins that haven't checked out yet but reservation ends today
        expected_checkouts = self.get_queryset().filter(
            check_out_time__isnull=True,
            reservation__check_out_date=today
        )
        
        serializer = CheckInListSerializer(expected_checkouts, many=True)
        
        return Response({
            'date': today,
            'total_expected_checkouts': expected_checkouts.count(),
            'expected_checkouts': serializer.data
        })

    @action(detail=False, methods=['get'])
    def overdue_checkouts(self, request):
        """Get overdue check-outs (past check-out date but still checked in)"""
        today = timezone.now().date()
        
        overdue_checkouts = self.get_queryset().filter(
            check_out_time__isnull=True,
            reservation__check_out_date__lt=today
        )
        
        overdue_data = []
        for checkin in overdue_checkouts:
            days_overdue = (today - checkin.reservation.check_out_date).days
            overdue_data.append({
                'checkin_id': checkin.id,
                'reservation_number': checkin.reservation.reservation_number,
                'guest_name': checkin.reservation.guest.full_name,
                'guest_phone': checkin.reservation.guest.phone,
                'expected_checkout_date': checkin.reservation.check_out_date,
                'days_overdue': days_overdue,
                'room_count': checkin.reservation.rooms.count(),
                'rooms': [r.room.number for r in checkin.reservation.rooms.all()]
            })
        
        return Response({
            'total_overdue_checkouts': len(overdue_data),
            'overdue_checkouts': overdue_data
        })

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Process guest check-out"""
        checkin = self.get_object()
        
        if checkin.check_out_time:
            return Response({
                'error': 'Guest has already checked out'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CheckOutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        checkout_time = validated_data.get('checkout_time', timezone.now())
        
        # Update check-in record
        checkin.check_out_time = checkout_time
        checkin.actual_checkout_time = timezone.now()
        
        # Check if early or late checkout
        expected_checkout = checkin.reservation.check_out_date
        checkout_date = checkout_time.date()
        
        if checkout_date < expected_checkout:
            checkin.early_checkout = True
        elif checkout_date > expected_checkout:
            checkin.late_checkout = True
        
        # Add checkout notes
        room_inspection = validated_data.get('room_inspection', {})
        damage_notes = validated_data.get('damage_notes', '')
        additional_charges = validated_data.get('additional_charges', Decimal('0'))
        guest_feedback = validated_data.get('guest_feedback', '')
        
        checkout_notes = []
        if room_inspection:
            checkout_notes.append(f"Room inspection: {room_inspection}")
        if damage_notes:
            checkout_notes.append(f"Damage notes: {damage_notes}")
        if additional_charges > 0:
            checkout_notes.append(f"Additional charges: {additional_charges}")
        if guest_feedback:
            checkout_notes.append(f"Guest feedback: {guest_feedback}")
        
        if checkout_notes:
            checkin.notes = (checkin.notes + "\n" if checkin.notes else "") + "\n".join(checkout_notes)
        
        checkin.save(update_fields=[
            'check_out_time', 'actual_checkout_time', 'early_checkout', 
            'late_checkout', 'notes', 'updated_at'
        ])
        
        # Update reservation status
        reservation = checkin.reservation
        reservation.status = 'CHECKED_OUT'
        reservation.actual_check_out = checkout_time
        reservation.save(update_fields=['status', 'actual_check_out', 'updated_at'])
        
        # Update room statuses and deactivate keys
        for room_reservation in reservation.rooms.all():
            room = room_reservation.room
            room.status = 'CLEANING'  # Or 'AVAILABLE' based on hotel policy
            room.save(update_fields=['status', 'updated_at'])
            
            # Deactivate room keys
            RoomKey.objects.filter(room=room, status='ACTIVE').update(
                status='DEACTIVATED',
                updated_at=timezone.now()
            )
        
        return Response({
            'success': True,
            'message': f'Guest {reservation.guest.full_name} checked out successfully',
            'checkout_time': checkout_time,
            'early_checkout': checkin.early_checkout,
            'late_checkout': checkin.late_checkout,
            'additional_charges': float(additional_charges),
            'checkin': CheckInSerializer(checkin).data
        })

    @action(detail=False, methods=['get'])
    def room_occupancy(self, request):
        """Get current room occupancy status"""
        current_checkins = self.get_queryset().filter(check_out_time__isnull=True)
        
        occupancy_data = []
        for checkin in current_checkins:
            for room_reservation in checkin.reservation.rooms.all():
                room = room_reservation.room
                
                # Get active key status
                active_keys = RoomKey.objects.filter(room=room, status='ACTIVE')
                key_status = f"{active_keys.count()} keys active" if active_keys.exists() else "No active keys"
                
                occupancy_data.append({
                    'room_id': room.id,
                    'room_number': room.number,
                    'room_type': room.room_type.name,
                    'floor': room.floor,
                    'current_status': room.status,
                    'guest_name': checkin.reservation.guest.full_name,
                    'check_in_time': checkin.check_in_time,
                    'expected_checkout': checkin.reservation.check_out_date,
                    'nights_staying': checkin.reservation.nights,
                    'key_status': key_status
                })
        
        # Calculate occupancy statistics
        from apps.rooms.models import Room
        total_rooms = Room.objects.filter(is_active=True).count()
        occupied_rooms = len(occupancy_data)
        occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
        
        return Response({
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': total_rooms - occupied_rooms,
            'occupancy_rate': round(occupancy_rate, 1),
            'room_occupancy': occupancy_data
        })

    @action(detail=False, methods=['get'])
    def stats_summary(self, request):
        """Get check-in statistics summary"""
        # Get date range from query params, default to last 30 days
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        checkins_in_period = self.get_queryset().filter(
            check_in_time__gte=start_date
        )
        
        total_checkins = checkins_in_period.count()
        total_checkouts = checkins_in_period.filter(check_out_time__isnull=False).count()
        currently_checked_in = checkins_in_period.filter(check_out_time__isnull=True).count()
        early_checkouts = checkins_in_period.filter(early_checkout=True).count()
        late_checkouts = checkins_in_period.filter(late_checkout=True).count()
        
        # Calculate average stay duration for completed stays
        completed_stays = checkins_in_period.filter(check_out_time__isnull=False)
        avg_stay_duration = 0
        if completed_stays.exists():
            total_duration = sum([
                (checkin.check_out_time.date() - checkin.check_in_time.date()).days
                for checkin in completed_stays
            ])
            avg_stay_duration = total_duration / completed_stays.count()
        
        # Current occupancy rate
        from apps.rooms.models import Room
        total_rooms = Room.objects.filter(is_active=True).count()
        current_occupied = self.get_queryset().filter(check_out_time__isnull=True).count()
        current_occupancy_rate = (current_occupied / total_rooms) * 100 if total_rooms > 0 else 0
        
        stats = {
            'period_days': days,
            'total_checkins': total_checkins,
            'total_checkouts': total_checkouts,
            'currently_checked_in': currently_checked_in,
            'early_checkouts': early_checkouts,
            'late_checkouts': late_checkouts,
            'average_stay_duration': round(avg_stay_duration, 1),
            'occupancy_rate': round(current_occupancy_rate, 1)
        }
        
        return Response(stats)

    @action(detail=True, methods=['get'])
    def guest_stay_details(self, request, pk=None):
        """Get detailed stay information for a guest"""
        checkin = self.get_object()
        reservation = checkin.reservation
        guest = reservation.guest
        
        # Get room details
        rooms_stayed = []
        for room_reservation in reservation.rooms.all():
            room = room_reservation.room
            rooms_stayed.append({
                'room_number': room.number,
                'room_type': room.room_type.name,
                'floor': room.floor,
                'rate': float(room_reservation.rate),
                'nights': reservation.nights
            })
        
        # Get bill information
        bill_info = None
        if hasattr(reservation, 'bill'):
            bill = reservation.bill
            bill_info = {
                'bill_number': bill.bill_number,
                'total_amount': float(bill.total_amount),
                'paid_amount': float(bill.paid_amount),
                'status': bill.status
            }
        
        stay_details = {
            'checkin_id': checkin.id,
            'reservation_number': reservation.reservation_number,
            'guest_info': {
                'name': guest.full_name,
                'email': guest.email,
                'phone': guest.phone,
                'is_vip': guest.is_vip,
                'loyalty_points': guest.loyalty_points
            },
            'stay_dates': {
                'check_in_date': reservation.check_in_date,
                'check_out_date': reservation.check_out_date,
                'actual_check_in': checkin.check_in_time,
                'actual_check_out': checkin.check_out_time,
                'nights_stayed': checkin.get_nights_stayed() if hasattr(checkin, 'get_nights_stayed') else 0
            },
            'rooms_stayed': rooms_stayed,
            'special_requests': checkin.special_requests,
            'checkout_flags': {
                'early_checkout': checkin.early_checkout,
                'late_checkout': checkin.late_checkout
            },
            'bill_info': bill_info,
            'notes': checkin.notes
        }
        
        return Response(stay_details)


class RoomKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing room keys"""
    queryset = RoomKey.objects.select_related('room').order_by('room__number')
    serializer_class = RoomKeySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'status']
    search_fields = ['room__number', 'key_code']
    ordering = ['room__number']

    def get_serializer_class(self):
        if self.action == 'create':
            return RoomKeyCreateSerializer
        return RoomKeySerializer

    @action(detail=False, methods=['get'])
    def active_keys(self, request):
        """Get all currently active keys"""
        active_keys = self.get_queryset().filter(status='ACTIVE')
        serializer = RoomKeySerializer(active_keys, many=True)
        
        return Response({
            'total_active_keys': active_keys.count(),
            'keys': serializer.data
        })

    @action(detail=False, methods=['get'])
    def keys_by_room(self, request):
        """Get keys grouped by room"""
        from apps.rooms.models import Room
        
        rooms = Room.objects.filter(is_active=True).prefetch_related('roomkey_set')
        room_keys_data = []
        
        for room in rooms:
            keys = room.roomkey_set.all()
            active_keys = keys.filter(status='ACTIVE')
            
            room_keys_data.append({
                'room_id': room.id,
                'room_number': room.number,
                'room_type': room.room_type.name,
                'total_keys': keys.count(),
                'active_keys': active_keys.count(),
                'keys': RoomKeySerializer(keys, many=True).data
            })
        
        return Response({
            'total_rooms': len(room_keys_data),
            'room_keys': room_keys_data
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a room key"""
        key = self.get_object()
        
        if key.status == 'ACTIVE':
            return Response({
                'message': f'Key {key.key_code} for room {key.room.number} is already active'
            })
        
        key.status = 'ACTIVE'
        key.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Key {key.key_code} for room {key.room.number} has been activated',
            'key': RoomKeySerializer(key).data
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a room key"""
        key = self.get_object()
        reason = request.data.get('reason', 'Manual deactivation')
        
        if key.status == 'DEACTIVATED':
            return Response({
                'message': f'Key {key.key_code} for room {key.room.number} is already deactivated'
            })
        
        key.status = 'DEACTIVATED'
        key.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Key {key.key_code} for room {key.room.number} has been deactivated',
            'reason': reason,
            'key': RoomKeySerializer(key).data
        })

    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        """Deactivate multiple keys (e.g., for maintenance)"""
        room_ids = request.data.get('room_ids', [])
        reason = request.data.get('reason', 'Bulk deactivation')
        
        if not room_ids:
            return Response({
                'error': 'room_ids list is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        keys_to_deactivate = self.get_queryset().filter(
            room_id__in=room_ids,
            status='ACTIVE'
        )
        
        updated_count = keys_to_deactivate.update(
            status='DEACTIVATED',
            updated_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': f'Deactivated {updated_count} keys for {len(room_ids)} rooms',
            'reason': reason,
            'deactivated_count': updated_count,
            'room_count': len(room_ids)
        })

    @action(detail=False, methods=['get'])
    def key_statistics(self, request):
        """Get key usage statistics"""
        total_keys = self.get_queryset().count()
        active_keys = self.get_queryset().filter(status='ACTIVE').count()
        deactivated_keys = self.get_queryset().filter(status='DEACTIVATED').count()
        lost_keys = self.get_queryset().filter(status='LOST').count()
        
        # Keys by room type
        from apps.rooms.models import RoomType
        room_types = RoomType.objects.filter(is_active=True)
        keys_by_type = []
        
        for room_type in room_types:
            type_keys = self.get_queryset().filter(room__room_type=room_type)
            keys_by_type.append({
                'room_type': room_type.name,
                'total_keys': type_keys.count(),
                'active_keys': type_keys.filter(status='ACTIVE').count(),
                'rooms_count': room_type.room_set.filter(is_active=True).count()
            })
        
        statistics = {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'deactivated_keys': deactivated_keys,
            'lost_keys': lost_keys,
            'activation_rate': round((active_keys / total_keys) * 100, 1) if total_keys > 0 else 0,
            'keys_by_room_type': keys_by_type
        }
        
        return Response(statistics)
