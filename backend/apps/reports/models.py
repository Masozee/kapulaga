from django.db import models
from decimal import Decimal


class DailyReport(models.Model):
    report_date = models.DateField(unique=True)
    total_rooms = models.PositiveIntegerField()
    occupied_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()
    maintenance_rooms = models.PositiveIntegerField(default=0)
    out_of_order_rooms = models.PositiveIntegerField(default=0)
    
    # Revenue data
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    room_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    food_beverage_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    other_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Guest data
    total_guests = models.PositiveIntegerField(default=0)
    walk_in_guests = models.PositiveIntegerField(default=0)
    online_bookings = models.PositiveIntegerField(default=0)
    
    # Financial metrics
    average_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    revenue_per_available_room = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']
        verbose_name = 'Daily Report'
        verbose_name_plural = 'Daily Reports'

    def __str__(self):
        return f"Daily Report - {self.report_date}"

    @property
    def occupancy_rate(self):
        """Calculate occupancy rate as percentage"""
        if self.total_rooms > 0:
            return round((self.occupied_rooms / self.total_rooms) * 100, 2)
        return 0.0

    @property
    def adr(self):
        """Average Daily Rate"""
        if self.occupied_rooms > 0 and self.room_revenue > 0:
            return self.room_revenue / self.occupied_rooms
        return Decimal('0.00')

    @property
    def revpar(self):
        """Revenue Per Available Room"""
        if self.total_rooms > 0:
            return self.room_revenue / self.total_rooms
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        # Auto-calculate available rooms
        if not self.available_rooms:
            self.available_rooms = max(0, self.total_rooms - self.occupied_rooms - self.maintenance_rooms - self.out_of_order_rooms)
        
        # Auto-calculate metrics
        self.average_daily_rate = self.adr
        self.revenue_per_available_room = self.revpar
        
        super().save(*args, **kwargs)


class MonthlyReport(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)])
    
    # Revenue data
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    room_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    food_beverage_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    other_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Expense data
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    staff_costs = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    utilities_costs = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    maintenance_costs = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    marketing_costs = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Operational data
    average_occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    average_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_guests = models.PositiveIntegerField(default=0)
    total_room_nights = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['year', 'month']
        verbose_name = 'Monthly Report'
        verbose_name_plural = 'Monthly Reports'

    def __str__(self):
        return f"Monthly Report - {self.year}-{self.month:02d}"

    @property
    def net_profit(self):
        """Calculate net profit"""
        return self.total_revenue - self.total_expenses

    @property
    def profit_margin(self):
        """Calculate profit margin as percentage"""
        if self.total_revenue > 0:
            return float(round((self.net_profit / self.total_revenue) * 100, 2))
        return 0.0

    @property
    def revpar(self):
        """Revenue Per Available Room for the month"""
        if self.total_room_nights > 0:
            return self.room_revenue / self.total_room_nights
        return Decimal('0.00')


class OccupancyReport(models.Model):
    """Model for tracking occupancy trends and analytics"""
    report_date = models.DateField()
    room_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Occupancy metrics
    total_rooms = models.PositiveIntegerField()
    occupied_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Revenue metrics
    room_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date', 'room_type']
        unique_together = ['report_date', 'room_type']
        verbose_name = 'Occupancy Report'
        verbose_name_plural = 'Occupancy Reports'

    def __str__(self):
        room_type_str = f" - {self.room_type}" if self.room_type else ""
        return f"Occupancy Report - {self.report_date}{room_type_str}"
