from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime
import uuid
from apps.reservations.models import Reservation
from apps.rooms.models import Room


class CheckIn(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='checkin')
    actual_check_in_time = models.DateTimeField()
    adults_count = models.PositiveIntegerField(null=True, blank=True)
    children_count = models.PositiveIntegerField(default=0)
    identity_verified = models.BooleanField(default=True)
    verified_by = models.CharField(max_length=100, blank=True, null=True)
    deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    early_checkin_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    number_of_keys = models.PositiveIntegerField(default=1)
    special_requests_fulfilled = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Check In'
        verbose_name_plural = 'Check Ins'

    def __str__(self):
        room_numbers = ', '.join([room.room.number for room in self.reservation.rooms.all()])
        return f"Check-in: {self.reservation.guest.full_name} - Room {room_numbers} - {self.actual_check_in_time.date()}"

    def clean(self):
        super().clean()
        if self.reservation and self.reservation.status == 'CANCELLED':
            raise ValidationError('Cannot check in a cancelled reservation')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Update reservation status
            self.reservation.status = 'CHECKED_IN'
            self.reservation.save(update_fields=['status', 'updated_at'])
            
            # Update room status to occupied
            for res_room in self.reservation.rooms.all():
                res_room.room.status = 'OCCUPIED'
                res_room.room.save(update_fields=['status', 'updated_at'])
            
            # Create room keys
            self.create_room_keys()

    def create_room_keys(self):
        """Create room keys for check-in"""
        for res_room in self.reservation.rooms.all():
            for i in range(self.number_of_keys):
                RoomKey.objects.create(
                    check_in=self,
                    room=res_room.room,
                    key_code=f"{res_room.room.number}-{uuid.uuid4().hex[:6].upper()}"
                )


class CheckOut(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Fully Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('REFUNDED', 'Refunded'),
    ]

    ROOM_CONDITION_CHOICES = [
        ('CLEAN', 'Clean'),
        ('NEEDS_CLEANING', 'Needs Cleaning'),
        ('MAINTENANCE_REQUIRED', 'Maintenance Required'),
        ('DAMAGED', 'Damaged'),
    ]

    check_in = models.OneToOneField(CheckIn, on_delete=models.CASCADE, related_name='checkout')
    actual_check_out_time = models.DateTimeField()
    final_bill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    late_checkout_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    damage_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    room_condition = models.CharField(max_length=30, choices=ROOM_CONDITION_CHOICES, default='CLEAN')
    minibar_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    phone_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    processed_by = models.CharField(max_length=100, blank=True, null=True)
    feedback_rating = models.PositiveIntegerField(null=True, blank=True)
    feedback_comment = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Check Out'
        verbose_name_plural = 'Check Outs'

    def __str__(self):
        room_numbers = ', '.join([room.room.number for room in self.check_in.reservation.rooms.all()])
        return f"Check-out: {self.check_in.reservation.guest.full_name} - Room {room_numbers} - {self.actual_check_out_time.date()}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Update reservation status
            self.check_in.reservation.status = 'CHECKED_OUT'
            self.check_in.reservation.save(update_fields=['status', 'updated_at'])
            
            # Update room status to available
            for res_room in self.check_in.reservation.rooms.all():
                if self.room_condition == 'CLEAN':
                    res_room.room.status = 'AVAILABLE'
                elif self.room_condition in ['NEEDS_CLEANING', 'MAINTENANCE_REQUIRED']:
                    res_room.room.status = 'MAINTENANCE'
                elif self.room_condition == 'DAMAGED':
                    res_room.room.status = 'OUT_OF_ORDER'
                res_room.room.save(update_fields=['status', 'updated_at'])
            
            # Deactivate room keys
            self.deactivate_room_keys()

    def deactivate_room_keys(self):
        """Deactivate all room keys for this check-in"""
        keys = RoomKey.objects.filter(check_in=self.check_in, is_active=True)
        for key in keys:
            key.deactivate()

    @property
    def total_extra_charges(self):
        """Calculate total extra charges"""
        return (self.late_checkout_charge + self.damage_charge + 
                self.minibar_charges + self.phone_charges + self.other_charges)


class RoomKey(models.Model):
    KEY_TYPE_CHOICES = [
        ('PHYSICAL', 'Physical Key'),
        ('RFID', 'RFID Card'),
        ('MAGNETIC', 'Magnetic Card'),
        ('DIGITAL', 'Digital/Mobile Key'),
    ]

    check_in = models.ForeignKey(CheckIn, on_delete=models.CASCADE, related_name='keys')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    key_code = models.CharField(max_length=50, unique=True)
    key_type = models.CharField(max_length=20, choices=KEY_TYPE_CHOICES, default='RFID')
    is_active = models.BooleanField(default=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Room Key'
        verbose_name_plural = 'Room Keys'

    def __str__(self):
        return f"Key {self.key_code} - Room {self.room.number} - {self.check_in.reservation.guest.full_name}"

    def deactivate(self):
        """Deactivate the room key"""
        self.is_active = False
        self.deactivated_at = datetime.now()
        self.save(update_fields=['is_active', 'deactivated_at'])
