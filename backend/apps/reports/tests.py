from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta
from apps.guests.models import Guest
from apps.rooms.models import RoomType, Room
from apps.reservations.models import Reservation, ReservationRoom
from apps.payments.models import Bill, Payment, PaymentMethod
from .models import DailyReport, MonthlyReport


class DailyReportModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            first_name='Test',
            last_name='Guest',
            email='test@example.com'
        )
        self.room_type = RoomType.objects.create(
            name='Standard',
            base_price=Decimal('100.00'),
            max_occupancy=2
        )
        self.room = Room.objects.create(
            number='101',
            room_type=self.room_type
        )

    def test_create_daily_report(self):
        """Test creating daily report"""
        report = DailyReport.objects.create(
            report_date=date.today(),
            total_rooms=50,
            occupied_rooms=30,
            available_rooms=20,
            total_revenue=Decimal('5000.00'),
            room_revenue=Decimal('4500.00'),
            other_revenue=Decimal('500.00')
        )
        self.assertEqual(report.report_date, date.today())
        self.assertEqual(report.occupancy_rate, 60.0)
        self.assertEqual(report.adr, Decimal('150.00'))  # 4500/30

    def test_daily_report_calculations(self):
        """Test daily report automatic calculations"""
        report = DailyReport.objects.create(
            report_date=date.today(),
            total_rooms=100,
            occupied_rooms=75,
            room_revenue=Decimal('7500.00')
        )
        self.assertEqual(report.occupancy_rate, 75.0)
        self.assertEqual(report.adr, Decimal('100.00'))

    def test_daily_report_str_representation(self):
        """Test string representation of daily report"""
        report = DailyReport(report_date=date.today())
        expected = f"Daily Report - {date.today()}"
        self.assertEqual(str(report), expected)


class MonthlyReportModelTest(TestCase):
    def test_create_monthly_report(self):
        """Test creating monthly report"""
        report = MonthlyReport.objects.create(
            year=2025,
            month=8,
            total_revenue=Decimal('150000.00'),
            room_revenue=Decimal('120000.00'),
            other_revenue=Decimal('30000.00'),
            total_expenses=Decimal('80000.00'),
            average_occupancy_rate=72.5,
            total_guests=450
        )
        self.assertEqual(report.year, 2025)
        self.assertEqual(report.month, 8)
        self.assertEqual(report.net_profit, Decimal('70000.00'))
        self.assertEqual(report.profit_margin, 46.67)

    def test_monthly_report_str_representation(self):
        """Test string representation of monthly report"""
        report = MonthlyReport(year=2025, month=8)
        expected = "Monthly Report - 2025-08"
        self.assertEqual(str(report), expected)
