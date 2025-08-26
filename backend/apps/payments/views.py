from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import PaymentMethod, Bill, Payment
from .serializers import (
    PaymentMethodSerializer, BillSerializer, BillListSerializer,
    BillCreateUpdateSerializer, PaymentSerializer, PaymentCreateSerializer,
    PaymentSummarySerializer, RevenueReportSerializer, PaymentMethodPerformanceSerializer,
    OutstandingPaymentsSerializer, DailyRevenueSerializer
)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment methods"""
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for this payment method"""
        payment_method = self.get_object()
        transactions = payment_method.transaction_set.filter(status='SUCCESS').order_by('-created_at')
        
        # Pagination
        limit = int(request.query_params.get('limit', 50))
        transactions = transactions[:limit]
        
        serializer = PaymentSerializer(transactions, many=True)
        return Response({
            'payment_method': payment_method.name,
            'total_transactions': payment_method.transaction_set.filter(status='SUCCESS').count(),
            'transactions': serializer.data
        })

    @action(detail=False, methods=['get'])
    def performance(self, request):
        """Get performance statistics for all payment methods"""
        payment_methods = self.get_queryset()
        performance_data = []
        
        # Calculate totals for percentage calculations
        total_amount = Payment.objects.filter(status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        for pm in payment_methods:
            transactions = pm.transaction_set.filter(status='SUCCESS')
            pm_total = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            performance_data.append({
                'payment_method': pm.name,
                'total_transactions': transactions.count(),
                'total_amount': float(pm_total),
                'success_rate': 100.0,  # Since we're only looking at successful transactions
                'average_transaction_amount': float(transactions.aggregate(avg=Avg('amount'))['avg'] or 0),
                'percentage_of_total': float((pm_total / total_amount) * 100) if total_amount > 0 else 0
            })
        
        # Sort by total amount descending
        performance_data.sort(key=lambda x: x['total_amount'], reverse=True)
        
        return Response({
            'total_amount': float(total_amount),
            'payment_methods': performance_data
        })


class BillViewSet(viewsets.ModelViewSet):
    """ViewSet for managing bills"""
    queryset = Bill.objects.select_related('reservation__guest').order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'reservation', 'due_date']
    search_fields = ['bill_number', 'reservation__reservation_number', 'reservation__guest__first_name', 'reservation__guest__last_name']
    ordering_fields = ['created_at', 'due_date', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return BillListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BillCreateUpdateSerializer
        return BillSerializer

    @action(detail=False, methods=['get'])
    def unpaid(self, request):
        """Get all unpaid bills"""
        unpaid_bills = self.get_queryset().filter(status__in=['PENDING', 'PARTIALLY_PAID'])
        serializer = BillListSerializer(unpaid_bills, many=True)
        
        total_outstanding = unpaid_bills.aggregate(
            total=Sum(F('total_amount') - F('paid_amount'))
        )['total'] or Decimal('0')
        
        return Response({
            'total_unpaid_bills': unpaid_bills.count(),
            'total_outstanding_amount': float(total_outstanding),
            'bills': serializer.data
        })

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue bills"""
        today = timezone.now().date()
        overdue_bills = self.get_queryset().filter(
            due_date__lt=today,
            status__in=['PENDING', 'PARTIALLY_PAID']
        )
        serializer = BillListSerializer(overdue_bills, many=True)
        
        overdue_data = []
        for bill in overdue_bills:
            days_overdue = (today - bill.due_date).days
            outstanding_amount = bill.total_amount - bill.paid_amount
            
            overdue_data.append({
                'bill_id': bill.id,
                'bill_number': bill.bill_number,
                'reservation_number': bill.reservation.reservation_number,
                'guest_name': bill.reservation.guest.full_name,
                'total_amount': float(bill.total_amount),
                'paid_amount': float(bill.paid_amount),
                'outstanding_amount': float(outstanding_amount),
                'due_date': bill.due_date,
                'days_overdue': days_overdue,
                'status': bill.status
            })
        
        return Response({
            'total_overdue_bills': len(overdue_data),
            'total_overdue_amount': sum([bill['outstanding_amount'] for bill in overdue_data]),
            'overdue_bills': overdue_data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get bills summary statistics"""
        bills = self.get_queryset()
        today = timezone.now().date()
        
        paid_bills = bills.filter(status='PAID')
        partially_paid_bills = bills.filter(status='PARTIALLY_PAID')
        unpaid_bills = bills.filter(status='PENDING')
        overdue_bills = bills.filter(
            due_date__lt=today,
            status__in=['PENDING', 'PARTIALLY_PAID']
        )
        
        total_revenue = paid_bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        total_outstanding = bills.filter(status__in=['PENDING', 'PARTIALLY_PAID']).aggregate(
            total=Sum(F('total_amount') - F('paid_amount'))
        )['total'] or Decimal('0')
        
        summary = {
            'total_bills': bills.count(),
            'paid_bills': paid_bills.count(),
            'partially_paid_bills': partially_paid_bills.count(),
            'unpaid_bills': unpaid_bills.count(),
            'overdue_bills': overdue_bills.count(),
            'total_revenue': float(total_revenue),
            'total_outstanding': float(total_outstanding),
            'average_bill_amount': float(bills.aggregate(avg=Avg('total_amount'))['avg'] or 0)
        }
        
        return Response(summary)

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """Add a payment to the bill"""
        bill = self.get_object()
        
        payment_data = {
            'bill': bill.id,
            'payment_method': request.data.get('payment_method'),
            'amount': request.data.get('amount'),
            'reference_number': request.data.get('reference_number', ''),
            'notes': request.data.get('notes', '')
        }
        
        serializer = PaymentCreateSerializer(data=payment_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = serializer.save()
        
        return Response({
            'success': True,
            'message': f'Payment of {transaction.amount} added to bill {bill.bill_number}',
            'payment': PaymentSerializer(payment).data,
            'bill': BillSerializer(bill).data
        })

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark bill as fully paid (for cash payments or external processing)"""
        bill = self.get_object()
        payment_method_id = request.data.get('payment_method')
        reference_number = request.data.get('reference_number', '')
        notes = request.data.get('notes', 'Marked as paid')
        
        if not payment_method_id:
            return Response({'error': 'payment_method is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        remaining_amount = bill.total_amount - bill.paid_amount
        
        if remaining_amount <= 0:
            return Response({'error': 'Bill is already fully paid'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create transaction for remaining amount
        transaction_data = {
            'bill': bill.id,
            'payment_method': payment_method_id,
            'amount': remaining_amount,
            'reference_number': reference_number,
            'notes': notes
        }
        
        serializer = PaymentCreateSerializer(data=transaction_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = serializer.save()
        
        return Response({
            'success': True,
            'message': f'Bill {bill.bill_number} marked as fully paid',
            'payment': PaymentSerializer(payment).data,
            'bill': BillSerializer(bill).data
        })

    @action(detail=True, methods=['get'])
    def payment_history(self, request, pk=None):
        """Get payment history for the bill"""
        bill = self.get_object()
        transactions = bill.transaction_set.all().order_by('-created_at')
        serializer = PaymentSerializer(transactions, many=True)
        
        return Response({
            'bill_number': bill.bill_number,
            'total_amount': float(bill.total_amount),
            'paid_amount': float(bill.paid_amount),
            'remaining_balance': float(bill.total_amount - bill.paid_amount),
            'payment_history': serializer.data
        })


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing transactions"""
    queryset = Payment.objects.select_related('bill__reservation__guest', 'payment_method').order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bill', 'payment_method', 'status']
    search_fields = ['transaction_id', 'bill__bill_number', 'reference_number']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily transaction summary"""
        # Get date from query params, default to today
        date_param = request.query_params.get('date')
        if date_param:
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date()
        
        # Get transactions for the date
        transactions = self.get_queryset().filter(
            processed_at__date=target_date,
            status='SUCCESS'
        )
        
        # Calculate totals by payment method
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        payment_breakdown = []
        
        for pm in payment_methods:
            pm_transactions = transactions.filter(payment_method=pm)
            pm_total = pm_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if pm_transactions.exists():
                payment_breakdown.append({
                    'payment_method': pm.name,
                    'transaction_count': pm_transactions.count(),
                    'total_amount': float(pm_total)
                })
        
        total_revenue = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        summary = {
            'date': target_date,
            'total_transactions': transactions.count(),
            'total_revenue': float(total_revenue),
            'average_transaction_amount': float(transactions.aggregate(avg=Avg('amount'))['avg'] or 0),
            'payment_method_breakdown': payment_breakdown
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'])
    def revenue_report(self, request):
        """Get revenue report for specified period"""
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to current month
            today = timezone.now().date()
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1)
        
        # Get transactions in date range
        transactions = self.get_queryset().filter(
            processed_at__date__gte=start_date,
            processed_at__date__lt=end_date,
            status='SUCCESS'
        )
        
        total_revenue = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Payment method breakdown
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        payment_breakdown = []
        
        for pm in payment_methods:
            pm_transactions = transactions.filter(payment_method=pm)
            pm_total = pm_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if pm_transactions.exists():
                payment_breakdown.append({
                    'payment_method': pm.name,
                    'transaction_count': pm_transactions.count(),
                    'total_amount': float(pm_total),
                    'percentage': float((pm_total / total_revenue) * 100) if total_revenue > 0 else 0
                })
        
        # Daily revenue breakdown
        daily_revenue = []
        current_date = start_date
        while current_date < end_date:
            daily_transactions = transactions.filter(processed_at__date=current_date)
            daily_total = daily_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if daily_transactions.exists() or daily_total > 0:
                daily_revenue.append({
                    'date': current_date,
                    'total_revenue': float(daily_total),
                    'transaction_count': daily_transactions.count(),
                    'average_transaction': float(daily_transactions.aggregate(avg=Avg('amount'))['avg'] or 0)
                })
            
            current_date += timedelta(days=1)
        
        # Top revenue days
        top_days = sorted(daily_revenue, key=lambda x: x['total_revenue'], reverse=True)[:5]
        
        report = {
            'period': f"{start_date} to {end_date}",
            'total_revenue': float(total_revenue),
            'total_transactions': transactions.count(),
            'average_transaction_amount': float(transactions.aggregate(avg=Avg('amount'))['avg'] or 0),
            'payment_method_breakdown': payment_breakdown,
            'daily_revenue': daily_revenue,
            'top_revenue_days': top_days
        }
        
        return Response(report)

    @action(detail=False, methods=['get'])
    def recent_transactions(self, request):
        """Get recent transactions"""
        limit = int(request.query_params.get('limit', 20))
        recent_transactions = self.get_queryset().filter(status='SUCCESS')[:limit]
        serializer = PaymentSerializer(recent_transactions, many=True)
        
        return Response({
            'total_recent_transactions': limit,
            'transactions': serializer.data
        })

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process refund for a transaction"""
        transaction = self.get_object()
        
        if transaction.status != 'SUCCESS':
            return Response({
                'error': 'Can only refund successful transactions'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        refund_amount = request.data.get('amount')
        reason = request.data.get('reason', 'Refund processed')
        
        if not refund_amount:
            refund_amount = transaction.amount
        else:
            refund_amount = Decimal(str(refund_amount))
            if refund_amount > transaction.amount:
                return Response({
                    'error': f'Refund amount cannot exceed original transaction amount of {transaction.amount}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create refund transaction
        refund_payment = Payment.objects.create(
            bill=transaction.bill,
            payment_method=transaction.payment_method,
            amount=-refund_amount,  # Negative amount for refund
            status='SUCCESS',
            processed_at=timezone.now(),
            reference_number=f"REFUND-{transaction.transaction_id}",
            notes=f"Refund for transaction {transaction.transaction_id}: {reason}"
        )
        
        # Update bill paid amount
        bill = transaction.bill
        bill.paid_amount -= refund_amount
        
        # Update bill status based on new paid amount
        if bill.paid_amount <= 0:
            bill.status = 'PENDING'
        elif bill.paid_amount < bill.total_amount:
            bill.status = 'PARTIALLY_PAID'
        
        bill.save(update_fields=['paid_amount', 'status', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Refund of {refund_amount} processed for transaction {transaction.transaction_id}',
            'refund_payment': PaymentSerializer(refund_payment).data,
            'original_payment': PaymentSerializer(payment).data,
            'bill': BillSerializer(bill).data
        })
