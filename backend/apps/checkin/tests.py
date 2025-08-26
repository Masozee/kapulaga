from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from apps.guests.models import Guest
from apps.rooms.models import RoomType, Room
from apps.reservations.models import Reservation, ReservationRoom
from .models import CheckIn, CheckOut, RoomKey


class CheckInModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
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
        self.reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
            status='CONFIRMED'
        )
        ReservationRoom.objects.create(
            reservation=self.reservation,
            room=self.room,
            rate=Decimal('100.00')
        )

    def test_create_checkin_with_valid_data(self):
        """Test creating a check-in with valid data"""
        checkin = CheckIn.objects.create(
            reservation=self.reservation,
            actual_check_in_time=datetime.now(),
            adults_count=2,
            children_count=0,
            deposit_paid=Decimal('50.00'),
            verified_by='Front Desk'
        )
        self.assertEqual(checkin.reservation, self.reservation)
        self.assertEqual(checkin.adults_count, 2)
        self.assertEqual(checkin.deposit_paid, Decimal('50.00'))
        self.assertEqual(checkin.verified_by, 'Front Desk')

    def test_checkin_str_representation(self):
        """Test string representation of check-in"""
        checkin = CheckIn.objects.create(
            reservation=self.reservation,
            actual_check_in_time=datetime.now()
        )
        expected = f"Check-in: John Doe - Room 101 - {date.today()}"
        self.assertEqual(str(checkin), expected)

    def test_checkin_creates_room_keys(self):
        """Test that check-in creates room keys"""
        checkin = CheckIn.objects.create(
            reservation=self.reservation,
            actual_check_in_time=datetime.now(),
            number_of_keys=2
        )
        keys = RoomKey.objects.filter(check_in=checkin)
        self.assertEqual(keys.count(), 2)
        for key in keys:
            self.assertTrue(key.is_active)

    def test_early_checkin_charge(self):
        """Test early check-in charge calculation"""
        # Check-in 4 hours before scheduled time
        early_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=10)
        checkin = CheckIn.objects.create(
            reservation=self.reservation,
            actual_check_in_time=early_time,
            early_checkin_charge=Decimal('25.00')
        )
        self.assertEqual(checkin.early_checkin_charge, Decimal('25.00'))

    def test_cannot_checkin_cancelled_reservation(self):
        """Test that cancelled reservations cannot be checked in"""
        self.reservation.status = 'CANCELLED'
        self.reservation.save()
        
        with self.assertRaises(ValidationError):
            checkin = CheckIn(
                reservation=self.reservation,
                actual_check_in_time=datetime.now()
            )
            checkin.full_clean()


class CheckOutModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )
        self.room_type = RoomType.objects.create(
            name='Deluxe',
            base_price=Decimal('150.00'),
            max_occupancy=3
        )
        self.room = Room.objects.create(
            number='201',
            room_type=self.room_type
        )
        self.reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=date.today() - timedelta(days=2),
            check_out_date=date.today(),
            status='CHECKED_IN'
        )
        ReservationRoom.objects.create(
            reservation=self.reservation,
            room=self.room,
            rate=Decimal('150.00')
        )
        self.checkin = CheckIn.objects.create(
            reservation=self.reservation,
            actual_check_in_time=datetime.now() - timedelta(days=2)
        )

    def test_create_checkout_with_valid_data(self):
        """Test creating a check-out with valid data"""
        checkout = CheckOut.objects.create(
            check_in=self.checkin,
            actual_check_out_time=datetime.now(),
            final_bill_amount=Decimal('320.00'),
            payment_status='PAID',
            room_condition='CLEAN',
            processed_by='Front Desk'
        )
        self.assertEqual(checkout.check_in, self.checkin)
        self.assertEqual(checkout.final_bill_amount, Decimal('320.00'))
        self.assertEqual(checkout.payment_status, 'PAID')
        self.assertEqual(checkout.room_condition, 'CLEAN')

    def test_checkout_str_representation(self):
        """Test string representation of check-out"""
        checkout = CheckOut.objects.create(
            check_in=self.checkin,
            actual_check_out_time=datetime.now()
        )
        expected = f"Check-out: Jane Smith - Room 201 - {date.today()}"
        self.assertEqual(str(checkout), expected)

    def test_late_checkout_charge(self):
        """Test late check-out charge"""
        late_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=16)
        checkout = CheckOut.objects.create(
            check_in=self.checkin,
            actual_check_out_time=late_time,
            late_checkout_charge=Decimal('50.00')
        )
        self.assertEqual(checkout.late_checkout_charge, Decimal('50.00'))

    def test_checkout_deactivates_room_keys(self):
        """Test that check-out deactivates room keys"""
        # Create some active keys
        key1 = RoomKey.objects.create(
            check_in=self.checkin,
            room=self.room,
            key_code='KEY001'
        )
        key2 = RoomKey.objects.create(
            check_in=self.checkin,
            room=self.room,
            key_code='KEY002'
        )
        
        checkout = CheckOut.objects.create(
            check_in=self.checkin,
            actual_check_out_time=datetime.now()
        )
        
        # Keys should be deactivated
        key1.refresh_from_db()
        key2.refresh_from_db()
        self.assertFalse(key1.is_active)
        self.assertFalse(key2.is_active)

    def test_payment_status_choices(self):
        """Test payment status choices validation"""
        valid_statuses = ['PENDING', 'PAID', 'PARTIAL', 'REFUNDED']
        
        for status in valid_statuses:
            checkout = CheckOut(
                check_in=self.checkin,
                actual_check_out_time=datetime.now(),
                payment_status=status
            )
            checkout.full_clean()

        with self.assertRaises(ValidationError):
            checkout = CheckOut(
                check_in=self.checkin,
                actual_check_out_time=datetime.now(),
                payment_status='INVALID_STATUS'
            )
            checkout.full_clean()


class RoomKeyModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            first_name='Bob',
            last_name='Johnson',
            email='bob@example.com'
        )
        self.room_type = RoomType.objects.create(
            name='Suite',
            base_price=Decimal('200.00'),
            max_occupancy=4
        )
        self.room = Room.objects.create(
            number='301',
            room_type=self.room_type
        )
        self.reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=1)
        )
        self.checkin = CheckIn.objects.create(
            reservation=self.reservation,
            actual_check_in_time=datetime.now()
        )

    def test_create_room_key(self):
        """Test creating a room key"""
        key = RoomKey.objects.create(
            check_in=self.checkin,
            room=self.room,
            key_code='RFID001',
            key_type='RFID'
        )
        self.assertEqual(key.check_in, self.checkin)
        self.assertEqual(key.room, self.room)
        self.assertEqual(key.key_code, 'RFID001')
        self.assertEqual(key.key_type, 'RFID')
        self.assertTrue(key.is_active)

    def test_room_key_str_representation(self):
        """Test string representation of room key"""
        key = RoomKey.objects.create(
            check_in=self.checkin,
            room=self.room,
            key_code='RFID001'
        )
        expected = f"Key RFID001 - Room 301 - Bob Johnson"
        self.assertEqual(str(key), expected)

    def test_key_type_choices(self):
        """Test key type choices validation"""
        valid_types = ['PHYSICAL', 'RFID', 'MAGNETIC', 'DIGITAL']
        
        for key_type in valid_types:
            key = RoomKey(
                check_in=self.checkin,
                room=self.room,
                key_code=f'KEY{key_type}',
                key_type=key_type
            )
            key.full_clean()

        with self.assertRaises(ValidationError):
            key = RoomKey(
                check_in=self.checkin,
                room=self.room,
                key_code='KEYINVALID',
                key_type='INVALID_TYPE'
            )
            key.full_clean()

    def test_deactivate_key(self):
        """Test key deactivation"""
        key = RoomKey.objects.create(
            check_in=self.checkin,
            room=self.room,
            key_code='RFID001'
        )
        self.assertTrue(key.is_active)
        
        key.deactivate()
        self.assertFalse(key.is_active)
        self.assertIsNotNone(key.deactivated_at)
