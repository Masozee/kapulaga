from rest_framework import serializers
from decimal import Decimal
from .models import InventoryCategory, Supplier, InventoryItem, StockMovement


class InventoryCategorySerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    total_stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryCategory
        fields = [
            'id', 'name', 'description', 'is_active', 'created_at', 'updated_at',
            'items_count', 'total_stock_value'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_items_count(self, obj):
        """Get total number of items in category"""
        return obj.inventoryitem_set.filter(is_active=True).count()

    def get_total_stock_value(self, obj):
        """Get total stock value for category"""
        total = sum([
            item.current_stock * item.unit_cost 
            for item in obj.inventoryitem_set.filter(is_active=True)
        ])
        return float(total)


class SupplierSerializer(serializers.ModelSerializer):
    contact_person_display = serializers.SerializerMethodField()
    items_supplied = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'contact_person_display', 'email', 
            'phone', 'address', 'city', 'country', 'payment_terms', 'is_active',
            'created_at', 'updated_at', 'items_supplied', 'total_orders'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_contact_person_display(self, obj):
        """Get formatted contact person info"""
        if obj.contact_person and obj.email:
            return f"{obj.contact_person} ({obj.email})"
        return obj.contact_person or obj.email or "No contact info"

    def get_items_supplied(self, obj):
        """Get count of items supplied by this supplier"""
        return obj.inventoryitem_set.filter(is_active=True).count()

    def get_total_orders(self, obj):
        """Get total number of stock movements from this supplier"""
        return obj.stockmovement_set.filter(movement_type='IN').count()


class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    stock_value = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    recent_movements = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'sku', 'category', 'category_name',
            'supplier', 'supplier_name', 'unit', 'current_stock', 'minimum_stock',
            'unit_cost', 'stock_value', 'stock_status', 'location', 'is_active',
            'created_at', 'updated_at', 'recent_movements'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_stock_value(self, obj):
        """Calculate total stock value"""
        return float(obj.current_stock * obj.unit_cost)

    def get_stock_status(self, obj):
        """Get stock status based on minimum stock level"""
        if obj.current_stock <= 0:
            return {'status': 'OUT_OF_STOCK', 'color': 'red'}
        elif obj.current_stock <= obj.minimum_stock:
            return {'status': 'LOW_STOCK', 'color': 'orange'}
        elif obj.current_stock <= (obj.minimum_stock * 2):
            return {'status': 'MODERATE_STOCK', 'color': 'yellow'}
        else:
            return {'status': 'IN_STOCK', 'color': 'green'}

    def get_recent_movements(self, obj):
        """Get last 5 stock movements"""
        movements = obj.movements.order_by('-created_at')[:5]
        return StockMovementSerializer(movements, many=True).data


class InventoryItemListSerializer(serializers.ModelSerializer):
    """Simplified serializer for item listings"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'sku', 'category_name', 'current_stock',
            'minimum_stock', 'unit_cost', 'stock_value', 'stock_status',
            'is_active'
        ]

    def get_stock_status(self, obj):
        """Get stock status"""
        if obj.current_stock <= 0:
            return 'OUT_OF_STOCK'
        elif obj.current_stock <= obj.minimum_stock:
            return 'LOW_STOCK'
        else:
            return 'IN_STOCK'

    def get_stock_value(self, obj):
        """Calculate stock value"""
        return float(obj.current_stock * obj.unit_cost)


class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating items"""
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'description', 'sku', 'category', 'supplier', 'unit',
            'current_stock', 'minimum_stock', 'unit_cost', 'location'
        ]

    def validate_sku(self, value):
        """Validate SKU uniqueness"""
        if self.instance:
            if InventoryItem.objects.exclude(pk=self.instance.pk).filter(sku=value).exists():
                raise serializers.ValidationError("Item with this SKU already exists.")
        else:
            if InventoryItem.objects.filter(sku=value).exists():
                raise serializers.ValidationError("Item with this SKU already exists.")
        return value

    def validate(self, data):
        """Validate item data"""
        if data.get('current_stock', 0) < 0:
            raise serializers.ValidationError("Current stock cannot be negative.")
        
        if data.get('minimum_stock', 0) < 0:
            raise serializers.ValidationError("Minimum stock cannot be negative.")
        
        if data.get('unit_cost', 0) <= 0:
            raise serializers.ValidationError("Unit cost must be greater than zero.")
        
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_sku = serializers.CharField(source='item.sku', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_name', 'item_sku', 'movement_type',
            'movement_type_display', 'quantity', 'unit_cost', 'total_cost',
            'supplier', 'supplier_name', 'reference_number', 'notes',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_total_cost(self, obj):
        """Calculate total cost of movement"""
        return float(obj.quantity * obj.unit_cost)


class StockMovementCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating stock movements"""
    class Meta:
        model = StockMovement
        fields = [
            'item', 'movement_type', 'quantity', 'unit_cost', 'supplier',
            'reference_number', 'notes'
        ]

    def validate(self, data):
        """Validate stock movement data"""
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        
        if data['unit_cost'] < 0:
            raise serializers.ValidationError("Unit cost cannot be negative.")
        
        # For OUT movements, check if there's enough stock
        if data['movement_type'] == 'OUT':
            item = data['item']
            if item.current_stock < data['quantity']:
                raise serializers.ValidationError(
                    f"Insufficient stock. Available: {item.current_stock}, Requested: {data['quantity']}"
                )
        
        return data

    def create(self, validated_data):
        """Create stock movement and update item stock"""
        movement = StockMovement.objects.create(**validated_data)
        
        # Update item stock based on movement type
        item = movement.item
        if movement.movement_type == 'IN':
            item.current_stock += movement.quantity
            # Update unit cost with weighted average
            if item.current_stock > 0:
                total_value = (item.current_stock - movement.quantity) * item.unit_cost + movement.quantity * movement.unit_cost
                item.unit_cost = total_value / item.current_stock
        else:  # OUT movement
            item.current_stock -= movement.quantity
        
        item.save(update_fields=['current_stock', 'unit_cost', 'updated_at'])
        
        return movement


class InventoryReportSerializer(serializers.Serializer):
    """Serializer for inventory reports"""
    total_items = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    category_breakdown = serializers.ListField()
    recent_movements = serializers.ListField()


class LowStockAlertSerializer(serializers.Serializer):
    """Serializer for low stock alerts"""
    item_id = serializers.IntegerField()
    item_name = serializers.CharField()
    sku = serializers.CharField()
    current_stock = serializers.IntegerField()
    minimum_stock = serializers.IntegerField()
    category = serializers.CharField()
    supplier = serializers.CharField()
    stock_status = serializers.CharField()
    days_since_last_restock = serializers.IntegerField()


class StockValuationSerializer(serializers.Serializer):
    """Serializer for stock valuation"""
    item_id = serializers.IntegerField()
    item_name = serializers.CharField()
    sku = serializers.CharField()
    category = serializers.CharField()
    current_stock = serializers.IntegerField()
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage_of_total = serializers.FloatField()


class SupplierPerformanceSerializer(serializers.Serializer):
    """Serializer for supplier performance metrics"""
    supplier_id = serializers.IntegerField()
    supplier_name = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_items_supplied = serializers.IntegerField()
    total_value_supplied = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    last_order_date = serializers.DateTimeField()
    payment_terms = serializers.CharField()