from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, F
from django.urls import reverse
from .models import InventoryCategory, InventoryItem, StockMovement


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    fields = ('movement_type', 'quantity', 'reason', 'unit_cost', 'notes', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'inventory_items_count', 'total_stock', 'total_value', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'inventory_items_count', 'total_stock', 'total_value')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Inventory Summary', {
            'fields': ('inventory_items_count', 'total_stock', 'total_value'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_categories', 'deactivate_categories']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _inventory_items_count=Count('inventoryitem', distinct=True),
            _total_stock=Sum('inventoryitem__current_stock'),
            _total_value=Sum(F('inventoryitem__current_stock') * F('inventoryitem__unit_cost'))
        )
        return queryset
    
    def inventory_items_count(self, obj):
        count = getattr(obj, '_inventory_items_count', 0)
        if count > 0:
            try:
                url = reverse('admin:inventory_inventoryitem_changelist')
                return format_html(
                    '<a href="{}?category={}">{} items</a>',
                    str(url),
                    obj.id,
                    count
                )
            except (ValueError, TypeError, AttributeError):
                return f'{count} items'
        return '0 items'
    inventory_items_count.admin_order_field = '_inventory_items_count'
    inventory_items_count.short_description = 'Inventory Items'
    
    def total_stock(self, obj):
        stock = getattr(obj, '_total_stock', 0) or 0
        if stock > 0:
            try:
                return format_html('<strong>{}</strong>', int(stock))
            except (ValueError, TypeError):
                return str(stock)
        return '0'
    total_stock.admin_order_field = '_total_stock'
    total_stock.short_description = 'Total Stock'
    
    def total_value(self, obj):
        value = getattr(obj, '_total_value', None)
        if value is not None and value > 0:
            try:
                return format_html('<strong>${:,.2f}</strong>', float(value))
            except (ValueError, TypeError):
                return '$0.00'
        return '$0.00'
    total_value.admin_order_field = '_total_value'
    total_value.short_description = 'Total Value'
    
    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Activated {updated} categories.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {updated} categories.')
    deactivate_categories.short_description = 'Deactivate selected categories'


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_link', 'location', 'current_stock', 'stock_status', 'unit_cost', 'total_value', 'movements_count')
    list_filter = ('category', 'unit', 'location', 'minimum_stock', 'maximum_stock')
    search_fields = ('name', 'sku', 'location', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'stock_status', 'total_value', 'movements_count', 'last_movement')
    
    fieldsets = (
        ('Item Information', {
            'fields': ('name', 'category', 'sku', 'unit', 'location', 'supplier')
        }),
        ('Stock Levels', {
            'fields': ('current_stock', 'minimum_stock', 'maximum_stock', 'stock_status')
        }),
        ('Pricing', {
            'fields': ('unit_cost', 'total_value')
        }),
        ('Tracking', {
            'fields': ('movements_count', 'last_movement')
        }),
        ('Additional Info', {
            'fields': ('expiry_date', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [StockMovementInline]
    actions = ['restock_items', 'mark_low_stock', 'update_costs']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').annotate(
            _movements_count=Count('movements', distinct=True)
        )
    
    def category_link(self, obj):
        try:
            url = reverse('admin:inventory_inventorycategory_change', args=[obj.category.id])
            return format_html(
                '<a href="{}">{}</a>',
                str(url),
                str(obj.category.name)
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.category.name) if obj.category else 'No Category'
    category_link.short_description = 'Category'
    category_link.admin_order_field = 'category__name'
    
    def stock_status(self, obj):
        try:
            if obj.current_stock <= obj.minimum_stock:
                return format_html('<span style="color: red; font-weight: bold;">🔴 Low Stock</span>')
            elif obj.maximum_stock and obj.current_stock >= obj.maximum_stock:
                return format_html('<span style="color: orange; font-weight: bold;">🟡 Overstock</span>')
            else:
                return format_html('<span style="color: green; font-weight: bold;">🟢 Normal</span>')
        except (ValueError, TypeError, AttributeError):
            if obj.current_stock <= obj.minimum_stock:
                return '🔴 Low Stock'
            elif obj.maximum_stock and obj.current_stock >= obj.maximum_stock:
                return '🟡 Overstock'
            else:
                return '🟢 Normal'
    stock_status.short_description = 'Status'
    
    def total_value(self, obj):
        try:
            value = obj.current_stock * obj.unit_cost
            return format_html('<strong>${:,.2f}</strong>', float(value))
        except (ValueError, TypeError, AttributeError):
            return '$0.00'
    total_value.short_description = 'Total Value'
    
    def movements_count(self, obj):
        count = getattr(obj, '_movements_count', 0)
        if count > 0:
            try:
                url = reverse('admin:inventory_stockmovement_changelist')
                return format_html(
                    '<a href="{}?item={}">{} movements</a>',
                    str(url),
                    obj.id,
                    count
                )
            except (ValueError, TypeError, AttributeError):
                return f'{count} movements'
        return '0 movements'
    movements_count.admin_order_field = '_movements_count'
    movements_count.short_description = 'Movements'
    
    def last_movement(self, obj):
        last_movement = obj.movements.first()
        if last_movement:
            try:
                url = reverse('admin:inventory_stockmovement_change', args=[last_movement.id])
                movement_type = last_movement.get_movement_type_display()
                date_str = last_movement.created_at.strftime('%Y-%m-%d')
                return format_html(
                    '<a href="{}">{} ({})</a>',
                    str(url),
                    str(movement_type),
                    str(date_str)
                )
            except (ValueError, TypeError, AttributeError):
                return f'{last_movement.get_movement_type_display()} ({last_movement.created_at.strftime("%Y-%m-%d")})'
        return 'No movements'
    last_movement.short_description = 'Last Movement'
    
    def restock_items(self, request, queryset):
        # This would typically integrate with a restocking system
        low_stock_items = queryset.filter(current_stock__lte=F('minimum_stock'))
        self.message_user(request, f'Found {low_stock_items.count()} items that need restocking.')
    restock_items.short_description = 'Check items for restocking'
    
    def mark_low_stock(self, request, queryset):
        low_stock_count = queryset.filter(current_stock__lte=F('minimum_stock')).count()
        self.message_user(request, f'{low_stock_count} items are currently low on stock.')
    mark_low_stock.short_description = 'Identify low stock items'
    
    def update_costs(self, request, queryset):
        # Placeholder for cost update functionality
        self.message_user(request, f'Cost update functionality can be implemented here for {queryset.count()} items.')
    update_costs.short_description = 'Update unit costs'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('inventory_item_link', 'movement_type_badge', 'quantity', 'reason', 'unit_cost', 'total_cost', 'performed_by', 'created_at')
    list_filter = ('movement_type', 'reason', 'created_at', 'item__location', 'item__category')
    search_fields = ('item__name', 'item__location', 'performed_by', 'notes')
    readonly_fields = ('created_at', 'total_cost', 'inventory_item_link')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('item', 'movement_type', 'quantity', 'reason', 'unit_cost', 'total_cost')
        }),
        ('Processing', {
            'fields': ('performed_by', 'reference_number', 'notes')
        }),
        ('References', {
            'fields': ('inventory_item_link',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('item', 'item__category')
    
    def inventory_item_link(self, obj):
        try:
            url = reverse('admin:inventory_inventoryitem_change', args=[obj.item.id])
            location = obj.item.location or 'No location'
            return format_html(
                '<a href="{}">{} - {}</a>',
                str(url),
                str(obj.item.name),
                str(location)
            )
        except (ValueError, TypeError, AttributeError):
            return f'{obj.item.name} - {obj.item.location or "No location"}' if obj.item else 'Unknown Item'
    inventory_item_link.short_description = 'Inventory Item'
    
    def movement_type_badge(self, obj):
        colors = {
            'IN': 'green',
            'OUT': 'red',
            'TRANSFER': 'blue',
            'ADJUSTMENT': 'orange',
            'DAMAGED': 'darkred'
        }
        color = colors.get(obj.movement_type, 'gray')
        icons = {
            'IN': '➕',
            'OUT': '➖',
            'TRANSFER': '🔄',
            'ADJUSTMENT': '⚖️',
            'DAMAGED': '❌'
        }
        icon = icons.get(obj.movement_type, '📦')
        
        try:
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {}</span>',
                str(color),
                str(icon),
                str(obj.get_movement_type_display())
            )
        except (ValueError, TypeError, AttributeError):
            return f'{icon} {obj.get_movement_type_display()}'
    movement_type_badge.short_description = 'Movement Type'
    movement_type_badge.admin_order_field = 'movement_type'
    
    def total_cost(self, obj):
        if obj.unit_cost and obj.quantity:
            try:
                total = obj.unit_cost * obj.quantity
                return format_html('<strong>${:,.2f}</strong>', float(total))
            except (ValueError, TypeError):
                return '—'
        return '—'
    total_cost.short_description = 'Total Cost'
