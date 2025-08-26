from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.utils import timezone

from .models import Guest, GuestDocument
from .serializers import (
    GuestSerializer, GuestListSerializer, GuestCreateUpdateSerializer,
    GuestDocumentSerializer, LoyaltyPointsSerializer
)


class GuestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing guests"""
    queryset = Guest.objects.select_related().prefetch_related('documents', 'reservations')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nationality', 'gender', 'is_vip', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'loyalty_points', 'created_at']
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return GuestListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return GuestCreateUpdateSerializer
        return GuestSerializer

    @action(detail=False, methods=['get'])
    def vip_guests(self, request):
        """Get all VIP guests"""
        vip_guests = self.get_queryset().filter(is_vip=True)
        serializer = GuestListSerializer(vip_guests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def loyalty_summary(self, request):
        """Get loyalty program summary"""
        guests = self.get_queryset().filter(is_active=True)
        
        summary = {
            'total_guests': guests.count(),
            'vip_guests': guests.filter(is_vip=True).count(),
            'loyalty_levels': {
                'platinum': guests.filter(loyalty_points__gte=1000).count(),
                'gold': guests.filter(loyalty_points__gte=500, loyalty_points__lt=1000).count(),
                'silver': guests.filter(loyalty_points__gte=100, loyalty_points__lt=500).count(),
                'bronze': guests.filter(loyalty_points__lt=100).count()
            },
            'total_loyalty_points': guests.aggregate(total=Sum('loyalty_points'))['total'] or 0
        }
        
        return Response(summary)

    @action(detail=True, methods=['post'])
    def add_loyalty_points(self, request, pk=None):
        """Add loyalty points to a guest"""
        guest = self.get_object()
        serializer = LoyaltyPointsSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        points = serializer.validated_data['points']
        reason = serializer.validated_data['reason']
        
        guest.add_loyalty_points(points)
        
        return Response({
            'success': True,
            'message': f'Added {points} loyalty points to {guest.full_name}',
            'reason': reason,
            'new_balance': guest.loyalty_points,
            'loyalty_level': GuestSerializer(guest).data['loyalty_level']
        })

    @action(detail=True, methods=['post'])
    def deduct_loyalty_points(self, request, pk=None):
        """Deduct loyalty points from a guest"""
        guest = self.get_object()
        serializer = LoyaltyPointsSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        points = serializer.validated_data['points']
        reason = serializer.validated_data['reason']
        
        if guest.deduct_loyalty_points(points):
            return Response({
                'success': True,
                'message': f'Deducted {points} loyalty points from {guest.full_name}',
                'reason': reason,
                'new_balance': guest.loyalty_points,
                'loyalty_level': GuestSerializer(guest).data['loyalty_level']
            })
        else:
            return Response({
                'success': False,
                'error': 'Insufficient loyalty points',
                'current_balance': guest.loyalty_points,
                'requested_deduction': points
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def reservation_history(self, request, pk=None):
        """Get guest's reservation history"""
        guest = self.get_object()
        reservations = guest.reservations.select_related('bill').prefetch_related('rooms__room')
        
        history_data = []
        for reservation in reservations:
            rooms_data = [
                {
                    'room_number': room.room.number,
                    'room_type': room.room.room_type.name,
                    'rate': float(room.rate)
                }
                for room in reservation.rooms.all()
            ]
            
            bill_data = None
            if hasattr(reservation, 'bill'):
                bill_data = {
                    'bill_number': reservation.bill.bill_number,
                    'total_amount': float(reservation.bill.total_amount),
                    'status': reservation.bill.status
                }
            
            history_data.append({
                'reservation_number': reservation.reservation_number,
                'check_in_date': reservation.check_in_date,
                'check_out_date': reservation.check_out_date,
                'status': reservation.status,
                'adults': reservation.adults,
                'children': reservation.children,
                'rooms': rooms_data,
                'bill': bill_data,
                'created_at': reservation.created_at
            })
        
        return Response({
            'guest': guest.full_name,
            'total_stays': len([r for r in history_data if r['status'] == 'CHECKED_OUT']),
            'reservations': history_data
        })

    @action(detail=True, methods=['post'])
    def mark_vip(self, request, pk=None):
        """Mark guest as VIP"""
        guest = self.get_object()
        guest.is_vip = True
        guest.save(update_fields=['is_vip', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'{guest.full_name} has been marked as VIP'
        })

    @action(detail=True, methods=['post'])
    def remove_vip(self, request, pk=None):
        """Remove VIP status from guest"""
        guest = self.get_object()
        guest.is_vip = False
        guest.save(update_fields=['is_vip', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'VIP status removed from {guest.full_name}'
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced guest search"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        guests = self.get_queryset().filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(documents__document_number__icontains=query)
        ).distinct()
        
        serializer = GuestListSerializer(guests, many=True)
        return Response({
            'query': query,
            'count': len(serializer.data),
            'results': serializer.data
        })


class GuestDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing guest documents"""
    queryset = GuestDocument.objects.select_related('guest')
    serializer_class = GuestDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document_type', 'issuing_country', 'is_verified']
    search_fields = ['document_number', 'guest__first_name', 'guest__last_name']

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired documents"""
        expired_docs = self.get_queryset().filter(
            expiry_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(expired_docs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get documents expiring in next 30 days"""
        from datetime import timedelta
        expiring_date = timezone.now().date() + timedelta(days=30)
        
        expiring_docs = self.get_queryset().filter(
            expiry_date__lte=expiring_date,
            expiry_date__gt=timezone.now().date()
        )
        serializer = self.get_serializer(expiring_docs, many=True)
        return Response(serializer.data)