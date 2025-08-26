from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from apps.guests.models import Guest
from apps.rooms.models import Room


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    BOOKING_SOURCE_CHOICES = [
        ('DIRECT', 'Direct Booking'),
        ('ONLINE', 'Online Booking'),
        ('OTA', 'Online Travel Agent'),
        ('WALK_IN', 'Walk-in'),
        ('PHONE', 'Phone Booking'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='reservations')
    reservation_number = models.CharField(max_length=20, unique=True, blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    special_requests = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    booking_source = models.CharField(max_length=20, choices=BOOKING_SOURCE_CHOICES, default='DIRECT')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-check_in_date', '-created_at']
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

    def __str__(self):
        return f"{self.guest.full_name} - {self.check_in_date} to {self.check_out_date}"

    def clean(self):
        super().clean()
        if self.check_in_date and self.check_out_date:
            if self.check_out_date <= self.check_in_date:
                raise ValidationError('Check-out date must be after check-in date')

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            self.reservation_number = self.generate_reservation_number()
        super().save(*args, **kwargs)

    def generate_reservation_number(self):
        """Generate unique reservation number"""
        import random
        import string
        prefix = 'RSV'
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{suffix}"

    @property
    def nights(self):
        """Calculate number of nights"""
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0

    def can_cancel(self):
        """Check if reservation can be cancelled"""
        return self.status in ['PENDING', 'CONFIRMED'] and self.check_in_date > date.today()

    def calculate_total_amount(self):
        """Calculate total amount from reservation rooms"""
        total = Decimal('0.00')
        for res_room in self.rooms.all():
            try:
                room_total = res_room.total_amount
                if room_total is not None:
                    total += room_total
            except (TypeError, ValueError):
                # Skip invalid room totals
                continue
        return total

    def update_total_amount(self):
        """Update total amount and save"""
        self.total_amount = self.calculate_total_amount()
        self.save(update_fields=['total_amount', 'updated_at'])


class ReservationRoom(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    extra_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['reservation', 'room']
        verbose_name = 'Reservation Room'
        verbose_name_plural = 'Reservation Rooms'

    def __str__(self):
        return f"Reservation {self.reservation.id} - Room {self.room.number}"

    @property
    def total_amount(self):
        """Calculate total amount for this room"""
        nights = getattr(self.reservation, 'nights', 0) or 0
        rate = self.rate or Decimal('0.00')
        discount = self.discount_amount or Decimal('0.00')
        extra = self.extra_charges or Decimal('0.00')
        
        subtotal = rate * nights
        return subtotal - discount + extra

    def clean(self):
        super().clean()
        # Check if room is available for the reservation dates
        if self.room and self.reservation:
            overlapping_reservations = ReservationRoom.objects.filter(
                room=self.room,
                reservation__check_in_date__lt=self.reservation.check_out_date,
                reservation__check_out_date__gt=self.reservation.check_in_date,
                reservation__status__in=['CONFIRMED', 'CHECKED_IN']
            ).exclude(reservation=self.reservation)
            
            if overlapping_reservations.exists():
                raise ValidationError(f'Room {self.room.number} is not available for the selected dates')
