from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Inventory Category'
        verbose_name_plural = 'Inventory Categories'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('set', 'Set'),
        ('kg', 'Kilogram'),
        ('liter', 'Liter'),
        ('bottle', 'Bottle'),
        ('roll', 'Roll'),
        ('pack', 'Pack'),
        ('box', 'Box'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=0)
    maximum_stock = models.PositiveIntegerField(null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'

    def __str__(self):
        return self.name

    def is_low_stock(self):
        """Check if item is low on stock"""
        return self.current_stock <= self.minimum_stock

    def stock_value(self):
        """Calculate total stock value"""
        return self.current_stock * self.unit_cost

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

    def generate_sku(self):
        """Generate SKU automatically"""
        prefix = self.category.name[:3].upper() if self.category else 'INV'
        count = InventoryItem.objects.count() + 1
        return f"{prefix}-{count:04d}"


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('TRANSFER', 'Transfer'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    REASON_CHOICES = [
        ('Purchase', 'Purchase'),
        ('Room Usage', 'Room Usage'),
        ('Housekeeping', 'Housekeeping'),
        ('Damage', 'Damage/Loss'),
        ('Return', 'Return'),
        ('Inventory Count', 'Inventory Count'),
        ('Transfer', 'Transfer'),
        ('Other', 'Other'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'

    def __str__(self):
        return f"{self.item.name} - {self.movement_type}: {self.quantity}"

    def clean(self):
        super().clean()
        if self.movement_type == 'OUT' and self.quantity > self.item.current_stock:
            raise ValidationError(f'Cannot remove {self.quantity} items. Only {self.item.current_stock} available.')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.update_item_stock()

    def update_item_stock(self):
        """Update item stock based on movement"""
        if self.movement_type == 'IN':
            self.item.current_stock += self.quantity
        elif self.movement_type == 'OUT':
            self.item.current_stock = max(0, self.item.current_stock - self.quantity)
        elif self.movement_type == 'ADJUSTMENT':
            # For adjustments, quantity represents the new stock level
            self.item.current_stock = self.quantity
        
        self.item.save(update_fields=['current_stock', 'updated_at'])
