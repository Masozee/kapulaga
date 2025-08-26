from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
import random
import string
from apps.reservations.models import Reservation


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'

    def __str__(self):
        return self.name


class Bill(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='bill')
    bill_number = models.CharField(max_length=20, unique=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'

    def __str__(self):
        return f"Bill {self.bill_number} - {self.reservation.guest.full_name} - ${self.total_amount}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = self.generate_bill_number()
        
        # Auto-calculate tax and service charge if not set
        if not self.tax_amount and self.subtotal:
            self.tax_amount = (self.subtotal * self.tax_rate / 100)
        
        if not self.service_charge and self.subtotal:
            self.service_charge = (self.subtotal * self.service_charge_rate / 100)
        
        # Calculate total if not set
        if not self.total_amount:
            self.total_amount = self.subtotal + self.tax_amount + self.service_charge - self.discount_amount
        
        super().save(*args, **kwargs)

    def generate_bill_number(self):
        """Generate unique bill number"""
        prefix = 'BILL'
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{suffix}"

    @property
    def payment_status(self):
        """Calculate payment status based on payments"""
        total_paid = self.payments.filter(status='COMPLETED').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        if total_paid == 0:
            return 'PENDING'
        elif total_paid >= self.total_amount:
            return 'PAID'
        else:
            return 'PARTIAL'

    @property
    def amount_paid(self):
        """Calculate total amount paid"""
        return self.payments.filter(status='COMPLETED').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return max(Decimal('0.00'), self.total_amount - self.amount_paid)


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=20, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    processed_by = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"Payment {self.transaction_id} - ${self.amount} via {self.payment_method.name}"

    def clean(self):
        super().clean()
        if self.bill:
            current_paid = self.bill.amount_paid
            if self.status == 'COMPLETED' and self.pk:
                # Exclude current payment from calculation if updating
                current_payment = Payment.objects.filter(pk=self.pk).first()
                if current_payment:
                    current_paid -= current_payment.amount
            
            if current_paid + self.amount > self.bill.total_amount:
                raise ValidationError(f'Payment amount ${self.amount} would exceed bill balance of ${self.bill.balance_due}')

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        # Calculate processing fee if not set
        if not self.processing_fee and self.payment_method.processing_fee_percentage > 0:
            self.processing_fee = (self.amount * self.payment_method.processing_fee_percentage / 100)
        
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        prefix = 'PAY'
        suffix = ''.join(random.choices(string.digits, k=9))
        return f"{prefix}{suffix}"
