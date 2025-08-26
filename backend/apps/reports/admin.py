from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Sum, Count
from django.urls import reverse
from datetime import date, timedelta
from .models import DailyReport, MonthlyReport, OccupancyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'occupancy_rate_badge', 'total_rooms', 'occupied_rooms', 'available_rooms', 'total_revenue', 'adr', 'revpar', 'total_guests')
    list_filter = ('report_date', 'total_rooms', 'created_at')
    search_fields = ('report_date',)
    readonly_fields = ('created_at', 'updated_at', 'occupancy_rate_badge', 'adr', 'revpar', 'revenue_breakdown')
    date_hierarchy = 'report_date'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_date', 'occupancy_rate_badge')
        }),
        ('Room Statistics', {
            'fields': ('total_rooms', 'occupied_rooms', 'available_rooms', 'maintenance_rooms', 'out_of_order_rooms')
        }),
        ('Revenue Data', {
            'fields': ('total_revenue', 'room_revenue', 'food_beverage_revenue', 'other_revenue', 'revenue_breakdown')
        }),
        ('Guest Data', {
            'fields': ('total_guests', 'walk_in_guests', 'online_bookings')
        }),
        ('Key Performance Indicators', {
            'fields': ('adr', 'revpar', 'average_daily_rate', 'revenue_per_available_room'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generate_summary_report', 'compare_with_previous_month']
    
    def occupancy_rate_badge(self, obj):
        try:
            rate = obj.occupancy_rate
            if rate >= 90:
                color = 'green'
                status = 'Excellent'
            elif rate >= 75:
                color = 'blue'
                status = 'Good'
            elif rate >= 60:
                color = 'orange'
                status = 'Fair'
            else:
                color = 'red'
                status = 'Poor'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}% ({})</span>',
                str(color), float(rate), str(status)
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.occupancy_rate) if hasattr(obj, 'occupancy_rate') else 'N/A'
    occupancy_rate_badge.short_description = 'Occupancy Rate'
    occupancy_rate_badge.admin_order_field = 'occupied_rooms'
    
    def adr(self, obj):
        try:
            return format_html('<strong>${:,.2f}</strong>', float(obj.adr))
        except (ValueError, TypeError, AttributeError):
            return '$0.00'
    adr.short_description = 'ADR'
    
    def revpar(self, obj):
        try:
            return format_html('<strong>${:,.2f}</strong>', float(obj.revpar))
        except (ValueError, TypeError, AttributeError):
            return '$0.00'
    revpar.short_description = 'RevPAR'
    
    def revenue_breakdown(self, obj):
        try:
            total = obj.total_revenue
            if total > 0:
                room_pct = (obj.room_revenue / total) * 100
                fb_pct = (obj.food_beverage_revenue / total) * 100
                other_pct = (obj.other_revenue / total) * 100
                
                return format_html(
                    'Room: {:.1f}% | F&B: {:.1f}% | Other: {:.1f}%',
                    float(room_pct), float(fb_pct), float(other_pct)
                )
            return 'No revenue'
        except (ValueError, TypeError, AttributeError, ZeroDivisionError):
            return 'No revenue'
    revenue_breakdown.short_description = 'Revenue Breakdown'
    
    def generate_summary_report(self, request, queryset):
        total_revenue = sum(report.total_revenue for report in queryset)
        avg_occupancy = sum(report.occupancy_rate for report in queryset) / queryset.count()
        self.message_user(
            request, 
            f'Summary: {queryset.count()} reports, Total Revenue: ${total_revenue:,.2f}, Avg Occupancy: {avg_occupancy:.1f}%'
        )
    generate_summary_report.short_description = 'Generate summary for selected reports'
    
    def compare_with_previous_month(self, request, queryset):
        # Placeholder for comparison functionality
        self.message_user(request, f'Comparison functionality can be implemented for {queryset.count()} reports.')
    compare_with_previous_month.short_description = 'Compare with previous month'


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('month_year', 'total_revenue', 'total_expenses', 'net_profit_badge', 'profit_margin_badge', 'average_occupancy_rate', 'average_daily_rate', 'total_guests')
    list_filter = ('year', 'month', 'created_at')
    search_fields = ('year', 'month')
    readonly_fields = ('created_at', 'updated_at', 'net_profit_badge', 'profit_margin_badge', 'revenue_breakdown', 'expense_breakdown')
    
    fieldsets = (
        ('Report Period', {
            'fields': ('year', 'month')
        }),
        ('Revenue Summary', {
            'fields': ('total_revenue', 'room_revenue', 'food_beverage_revenue', 'other_revenue', 'revenue_breakdown')
        }),
        ('Expense Summary', {
            'fields': ('total_expenses', 'staff_costs', 'utilities_costs', 'maintenance_costs', 'marketing_costs', 'other_expenses', 'expense_breakdown')
        }),
        ('Financial Performance', {
            'fields': ('net_profit_badge', 'profit_margin_badge')
        }),
        ('Operational Data', {
            'fields': ('average_occupancy_rate', 'average_daily_rate', 'total_guests', 'total_room_nights')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['calculate_yearly_summary', 'export_financial_report']
    
    def month_year(self, obj):
        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return f"{month_names[obj.month]} {obj.year}"
    month_year.short_description = 'Period'
    month_year.admin_order_field = 'year'
    
    def net_profit_badge(self, obj):
        try:
            profit = obj.net_profit
            if profit > 0:
                return format_html('<strong style="color: green;">${:,.2f}</strong>', float(profit))
            else:
                return format_html('<strong style="color: red;">-${:,.2f}</strong>', float(abs(profit)))
        except (ValueError, TypeError, AttributeError):
            return '$0.00'
    net_profit_badge.short_description = 'Net Profit'
    
    def profit_margin_badge(self, obj):
        try:
            margin = obj.profit_margin
            if margin >= 20:
                color = 'green'
            elif margin >= 10:
                color = 'blue'
            elif margin >= 0:
                color = 'orange'
            else:
                color = 'red'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
                str(color), float(margin)
            )
        except (ValueError, TypeError, AttributeError):
            return '0.00%'
    profit_margin_badge.short_description = 'Profit Margin'
    
    def revenue_breakdown(self, obj):
        try:
            total = obj.total_revenue
            if total > 0:
                room_pct = (obj.room_revenue / total) * 100
                fb_pct = (obj.food_beverage_revenue / total) * 100
                other_pct = (obj.other_revenue / total) * 100
                
                return format_html(
                    'Room: {:.1f}% | F&B: {:.1f}% | Other: {:.1f}%',
                    float(room_pct), float(fb_pct), float(other_pct)
                )
            return 'No revenue'
        except (ValueError, TypeError, AttributeError, ZeroDivisionError):
            return 'No revenue'
    revenue_breakdown.short_description = 'Revenue Mix'
    
    def expense_breakdown(self, obj):
        try:
            total = obj.total_expenses
            if total > 0:
                staff_pct = (obj.staff_costs / total) * 100
                utilities_pct = (obj.utilities_costs / total) * 100
                maintenance_pct = (obj.maintenance_costs / total) * 100
                marketing_pct = (obj.marketing_costs / total) * 100
                other_pct = (obj.other_expenses / total) * 100
                
                return format_html(
                    'Staff: {:.1f}% | Utilities: {:.1f}% | Maintenance: {:.1f}% | Marketing: {:.1f}% | Other: {:.1f}%',
                    float(staff_pct), float(utilities_pct), float(maintenance_pct), float(marketing_pct), float(other_pct)
                )
            return 'No expenses'
        except (ValueError, TypeError, AttributeError, ZeroDivisionError):
            return 'No expenses'
    expense_breakdown.short_description = 'Expense Mix'
    
    def calculate_yearly_summary(self, request, queryset):
        total_revenue = sum(report.total_revenue for report in queryset)
        total_expenses = sum(report.total_expenses for report in queryset)
        net_profit = total_revenue - total_expenses
        self.message_user(
            request,
            f'Yearly Summary: Revenue: ${total_revenue:,.2f}, Expenses: ${total_expenses:,.2f}, Profit: ${net_profit:,.2f}'
        )
    calculate_yearly_summary.short_description = 'Calculate yearly summary'
    
    def export_financial_report(self, request, queryset):
        self.message_user(request, f'Financial report export functionality for {queryset.count()} reports.')
    export_financial_report.short_description = 'Export financial reports'


@admin.register(OccupancyReport)
class OccupancyReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'room_type_display', 'occupancy_rate_badge', 'total_rooms', 'occupied_rooms', 'room_revenue', 'average_rate')
    list_filter = ('report_date', 'room_type', 'occupancy_rate', 'created_at')
    search_fields = ('room_type', 'report_date')
    readonly_fields = ('created_at', 'occupancy_rate_badge')
    date_hierarchy = 'report_date'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_date', 'room_type', 'occupancy_rate_badge')
        }),
        ('Occupancy Data', {
            'fields': ('total_rooms', 'occupied_rooms', 'available_rooms', 'occupancy_rate')
        }),
        ('Revenue Data', {
            'fields': ('room_revenue', 'average_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['analyze_room_type_performance', 'generate_occupancy_trends']
    
    def room_type_display(self, obj):
        if obj.room_type:
            return obj.room_type
        return format_html('<em>All Room Types</em>')
    room_type_display.short_description = 'Room Type'
    room_type_display.admin_order_field = 'room_type'
    
    def occupancy_rate_badge(self, obj):
        try:
            rate = float(obj.occupancy_rate)
            if rate >= 90:
                color = 'green'
                status = 'Excellent'
            elif rate >= 75:
                color = 'blue'
                status = 'Good'
            elif rate >= 60:
                color = 'orange'
                status = 'Fair'
            else:
                color = 'red'
                status = 'Poor'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}% ({})</span>',
                str(color), float(rate), str(status)
            )
        except (ValueError, TypeError, AttributeError):
            return str(obj.occupancy_rate) if hasattr(obj, 'occupancy_rate') else 'N/A'
    occupancy_rate_badge.short_description = 'Occupancy Rate'
    occupancy_rate_badge.admin_order_field = 'occupancy_rate'
    
    def analyze_room_type_performance(self, request, queryset):
        if queryset.exists():
            avg_occupancy = queryset.aggregate(avg_occ=Avg('occupancy_rate'))['avg_occ']
            total_revenue = queryset.aggregate(total_rev=Sum('room_revenue'))['total_rev']
            self.message_user(
                request,
                f'Analysis: Avg Occupancy: {avg_occupancy:.1f}%, Total Revenue: ${total_revenue:,.2f}'
            )
    analyze_room_type_performance.short_description = 'Analyze room type performance'
    
    def generate_occupancy_trends(self, request, queryset):
        self.message_user(request, f'Occupancy trends analysis for {queryset.count()} reports.')
    generate_occupancy_trends.short_description = 'Generate occupancy trends'
