from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import RoomType, Room


class RoomTypeModelTest(TestCase):
    def test_create_room_type_with_valid_data(self):
        """Test creating a room type with valid data"""
        room_type = RoomType.objects.create(
            name='Standard',
            description='Standard room with basic amenities',
            base_price=Decimal('100.00'),
            max_occupancy=2,
            size_sqm=25.5
        )
        self.assertEqual(room_type.name, 'Standard')
        self.assertEqual(room_type.base_price, Decimal('100.00'))
        self.assertEqual(room_type.max_occupancy, 2)
        self.assertEqual(room_type.size_sqm, 25.5)
        self.assertTrue(room_type.is_active)

    def test_room_type_name_is_required(self):
        """Test that room type name is required"""
        with self.assertRaises(ValidationError):
            room_type = RoomType(
                base_price=Decimal('100.00'),
                max_occupancy=2
            )
            room_type.full_clean()

    def test_room_type_base_price_positive(self):
        """Test that base price must be positive"""
        with self.assertRaises(ValidationError):
            room_type = RoomType(
                name='Standard',
                base_price=Decimal('-100.00'),
                max_occupancy=2
            )
            room_type.full_clean()

    def test_room_type_max_occupancy_positive(self):
        """Test that max occupancy must be positive"""
        with self.assertRaises(ValidationError):
            room_type = RoomType(
                name='Standard',
                base_price=Decimal('100.00'),
                max_occupancy=0
            )
            room_type.full_clean()

    def test_room_type_str_representation(self):
        """Test string representation of room type"""
        room_type = RoomType(name='Deluxe')
        self.assertEqual(str(room_type), 'Deluxe')


class RoomModelTest(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(
            name='Standard',
            base_price=Decimal('100.00'),
            max_occupancy=2
        )

    def test_create_room_with_valid_data(self):
        """Test creating a room with valid data"""
        room = Room.objects.create(
            number='101',
            room_type=self.room_type,
            floor=1,
            status='AVAILABLE'
        )
        self.assertEqual(room.number, '101')
        self.assertEqual(room.room_type, self.room_type)
        self.assertEqual(room.floor, 1)
        self.assertEqual(room.status, 'AVAILABLE')
        self.assertTrue(room.is_active)

    def test_room_number_is_required(self):
        """Test that room number is required"""
        with self.assertRaises(ValidationError):
            room = Room(
                room_type=self.room_type,
                floor=1
            )
            room.full_clean()

    def test_room_number_is_unique(self):
        """Test that room number must be unique"""
        Room.objects.create(
            number='101',
            room_type=self.room_type,
            floor=1
        )
        with self.assertRaises(ValidationError):
            room = Room(
                number='101',
                room_type=self.room_type,
                floor=2
            )
            room.full_clean()

    def test_room_status_choices(self):
        """Test room status choices validation"""
        valid_statuses = ['AVAILABLE', 'OCCUPIED', 'RESERVED', 'MAINTENANCE', 'OUT_OF_ORDER']
        
        for status in valid_statuses:
            room = Room(
                number=f'10{status[0]}',
                room_type=self.room_type,
                floor=1,
                status=status
            )
            # Should not raise ValidationError
            room.full_clean()

        # Test invalid status
        with self.assertRaises(ValidationError):
            room = Room(
                number='199',
                room_type=self.room_type,
                floor=1,
                status='INVALID_STATUS'
            )
            room.full_clean()

    def test_room_str_representation(self):
        """Test string representation of room"""
        room = Room(
            number='101',
            room_type=self.room_type
        )
        self.assertEqual(str(room), 'Room 101 - Standard')

    def test_room_is_available_method(self):
        """Test room availability check method"""
        room = Room.objects.create(
            number='101',
            room_type=self.room_type,
            floor=1,
            status='AVAILABLE'
        )
        self.assertTrue(room.is_available())

        room.status = 'OCCUPIED'
        room.save()
        self.assertFalse(room.is_available())

    def test_room_get_current_price(self):
        """Test getting current room price"""
        room = Room.objects.create(
            number='101',
            room_type=self.room_type,
            floor=1
        )
        self.assertEqual(room.get_current_price(), self.room_type.base_price)
