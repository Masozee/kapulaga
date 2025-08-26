from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from datetime import date
import re


class Guest(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    preferences = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_vip = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        super().clean()
        if self.phone:
            # Basic phone validation
            phone_pattern = r'^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
            if not re.match(phone_pattern, self.phone.replace(' ', '').replace('-', '')):
                raise ValidationError('Invalid phone number format')

    def add_loyalty_points(self, points):
        """Add loyalty points to guest account"""
        self.loyalty_points += points
        self.save(update_fields=['loyalty_points', 'updated_at'])

    def deduct_loyalty_points(self, points):
        """Deduct loyalty points from guest account"""
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            self.save(update_fields=['loyalty_points', 'updated_at'])
            return True
        return False

    @property
    def age(self):
        """Calculate guest age from date of birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None


class GuestDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('KTP', 'KTP (Indonesian ID)'),
        ('PASSPORT', 'Passport'),
        ('DRIVER_LICENSE', 'Driver License'),
        ('OTHER', 'Other'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_number = models.CharField(max_length=50)
    issuing_country = models.CharField(max_length=100, default='Indonesia')
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['document_type']
        unique_together = ['guest', 'document_type']
        verbose_name = 'Guest Document'
        verbose_name_plural = 'Guest Documents'

    def __str__(self):
        return f"{self.guest.full_name} - {self.document_type}: {self.document_number}"

    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False
