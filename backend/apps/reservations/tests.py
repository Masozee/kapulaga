from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from apps.guests.models import Guest
from apps.rooms.models import RoomType, Room
from .models import Reservation, ReservationRoom


class ReservationModelTest(TestCase):
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

    def test_create_reservation_with_valid_data(self):
        """Test creating a reservation with valid data"""
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)
        
        reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            children=0,
            total_amount=Decimal('200.00'),
            status='CONFIRMED'
        )
        self.assertEqual(reservation.guest, self.guest)
        self.assertEqual(reservation.check_in_date, check_in)
        self.assertEqual(reservation.check_out_date, check_out)
        self.assertEqual(reservation.adults, 2)
        self.assertEqual(reservation.total_amount, Decimal('200.00'))
        self.assertEqual(reservation.status, 'CONFIRMED')

    def test_reservation_nights_property(self):
        """Test reservation nights calculation"""
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=4)
        
        reservation = Reservation(
            guest=self.guest,
            check_in_date=check_in,
            check_out_date=check_out
        )
        self.assertEqual(reservation.nights, 3)

    def test_check_out_after_check_in_validation(self):
        """Test that check out date must be after check in date"""
        check_in = date.today() + timedelta(days=3)
        check_out = date.today() + timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            reservation = Reservation(
                guest=self.guest,
                check_in_date=check_in,
                check_out_date=check_out
            )
            reservation.full_clean()

    def test_reservation_status_choices(self):
        """Test reservation status choices validation"""
        valid_statuses = ['PENDING', 'CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED', 'NO_SHOW']
        
        for status in valid_statuses:
            reservation = Reservation(
                guest=self.guest,
                check_in_date=date.today() + timedelta(days=1),
                check_out_date=date.today() + timedelta(days=3),
                status=status
            )
            reservation.full_clean()

        with self.assertRaises(ValidationError):
            reservation = Reservation(
                guest=self.guest,
                check_in_date=date.today() + timedelta(days=1),
                check_out_date=date.today() + timedelta(days=3),
                status='INVALID_STATUS'
            )
            reservation.full_clean()

    def test_reservation_str_representation(self):
        """Test string representation of reservation"""
        reservation = Reservation(
            guest=self.guest,
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=3)
        )
        expected = f"John Doe - {reservation.check_in_date} to {reservation.check_out_date}"
        self.assertEqual(str(reservation), expected)

    def test_can_cancel_reservation(self):
        """Test reservation cancellation rules"""
        # Future reservation should be cancellable
        future_reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=3),
            status='CONFIRMED'
        )
        self.assertTrue(future_reservation.can_cancel())

        # Checked in reservation should not be cancellable
        future_reservation.status = 'CHECKED_IN'
        future_reservation.save()
        self.assertFalse(future_reservation.can_cancel())

    def test_calculate_total_amount(self):
        """Test total amount calculation"""
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)
        
        reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=check_in,
            check_out_date=check_out
        )
        
        ReservationRoom.objects.create(
            reservation=reservation,
            room=self.room,
            rate=Decimal('100.00')
        )
        
        total = reservation.calculate_total_amount()
        self.assertEqual(total, Decimal('200.00'))  # 2 nights * 100.00


class ReservationRoomModelTest(TestCase):
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
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=3)
        )

    def test_create_reservation_room(self):
        """Test creating a reservation room"""
        res_room = ReservationRoom.objects.create(
            reservation=self.reservation,
            room=self.room,
            rate=Decimal('100.00')
        )
        self.assertEqual(res_room.reservation, self.reservation)
        self.assertEqual(res_room.room, self.room)
        self.assertEqual(res_room.rate, Decimal('100.00'))

    def test_reservation_room_str_representation(self):
        """Test string representation of reservation room"""
        res_room = ReservationRoom(
            reservation=self.reservation,
            room=self.room,
            rate=Decimal('100.00')
        )
        expected = f"Reservation {self.reservation.id} - Room {self.room.number}"
        self.assertEqual(str(res_room), expected)

    def test_total_amount_calculation(self):
        """Test total amount calculation for reservation room"""
        res_room = ReservationRoom.objects.create(
            reservation=self.reservation,
            room=self.room,
            rate=Decimal('100.00')
        )
        self.assertEqual(res_room.total_amount, Decimal('200.00'))  # 2 nights * 100.00
