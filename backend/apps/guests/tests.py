from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date
from .models import Guest, GuestDocument


class GuestModelTest(TestCase):
    def test_create_guest_with_valid_data(self):
        """Test creating a guest with valid data"""
        guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+628123456789',
            date_of_birth=date(1990, 1, 1),
            nationality='Indonesian',
            address='Jl. Example 123, Jakarta'
        )
        self.assertEqual(guest.first_name, 'John')
        self.assertEqual(guest.last_name, 'Doe')
        self.assertEqual(guest.email, 'john.doe@example.com')
        self.assertEqual(guest.phone, '+628123456789')
        self.assertEqual(guest.nationality, 'Indonesian')
        self.assertTrue(guest.is_active)
        self.assertEqual(guest.loyalty_points, 0)

    def test_guest_full_name_property(self):
        """Test guest full name property"""
        guest = Guest(first_name='John', last_name='Doe')
        self.assertEqual(guest.full_name, 'John Doe')

    def test_guest_email_is_unique(self):
        """Test that guest email must be unique"""
        Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com'
        )
        with self.assertRaises(ValidationError):
            guest = Guest(
                first_name='Jane',
                last_name='Smith',
                email='john.doe@example.com'
            )
            guest.full_clean()

    def test_guest_phone_validation(self):
        """Test phone number validation"""
        valid_phones = ['+628123456789', '+62-21-123-4567', '08123456789']
        for phone in valid_phones:
            guest = Guest(
                first_name='John',
                last_name='Doe',
                email=f'john{phone}@example.com',
                phone=phone
            )
            # Should not raise ValidationError
            guest.full_clean()

    def test_guest_str_representation(self):
        """Test string representation of guest"""
        guest = Guest(first_name='John', last_name='Doe')
        self.assertEqual(str(guest), 'John Doe')

    def test_guest_add_loyalty_points(self):
        """Test adding loyalty points to guest"""
        guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        guest.add_loyalty_points(100)
        self.assertEqual(guest.loyalty_points, 100)
        
        guest.add_loyalty_points(50)
        self.assertEqual(guest.loyalty_points, 150)

    def test_guest_deduct_loyalty_points(self):
        """Test deducting loyalty points from guest"""
        guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            loyalty_points=100
        )
        result = guest.deduct_loyalty_points(50)
        self.assertTrue(result)
        self.assertEqual(guest.loyalty_points, 50)

        # Test insufficient points
        result = guest.deduct_loyalty_points(100)
        self.assertFalse(result)
        self.assertEqual(guest.loyalty_points, 50)

    def test_guest_preferences_json_field(self):
        """Test guest preferences JSON field"""
        preferences = {
            'room_type': 'non-smoking',
            'floor': 'high',
            'bed_type': 'king'
        }
        guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            preferences=preferences
        )
        self.assertEqual(guest.preferences['room_type'], 'non-smoking')
        self.assertEqual(guest.preferences['floor'], 'high')


class GuestDocumentModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )

    def test_create_guest_document(self):
        """Test creating a guest document"""
        document = GuestDocument.objects.create(
            guest=self.guest,
            document_type='KTP',
            document_number='1234567890123456',
            issuing_country='Indonesia',
            expiry_date=date(2030, 12, 31)
        )
        self.assertEqual(document.guest, self.guest)
        self.assertEqual(document.document_type, 'KTP')
        self.assertEqual(document.document_number, '1234567890123456')
        self.assertEqual(document.issuing_country, 'Indonesia')
        self.assertTrue(document.is_verified)

    def test_document_type_choices(self):
        """Test document type choices validation"""
        valid_types = ['KTP', 'PASSPORT', 'DRIVER_LICENSE', 'OTHER']
        
        for doc_type in valid_types:
            document = GuestDocument(
                guest=self.guest,
                document_type=doc_type,
                document_number=f'DOC{doc_type}123'
            )
            # Should not raise ValidationError
            document.full_clean()

        # Test invalid type
        with self.assertRaises(ValidationError):
            document = GuestDocument(
                guest=self.guest,
                document_type='INVALID_TYPE',
                document_number='123456789'
            )
            document.full_clean()

    def test_document_str_representation(self):
        """Test string representation of document"""
        document = GuestDocument(
            guest=self.guest,
            document_type='KTP',
            document_number='1234567890123456'
        )
        self.assertEqual(str(document), 'John Doe - KTP: 1234567890123456')

    def test_document_is_expired_method(self):
        """Test document expiry check"""
        # Document with future expiry
        future_document = GuestDocument.objects.create(
            guest=self.guest,
            document_type='PASSPORT',
            document_number='P123456789',
            expiry_date=date(2030, 12, 31)
        )
        self.assertFalse(future_document.is_expired())

        # Document with past expiry
        past_document = GuestDocument.objects.create(
            guest=self.guest,
            document_type='KTP',
            document_number='K123456789',
            expiry_date=date(2020, 1, 1)
        )
        self.assertTrue(past_document.is_expired())
