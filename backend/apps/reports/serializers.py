from rest_framework import serializers


class OccupancyReportSerializer(serializers.Serializer):
    """Serializer for occupancy reports"""
    date = serializers.DateField()
    total_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    out_of_order_rooms = serializers.IntegerField()
    maintenance_rooms = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    room_type_breakdown = serializers.ListField()


class RevenueReportSerializer(serializers.Serializer):
    """Serializer for revenue reports"""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    room_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    additional_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    service_charge = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_daily_rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue_per_available_room = serializers.DecimalField(max_digits=10, decimal_places=2)
    daily_breakdown = serializers.ListField()


class BookingAnalyticsSerializer(serializers.Serializer):
    """Serializer for booking analytics"""
    period = serializers.CharField()
    total_reservations = serializers.IntegerField()
    confirmed_reservations = serializers.IntegerField()
    cancelled_reservations = serializers.IntegerField()
    checked_in_reservations = serializers.IntegerField()
    checked_out_reservations = serializers.IntegerField()
    no_show_reservations = serializers.IntegerField()
    booking_source_breakdown = serializers.ListField()
    lead_time_analysis = serializers.DictField()
    cancellation_rate = serializers.FloatField()
    show_rate = serializers.FloatField()


class GuestAnalyticsSerializer(serializers.Serializer):
    """Serializer for guest analytics"""
    total_guests = serializers.IntegerField()
    new_guests = serializers.IntegerField()
    returning_guests = serializers.IntegerField()
    vip_guests = serializers.IntegerField()
    guest_nationality_breakdown = serializers.ListField()
    loyalty_program_stats = serializers.DictField()
    average_stay_duration = serializers.FloatField()
    guest_satisfaction_metrics = serializers.DictField()


class FinancialSummarySerializer(serializers.Serializer):
    """Serializer for financial summary reports"""
    period = serializers.CharField()
    gross_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_discounts = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_taxes = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_service_charges = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_payments = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method_breakdown = serializers.ListField()
    cost_breakdown = serializers.DictField()
    profit_margins = serializers.DictField()


class OperationalReportSerializer(serializers.Serializer):
    """Serializer for operational reports"""
    report_date = serializers.DateField()
    occupancy_metrics = serializers.DictField()
    staff_metrics = serializers.DictField()
    maintenance_metrics = serializers.DictField()
    inventory_alerts = serializers.ListField()
    room_status_summary = serializers.DictField()
    key_performance_indicators = serializers.DictField()


class InventoryReportSerializer(serializers.Serializer):
    """Serializer for inventory reports"""
    report_date = serializers.DateField()
    total_items = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    category_breakdown = serializers.ListField()
    top_value_items = serializers.ListField()
    movement_summary = serializers.DictField()


class StaffReportSerializer(serializers.Serializer):
    """Serializer for staff reports"""
    report_period = serializers.CharField()
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    department_breakdown = serializers.ListField()
    attendance_summary = serializers.DictField()
    overtime_summary = serializers.DictField()
    performance_metrics = serializers.DictField()
    payroll_summary = serializers.DictField()


class CompetitorAnalysisSerializer(serializers.Serializer):
    """Serializer for competitor analysis (placeholder for future integration)"""
    analysis_date = serializers.DateField()
    market_position = serializers.CharField()
    pricing_comparison = serializers.DictField()
    occupancy_comparison = serializers.DictField()
    service_comparison = serializers.DictField()
    recommendations = serializers.ListField()


class ForecastReportSerializer(serializers.Serializer):
    """Serializer for forecasting reports"""
    forecast_period = serializers.CharField()
    occupancy_forecast = serializers.ListField()
    revenue_forecast = serializers.ListField()
    demand_patterns = serializers.DictField()
    seasonal_trends = serializers.DictField()
    booking_pace = serializers.DictField()
    recommendations = serializers.ListField()


class CustomReportSerializer(serializers.Serializer):
    """Serializer for custom reports"""
    report_name = serializers.CharField()
    report_type = serializers.CharField()
    parameters = serializers.DictField()
    generated_at = serializers.DateTimeField()
    data = serializers.DictField()
    summary = serializers.DictField()
    charts = serializers.ListField()


class ExportRequestSerializer(serializers.Serializer):
    """Serializer for export requests"""
    report_type = serializers.ChoiceField(choices=[
        'occupancy', 'revenue', 'booking_analytics', 'guest_analytics',
        'financial_summary', 'operational', 'inventory', 'staff'
    ])
    format = serializers.ChoiceField(choices=['pdf', 'excel', 'csv'], default='pdf')
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    filters = serializers.DictField(required=False, default=dict)
    email_recipients = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        help_text="Email addresses to send the report to"
    )
    
    def validate(self, data):
        """Validate export request data"""
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("End date must be after start date")
        
        # Validate date range (max 1 year)
        from datetime import timedelta
        max_range = timedelta(days=365)
        if data['end_date'] - data['start_date'] > max_range:
            raise serializers.ValidationError("Date range cannot exceed 1 year")
        
        return data


class ReportScheduleSerializer(serializers.Serializer):
    """Serializer for scheduled reports"""
    report_name = serializers.CharField(max_length=200)
    report_type = serializers.ChoiceField(choices=[
        'daily_occupancy', 'weekly_revenue', 'monthly_financial',
        'quarterly_performance', 'inventory_alerts'
    ])
    schedule_type = serializers.ChoiceField(choices=['daily', 'weekly', 'monthly', 'quarterly'])
    recipients = serializers.ListField(child=serializers.EmailField())
    format = serializers.ChoiceField(choices=['pdf', 'excel'], default='pdf')
    is_active = serializers.BooleanField(default=True)
    parameters = serializers.DictField(required=False, default=dict)


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics"""
    date = serializers.DateField()
    occupancy_rate = serializers.FloatField()
    adr = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Average Daily Rate")
    revpar = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Revenue Per Available Room")
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    guest_satisfaction = serializers.FloatField()
    staff_attendance = serializers.FloatField()
    inventory_alerts = serializers.IntegerField()
    pending_payments = serializers.DecimalField(max_digits=10, decimal_places=2)
    room_status = serializers.DictField()


class TrendAnalysisSerializer(serializers.Serializer):
    """Serializer for trend analysis"""
    metric_name = serializers.CharField()
    period = serializers.CharField()
    data_points = serializers.ListField()
    trend_direction = serializers.ChoiceField(choices=['up', 'down', 'stable'])
    trend_percentage = serializers.FloatField()
    seasonality_detected = serializers.BooleanField()
    forecast_next_period = serializers.FloatField()
    insights = serializers.ListField()


class KPIReportSerializer(serializers.Serializer):
    """Serializer for Key Performance Indicators report"""
    period = serializers.CharField()
    occupancy_kpis = serializers.DictField()
    revenue_kpis = serializers.DictField()
    guest_kpis = serializers.DictField()
    operational_kpis = serializers.DictField()
    financial_kpis = serializers.DictField()
    benchmarks = serializers.DictField()
    performance_score = serializers.FloatField()
    improvement_areas = serializers.ListField()