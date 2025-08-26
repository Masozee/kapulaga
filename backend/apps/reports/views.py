from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .serializers import (
    OccupancyReportSerializer, RevenueReportSerializer, BookingAnalyticsSerializer,
    GuestAnalyticsSerializer, FinancialSummarySerializer, OperationalReportSerializer,
    InventoryReportSerializer, StaffReportSerializer, ForecastReportSerializer,
    CustomReportSerializer, ExportRequestSerializer, DashboardMetricsSerializer,
    TrendAnalysisSerializer, KPIReportSerializer
)


class ReportsViewSet(viewsets.ViewSet):
    """ViewSet for generating various hotel reports"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def occupancy_report(self, request):
        """Generate occupancy report"""
        # Get date range from query params
        start_date, end_date = self._get_date_range(request)
        
        from apps.rooms.models import Room
        from apps.checkin.models import CheckIn
        
        # Get room statistics
        total_rooms = Room.objects.filter(is_active=True).count()
        
        # Generate daily occupancy data
        occupancy_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Get check-ins for this date
            checkins = CheckIn.objects.filter(
                check_in_time__date__lte=current_date
            ).filter(
                Q(check_out_time__date__gt=current_date) | Q(check_out_time__isnull=True)
            )
            
            occupied_rooms = checkins.count()
            available_rooms = total_rooms - occupied_rooms
            
            # Room status breakdown
            room_statuses = Room.objects.filter(is_active=True).values('status').annotate(
                count=Count('id')
            )
            
            out_of_order = next((item['count'] for item in room_statuses if item['status'] == 'OUT_OF_ORDER'), 0)
            maintenance = next((item['count'] for item in room_statuses if item['status'] == 'MAINTENANCE'), 0)
            
            occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
            
            # Room type breakdown
            from apps.rooms.models import RoomType
            room_types = RoomType.objects.filter(is_active=True)
            room_type_breakdown = []
            
            for room_type in room_types:
                type_rooms = room_type.room_set.filter(is_active=True)
                type_occupied = checkins.filter(
                    reservation__rooms__room__room_type=room_type
                ).distinct().count()
                
                room_type_breakdown.append({
                    'room_type': room_type.name,
                    'total_rooms': type_rooms.count(),
                    'occupied_rooms': type_occupied,
                    'occupancy_rate': round((type_occupied / type_rooms.count()) * 100, 1) if type_rooms.count() > 0 else 0
                })
            
            occupancy_data.append({
                'date': current_date,
                'total_rooms': total_rooms,
                'occupied_rooms': occupied_rooms,
                'available_rooms': available_rooms,
                'out_of_order_rooms': out_of_order,
                'maintenance_rooms': maintenance,
                'occupancy_rate': round(occupancy_rate, 1),
                'room_type_breakdown': room_type_breakdown
            })
            
            current_date += timedelta(days=1)
        
        return Response({
            'period': f"{start_date} to {end_date}",
            'summary': {
                'average_occupancy_rate': round(
                    sum(day['occupancy_rate'] for day in occupancy_data) / len(occupancy_data), 1
                ) if occupancy_data else 0,
                'peak_occupancy_date': max(occupancy_data, key=lambda x: x['occupancy_rate'])['date'] if occupancy_data else None,
                'lowest_occupancy_date': min(occupancy_data, key=lambda x: x['occupancy_rate'])['date'] if occupancy_data else None
            },
            'daily_data': occupancy_data
        })

    @action(detail=False, methods=['get'])
    def revenue_report(self, request):
        """Generate revenue report"""
        start_date, end_date = self._get_date_range(request)
        
        from apps.payments.models import Bill, Payment
        from apps.reservations.models import Reservation
        
        # Get paid bills in the period
        bills = Bill.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='PAID'
        )
        
        # Calculate totals
        total_revenue = bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        room_revenue = bills.aggregate(total=Sum('subtotal'))['total'] or Decimal('0')
        tax_amount = bills.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        service_charge = bills.aggregate(total=Sum('service_charge'))['total'] or Decimal('0')
        discount_amount = bills.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0')
        
        additional_revenue = total_revenue - room_revenue - tax_amount - service_charge + discount_amount
        
        # Calculate ADR and RevPAR
        completed_reservations = Reservation.objects.filter(
            status='CHECKED_OUT',
            check_out_date__gte=start_date,
            check_out_date__lte=end_date
        )
        
        total_room_nights = sum(res.nights for res in completed_reservations)
        
        from apps.rooms.models import Room
        total_available_room_nights = Room.objects.filter(is_active=True).count() * (end_date - start_date).days
        
        adr = (room_revenue / total_room_nights) if total_room_nights > 0 else Decimal('0')
        revpar = (room_revenue / total_available_room_nights) if total_available_room_nights > 0 else Decimal('0')
        
        # Daily breakdown
        daily_breakdown = []
        current_date = start_date
        
        while current_date <= end_date:
            daily_bills = bills.filter(created_at__date=current_date)
            daily_revenue = daily_bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            daily_breakdown.append({
                'date': current_date,
                'revenue': float(daily_revenue),
                'bills_count': daily_bills.count()
            })
            
            current_date += timedelta(days=1)
        
        return Response({
            'period_start': start_date,
            'period_end': end_date,
            'total_revenue': float(total_revenue),
            'room_revenue': float(room_revenue),
            'additional_revenue': float(additional_revenue),
            'tax_amount': float(tax_amount),
            'service_charge': float(service_charge),
            'discount_amount': float(discount_amount),
            'average_daily_rate': float(adr),
            'revenue_per_available_room': float(revpar),
            'daily_breakdown': daily_breakdown,
            'summary_metrics': {
                'total_bills': bills.count(),
                'average_bill_amount': float(bills.aggregate(avg=Avg('total_amount'))['avg'] or 0),
                'highest_revenue_day': max(daily_breakdown, key=lambda x: x['revenue'])['date'] if daily_breakdown else None
            }
        })

    @action(detail=False, methods=['get'])
    def booking_analytics(self, request):
        """Generate booking analytics report"""
        start_date, end_date = self._get_date_range(request)
        
        from apps.reservations.models import Reservation
        
        # Get reservations in the period
        reservations = Reservation.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Status breakdown
        total_reservations = reservations.count()
        confirmed_reservations = reservations.filter(status='CONFIRMED').count()
        cancelled_reservations = reservations.filter(status='CANCELLED').count()
        checked_in_reservations = reservations.filter(status='CHECKED_IN').count()
        checked_out_reservations = reservations.filter(status='CHECKED_OUT').count()
        no_show_reservations = reservations.filter(status='NO_SHOW').count()
        
        # Booking source breakdown
        booking_sources = reservations.values('booking_source').annotate(
            count=Count('id')
        ).order_by('-count')
        
        booking_source_breakdown = [
            {
                'source': item['booking_source'],
                'count': item['count'],
                'percentage': round((item['count'] / total_reservations) * 100, 1) if total_reservations > 0 else 0
            }
            for item in booking_sources
        ]
        
        # Lead time analysis
        reservations_with_lead_time = reservations.exclude(check_in_date__isnull=True)
        lead_times = []
        
        for reservation in reservations_with_lead_time:
            lead_time = (reservation.check_in_date - reservation.created_at.date()).days
            lead_times.append(lead_time)
        
        lead_time_analysis = {
            'average_lead_time': round(sum(lead_times) / len(lead_times), 1) if lead_times else 0,
            'median_lead_time': sorted(lead_times)[len(lead_times)//2] if lead_times else 0,
            'same_day_bookings': len([lt for lt in lead_times if lt == 0]),
            'advance_bookings_7_days': len([lt for lt in lead_times if lt >= 7]),
            'advance_bookings_30_days': len([lt for lt in lead_times if lt >= 30])
        }
        
        # Calculate rates
        cancellation_rate = (cancelled_reservations / total_reservations) * 100 if total_reservations > 0 else 0
        show_rate = ((confirmed_reservations + checked_in_reservations + checked_out_reservations) / total_reservations) * 100 if total_reservations > 0 else 0
        
        return Response({
            'period': f"{start_date} to {end_date}",
            'total_reservations': total_reservations,
            'confirmed_reservations': confirmed_reservations,
            'cancelled_reservations': cancelled_reservations,
            'checked_in_reservations': checked_in_reservations,
            'checked_out_reservations': checked_out_reservations,
            'no_show_reservations': no_show_reservations,
            'booking_source_breakdown': booking_source_breakdown,
            'lead_time_analysis': lead_time_analysis,
            'cancellation_rate': round(cancellation_rate, 1),
            'show_rate': round(show_rate, 1)
        })

    @action(detail=False, methods=['get'])
    def guest_analytics(self, request):
        """Generate guest analytics report"""
        start_date, end_date = self._get_date_range(request)
        
        from apps.guests.models import Guest
        from apps.reservations.models import Reservation
        
        # Get guests who had reservations in the period
        guests_in_period = Guest.objects.filter(
            reservations__created_at__date__gte=start_date,
            reservations__created_at__date__lte=end_date
        ).distinct()
        
        # New vs returning guests
        new_guests = guests_in_period.filter(created_at__date__gte=start_date).count()
        returning_guests = guests_in_period.filter(created_at__date__lt=start_date).count()
        total_guests = guests_in_period.count()
        vip_guests = guests_in_period.filter(is_vip=True).count()
        
        # Nationality breakdown
        nationality_breakdown = guests_in_period.values('nationality').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        guest_nationality_breakdown = [
            {
                'nationality': item['nationality'] or 'Unknown',
                'count': item['count'],
                'percentage': round((item['count'] / total_guests) * 100, 1) if total_guests > 0 else 0
            }
            for item in nationality_breakdown
        ]
        
        # Loyalty program stats
        loyalty_stats = {
            'total_members': guests_in_period.filter(loyalty_points__gt=0).count(),
            'platinum_members': guests_in_period.filter(loyalty_points__gte=1000).count(),
            'gold_members': guests_in_period.filter(loyalty_points__gte=500, loyalty_points__lt=1000).count(),
            'silver_members': guests_in_period.filter(loyalty_points__gte=100, loyalty_points__lt=500).count(),
            'bronze_members': guests_in_period.filter(loyalty_points__lt=100, loyalty_points__gt=0).count(),
            'average_points': float(guests_in_period.aggregate(avg=Avg('loyalty_points'))['avg'] or 0)
        }
        
        # Average stay duration
        completed_reservations = Reservation.objects.filter(
            guest__in=guests_in_period,
            status='CHECKED_OUT'
        )
        
        avg_stay_duration = completed_reservations.aggregate(avg=Avg('nights'))['avg'] or 0
        
        return Response({
            'period': f"{start_date} to {end_date}",
            'total_guests': total_guests,
            'new_guests': new_guests,
            'returning_guests': returning_guests,
            'vip_guests': vip_guests,
            'guest_nationality_breakdown': guest_nationality_breakdown,
            'loyalty_program_stats': loyalty_stats,
            'average_stay_duration': float(avg_stay_duration),
            'guest_satisfaction_metrics': {
                'surveys_collected': 0,  # Placeholder for future implementation
                'average_rating': 0,
                'satisfaction_score': 0
            }
        })

    @action(detail=False, methods=['get'])
    def financial_summary(self, request):
        """Generate financial summary report"""
        start_date, end_date = self._get_date_range(request)
        
        from apps.payments.models import Bill, Payment, PaymentMethod
        
        bills_in_period = Bill.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Revenue calculations
        gross_revenue = bills_in_period.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        total_discounts = bills_in_period.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0')
        total_taxes = bills_in_period.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
        total_service_charges = bills_in_period.aggregate(total=Sum('service_charge'))['total'] or Decimal('0')
        
        net_revenue = gross_revenue - total_discounts
        
        # Outstanding payments
        outstanding_payments = bills_in_period.filter(
            status__in=['PENDING', 'PARTIALLY_PAID']
        ).aggregate(
            total=Sum(F('total_amount') - F('paid_amount'))
        )['total'] or Decimal('0')
        
        # Payment method breakdown
        successful_payments = Payment.objects.filter(
            bill__in=bills_in_period,
            status='COMPLETED'
        )
        
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        payment_method_breakdown = []
        
        for pm in payment_methods:
            pm_transactions = successful_transactions.filter(payment_method=pm)
            pm_total = pm_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if pm_transactions.exists():
                payment_method_breakdown.append({
                    'payment_method': pm.name,
                    'total_amount': float(pm_total),
                    'transaction_count': pm_transactions.count(),
                    'percentage': float((pm_total / gross_revenue) * 100) if gross_revenue > 0 else 0
                })
        
        # Cost breakdown (placeholder for future implementation)
        cost_breakdown = {
            'staff_costs': 0,
            'utilities': 0,
            'maintenance': 0,
            'inventory': 0,
            'marketing': 0,
            'other': 0
        }
        
        # Profit margins (simplified)
        profit_margins = {
            'gross_margin': float((net_revenue / gross_revenue) * 100) if gross_revenue > 0 else 0,
            'operating_margin': 0,  # Placeholder
            'net_margin': 0  # Placeholder
        }
        
        return Response({
            'period': f"{start_date} to {end_date}",
            'gross_revenue': float(gross_revenue),
            'net_revenue': float(net_revenue),
            'total_discounts': float(total_discounts),
            'total_taxes': float(total_taxes),
            'total_service_charges': float(total_service_charges),
            'outstanding_payments': float(outstanding_payments),
            'payment_method_breakdown': payment_method_breakdown,
            'cost_breakdown': cost_breakdown,
            'profit_margins': profit_margins
        })

    @action(detail=False, methods=['get'])
    def operational_report(self, request):
        """Generate operational report"""
        report_date = request.query_params.get('date')
        if report_date:
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        else:
            report_date = timezone.now().date()
        
        from apps.rooms.models import Room
        from apps.checkin.models import CheckIn
        from apps.employees.models import Employee, Attendance
        from apps.inventory.models import InventoryItem
        
        # Occupancy metrics
        total_rooms = Room.objects.filter(is_active=True).count()
        occupied_rooms = CheckIn.objects.filter(
            check_in_time__date__lte=report_date
        ).filter(
            Q(check_out_time__date__gt=report_date) | Q(check_out_time__isnull=True)
        ).count()
        
        occupancy_metrics = {
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'occupancy_rate': round((occupied_rooms / total_rooms) * 100, 1) if total_rooms > 0 else 0,
            'available_rooms': total_rooms - occupied_rooms
        }
        
        # Staff metrics
        total_staff = Employee.objects.filter(is_active=True).count()
        staff_attendance = Attendance.objects.filter(date=report_date)
        present_staff = staff_attendance.filter(status__in=['PRESENT', 'LATE']).count()
        
        staff_metrics = {
            'total_staff': total_staff,
            'present_staff': present_staff,
            'attendance_rate': round((present_staff / total_staff) * 100, 1) if total_staff > 0 else 0,
            'absent_staff': total_staff - present_staff
        }
        
        # Maintenance metrics
        maintenance_rooms = Room.objects.filter(status='MAINTENANCE').count()
        out_of_order_rooms = Room.objects.filter(status='OUT_OF_ORDER').count()
        
        maintenance_metrics = {
            'maintenance_rooms': maintenance_rooms,
            'out_of_order_rooms': out_of_order_rooms,
            'total_unavailable': maintenance_rooms + out_of_order_rooms
        }
        
        # Inventory alerts
        low_stock_items = InventoryItem.objects.filter(
            current_stock__lte=F('minimum_stock'),
            is_active=True
        )
        out_of_stock_items = InventoryItem.objects.filter(current_stock=0, is_active=True)
        
        inventory_alerts = [
            {
                'type': 'LOW_STOCK',
                'count': low_stock_items.count(),
                'items': [{'name': item.name, 'current_stock': item.current_stock, 'minimum_stock': item.minimum_stock} for item in low_stock_items[:5]]
            },
            {
                'type': 'OUT_OF_STOCK',
                'count': out_of_stock_items.count(),
                'items': [{'name': item.name, 'category': item.category.name} for item in out_of_stock_items[:5]]
            }
        ]
        
        # Room status summary
        room_status_summary = Room.objects.filter(is_active=True).values('status').annotate(
            count=Count('id')
        )
        
        room_status_dict = {item['status']: item['count'] for item in room_status_summary}
        
        # KPIs
        kpis = {
            'occupancy_rate': occupancy_metrics['occupancy_rate'],
            'staff_attendance_rate': staff_metrics['attendance_rate'],
            'rooms_out_of_service': maintenance_metrics['total_unavailable'],
            'inventory_alerts': low_stock_items.count() + out_of_stock_items.count()
        }
        
        return Response({
            'report_date': report_date,
            'occupancy_metrics': occupancy_metrics,
            'staff_metrics': staff_metrics,
            'maintenance_metrics': maintenance_metrics,
            'inventory_alerts': inventory_alerts,
            'room_status_summary': room_status_dict,
            'key_performance_indicators': kpis
        })

    @action(detail=False, methods=['get'])
    def dashboard_metrics(self, request):
        """Get key metrics for dashboard"""
        today = timezone.now().date()
        
        from apps.rooms.models import Room
        from apps.checkin.models import CheckIn
        from apps.payments.models import Bill
        from apps.inventory.models import InventoryItem
        
        # Calculate key metrics
        total_rooms = Room.objects.filter(is_active=True).count()
        occupied_rooms = CheckIn.objects.filter(
            check_in_time__date__lte=today
        ).filter(
            Q(check_out_time__date__gt=today) | Q(check_out_time__isnull=True)
        ).count()
        
        occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
        
        # Today's revenue
        today_revenue = Bill.objects.filter(
            created_at__date=today,
            status='PAID'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Pending payments
        pending_payments = Bill.objects.filter(
            status__in=['PENDING', 'PARTIALLY_PAID']
        ).aggregate(
            total=Sum(F('total_amount') - F('paid_amount'))
        )['total'] or Decimal('0')
        
        # Inventory alerts
        inventory_alerts = InventoryItem.objects.filter(
            is_active=True
        ).filter(
            Q(current_stock__lte=F('minimum_stock')) | Q(current_stock=0)
        ).count()
        
        # Room status breakdown
        room_status = Room.objects.filter(is_active=True).values('status').annotate(
            count=Count('id')
        )
        room_status_dict = {item['status']: item['count'] for item in room_status}
        
        return Response({
            'date': today,
            'occupancy_rate': round(occupancy_rate, 1),
            'adr': 0,  # Placeholder - would need more complex calculation
            'revpar': 0,  # Placeholder - would need more complex calculation
            'total_revenue': float(today_revenue),
            'guest_satisfaction': 0,  # Placeholder for future implementation
            'staff_attendance': 0,  # Placeholder - would need today's attendance data
            'inventory_alerts': inventory_alerts,
            'pending_payments': float(pending_payments),
            'room_status': room_status_dict
        })

    @action(detail=False, methods=['post'])
    def export_report(self, request):
        """Export report to PDF/Excel/CSV"""
        serializer = ExportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        # This would integrate with a report generation service
        # For now, return a placeholder response
        
        return Response({
            'success': True,
            'message': f'{validated_data["report_type"]} report export initiated',
            'export_format': validated_data['format'],
            'export_id': f'RPT-{timezone.now().strftime("%Y%m%d%H%M%S")}',
            'estimated_completion': timezone.now() + timedelta(minutes=5)
        })

    def _get_date_range(self, request):
        """Helper method to get date range from request parameters"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        
        return start_date, end_date
