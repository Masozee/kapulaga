from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, F, Max
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import InventoryCategory, Supplier, InventoryItem, StockMovement
from .serializers import (
    InventoryCategorySerializer, SupplierSerializer, InventoryItemSerializer, InventoryItemListSerializer,
    InventoryItemCreateUpdateSerializer, StockMovementSerializer, StockMovementCreateSerializer,
    InventoryReportSerializer, LowStockAlertSerializer, StockValuationSerializer,
    SupplierPerformanceSerializer
)


class InventoryCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing inventory categories"""
    queryset = InventoryCategory.objects.filter(is_active=True)
    serializer_class = InventoryCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items in category"""
        category = self.get_object()
        items = category.inventoryitem_set.filter(is_active=True)
        serializer = InventoryItemListSerializer(items, many=True)
        return Response({
            'category': category.name,
            'total_items': items.count(),
            'total_stock_value': sum([
                float(item.current_stock * item.unit_cost) 
                for item in items
            ]),
            'items': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get category summary statistics"""
        categories = self.get_queryset()
        summary_data = []
        
        for category in categories:
            items = category.inventoryitem_set.filter(is_active=True)
            low_stock_items = items.filter(current_stock__lte=F('minimum_stock'))
            out_of_stock_items = items.filter(current_stock=0)
            
            summary_data.append({
                'id': category.id,
                'name': category.name,
                'total_items': items.count(),
                'low_stock_items': low_stock_items.count(),
                'out_of_stock_items': out_of_stock_items.count(),
                'total_stock_value': sum([
                    float(item.current_stock * item.unit_cost) 
                    for item in items
                ])
            })
        
        return Response(summary_data)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing suppliers"""
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'country']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items supplied by this supplier"""
        supplier = self.get_object()
        items = supplier.inventoryitem_set.filter(is_active=True)
        serializer = InventoryItemListSerializer(items, many=True)
        return Response({
            'supplier': supplier.name,
            'total_items': items.count(),
            'items': serializer.data
        })

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get supplier performance metrics"""
        supplier = self.get_object()
        
        # Get stock movements from this supplier
        movements = supplier.stockmovement_set.filter(movement_type='IN')
        
        total_orders = movements.count()
        total_value = movements.aggregate(
            total=Sum(F('quantity') * F('unit_cost'))
        )['total'] or Decimal('0')
        
        last_order = movements.order_by('-created_at').first()
        
        performance_data = {
            'supplier': supplier.name,
            'total_orders': total_orders,
            'total_items_supplied': supplier.inventoryitem_set.filter(is_active=True).count(),
            'total_value_supplied': float(total_value),
            'average_order_value': float(total_value / total_orders) if total_orders > 0 else 0,
            'last_order_date': last_order.created_at if last_order else None,
            'payment_terms': supplier.payment_terms
        }
        
        return Response(performance_data)

    @action(detail=False, methods=['get'])
    def top_suppliers(self, request):
        """Get top suppliers by order volume"""
        suppliers = self.get_queryset().annotate(
            total_orders=Count('stockmovement', filter=Q(stockmovement__movement_type='IN')),
            total_value=Sum(F('stockmovement__quantity') * F('stockmovement__unit_cost'))
        ).filter(total_orders__gt=0).order_by('-total_value')[:10]
        
        top_suppliers_data = []
        for supplier in suppliers:
            top_suppliers_data.append({
                'id': supplier.id,
                'name': supplier.name,
                'total_orders': supplier.total_orders,
                'total_value': float(supplier.total_value or 0),
                'items_supplied': supplier.inventoryitem_set.filter(is_active=True).count()
            })
        
        return Response(top_suppliers_data)


class InventoryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing inventory items"""
    queryset = InventoryItem.objects.select_related('category', 'supplier').filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'supplier', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'current_stock', 'unit_cost', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return InventoryItemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return InventoryItemCreateUpdateSerializer
        return InventoryItemSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items with low stock"""
        low_stock_items = self.get_queryset().filter(
            current_stock__lte=F('minimum_stock')
        ).exclude(current_stock=0).order_by('current_stock')
        
        serializer = InventoryItemListSerializer(low_stock_items, many=True)
        return Response({
            'total_low_stock_items': low_stock_items.count(),
            'items': serializer.data
        })

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get items that are out of stock"""
        out_of_stock_items = self.get_queryset().filter(current_stock=0)
        serializer = InventoryItemListSerializer(out_of_stock_items, many=True)
        return Response({
            'total_out_of_stock_items': out_of_stock_items.count(),
            'items': serializer.data
        })

    @action(detail=False, methods=['get'])
    def stock_alerts(self, request):
        """Get comprehensive stock alerts"""
        current_time = timezone.now()
        
        # Get items with stock issues
        low_stock_items = self.get_queryset().filter(
            current_stock__lte=F('minimum_stock')
        ).exclude(current_stock=0)
        
        out_of_stock_items = self.get_queryset().filter(current_stock=0)
        
        # Format alert data
        alerts = []
        
        # Low stock alerts
        for item in low_stock_items:
            last_movement = item.movements.filter(
                movement_type='IN'
            ).order_by('-created_at').first()
            
            days_since_restock = 0
            if last_movement:
                days_since_restock = (current_time - last_movement.created_at).days
            
            alerts.append({
                'item_id': item.id,
                'item_name': item.name,
                'sku': item.sku,
                'current_stock': item.current_stock,
                'minimum_stock': item.minimum_stock,
                'category': item.category.name,
                'supplier': item.supplier.name if item.supplier else 'No supplier',
                'stock_status': 'LOW_STOCK',
                'days_since_last_restock': days_since_restock,
                'priority': 'HIGH' if item.current_stock <= (item.minimum_stock * 0.5) else 'MEDIUM'
            })
        
        # Out of stock alerts
        for item in out_of_stock_items:
            last_movement = item.movements.filter(
                movement_type='OUT'
            ).order_by('-created_at').first()
            
            days_since_out = 0
            if last_movement:
                days_since_out = (current_time - last_movement.created_at).days
            
            alerts.append({
                'item_id': item.id,
                'item_name': item.name,
                'sku': item.sku,
                'current_stock': item.current_stock,
                'minimum_stock': item.minimum_stock,
                'category': item.category.name,
                'supplier': item.supplier.name if item.supplier else 'No supplier',
                'stock_status': 'OUT_OF_STOCK',
                'days_since_last_restock': days_since_out,
                'priority': 'CRITICAL'
            })
        
        return Response({
            'total_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a['priority'] == 'CRITICAL']),
            'high_alerts': len([a for a in alerts if a['priority'] == 'HIGH']),
            'medium_alerts': len([a for a in alerts if a['priority'] == 'MEDIUM']),
            'alerts': alerts
        })

    @action(detail=False, methods=['get'])
    def valuation(self, request):
        """Get inventory valuation report"""
        items = self.get_queryset().filter(current_stock__gt=0)
        
        total_value = Decimal('0')
        valuation_data = []
        
        for item in items:
            stock_value = item.current_stock * item.unit_cost
            total_value += stock_value
            
            valuation_data.append({
                'item_id': item.id,
                'item_name': item.name,
                'sku': item.sku,
                'category': item.category.name,
                'current_stock': item.current_stock,
                'unit_cost': item.unit_cost,
                'stock_value': stock_value
            })
        
        # Calculate percentages
        for item_data in valuation_data:
            item_data['percentage_of_total'] = round(
                (float(item_data['stock_value']) / float(total_value)) * 100, 2
            ) if total_value > 0 else 0
            item_data['stock_value'] = float(item_data['stock_value'])
            item_data['unit_cost'] = float(item_data['unit_cost'])
        
        # Sort by stock value descending
        valuation_data.sort(key=lambda x: x['stock_value'], reverse=True)
        
        return Response({
            'total_inventory_value': float(total_value),
            'total_items_valued': len(valuation_data),
            'valuation_date': timezone.now().date(),
            'items': valuation_data[:50]  # Top 50 by value
        })

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Manually adjust item stock"""
        item = self.get_object()
        new_stock = request.data.get('new_stock')
        reason = request.data.get('reason', 'Manual adjustment')
        
        if new_stock is None:
            return Response({'error': 'new_stock is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                raise ValueError()
        except ValueError:
            return Response({'error': 'Invalid stock quantity'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_stock = item.current_stock
        adjustment = new_stock - old_stock
        
        # Create stock movement record
        if adjustment != 0:
            movement_type = 'IN' if adjustment > 0 else 'OUT'
            StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=abs(adjustment),
                unit_cost=item.unit_cost,
                notes=f"Stock adjustment: {reason}",
                reference_number=f"ADJ-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
        
        # Update item stock
        item.current_stock = new_stock
        item.save(update_fields=['current_stock', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Stock adjusted for {item.name}',
            'old_stock': old_stock,
            'new_stock': new_stock,
            'adjustment': adjustment,
            'reason': reason,
            'item': InventoryItemSerializer(item).data
        })

    @action(detail=True, methods=['get'])
    def movement_history(self, request, pk=None):
        """Get stock movement history for item"""
        item = self.get_object()
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        movements = item.movements.filter(
            created_at__gte=start_date
        ).order_by('-created_at')
        
        serializer = StockMovementSerializer(movements, many=True)
        
        # Calculate statistics
        in_movements = movements.filter(movement_type='IN')
        out_movements = movements.filter(movement_type='OUT')
        
        total_in = in_movements.aggregate(total=Sum('quantity'))['total'] or 0
        total_out = out_movements.aggregate(total=Sum('quantity'))['total'] or 0
        
        return Response({
            'item': item.name,
            'period_days': days,
            'total_movements': movements.count(),
            'total_in': total_in,
            'total_out': total_out,
            'net_change': total_in - total_out,
            'current_stock': item.current_stock,
            'movements': serializer.data
        })


class StockMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing stock movements"""
    queryset = StockMovement.objects.select_related('item', 'supplier').order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['item', 'movement_type', 'supplier']
    search_fields = ['item__name', 'item__sku', 'reference_number']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return StockMovementCreateSerializer
        return StockMovementSerializer

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily stock movement summary"""
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
        
        # Get movements for the date
        movements = self.get_queryset().filter(
            created_at__date=target_date
        )
        
        in_movements = movements.filter(movement_type='IN')
        out_movements = movements.filter(movement_type='OUT')
        
        summary = {
            'date': target_date,
            'total_movements': movements.count(),
            'in_movements': in_movements.count(),
            'out_movements': out_movements.count(),
            'total_in_quantity': in_movements.aggregate(total=Sum('quantity'))['total'] or 0,
            'total_out_quantity': out_movements.aggregate(total=Sum('quantity'))['total'] or 0,
            'total_in_value': float(in_movements.aggregate(
                total=Sum(F('quantity') * F('unit_cost'))
            )['total'] or 0),
            'total_out_value': float(out_movements.aggregate(
                total=Sum(F('quantity') * F('unit_cost'))
            )['total'] or 0)
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Get recent stock movement activities"""
        limit = int(request.query_params.get('limit', 20))
        recent_movements = self.get_queryset()[:limit]
        serializer = StockMovementSerializer(recent_movements, many=True)
        
        return Response({
            'total_recent_activities': limit,
            'activities': serializer.data
        })

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """Get monthly stock movement report"""
        # Get month/year from query params
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if month and year:
            try:
                target_date = datetime(int(year), int(month), 1).date()
            except ValueError:
                return Response({
                    'error': 'Invalid month or year'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date().replace(day=1)
        
        # Calculate month range
        if target_date.month == 12:
            next_month = target_date.replace(year=target_date.year + 1, month=1)
        else:
            next_month = target_date.replace(month=target_date.month + 1)
        
        movements = self.get_queryset().filter(
            created_at__date__gte=target_date,
            created_at__date__lt=next_month
        )
        
        in_movements = movements.filter(movement_type='IN')
        out_movements = movements.filter(movement_type='OUT')
        
        # Category breakdown
        categories = InventoryCategory.objects.filter(is_active=True)
        category_stats = []
        
        for category in categories:
            cat_in = in_movements.filter(item__category=category)
            cat_out = out_movements.filter(item__category=category)
            
            if cat_in.exists() or cat_out.exists():
                category_stats.append({
                    'category': category.name,
                    'in_quantity': cat_in.aggregate(total=Sum('quantity'))['total'] or 0,
                    'out_quantity': cat_out.aggregate(total=Sum('quantity'))['total'] or 0,
                    'in_value': float(cat_in.aggregate(
                        total=Sum(F('quantity') * F('unit_cost'))
                    )['total'] or 0),
                    'out_value': float(cat_out.aggregate(
                        total=Sum(F('quantity') * F('unit_cost'))
                    )['total'] or 0)
                })
        
        return Response({
            'month': target_date.strftime('%B %Y'),
            'total_movements': movements.count(),
            'summary': {
                'total_in_quantity': in_movements.aggregate(total=Sum('quantity'))['total'] or 0,
                'total_out_quantity': out_movements.aggregate(total=Sum('quantity'))['total'] or 0,
                'total_in_value': float(in_movements.aggregate(
                    total=Sum(F('quantity') * F('unit_cost'))
                )['total'] or 0),
                'total_out_value': float(out_movements.aggregate(
                    total=Sum(F('quantity') * F('unit_cost'))
                )['total'] or 0)
            },
            'category_breakdown': category_stats
        })
