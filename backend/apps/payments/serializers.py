from rest_framework import serializers
from decimal import Decimal
from .models import PaymentMethod, Bill, Payment


class PaymentMethodSerializer(serializers.ModelSerializer):
    payments_count = serializers.SerializerMethodField()
    total_payments_value = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'description', 'is_active', 'created_at', 'updated_at',
            'payments_count', 'total_payments_value'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_payments_count(self, obj):
        """Get total number of transactions using this payment method"""
        return obj.payment_set.filter(status='COMPLETED').count()

    def get_total_payments_value(self, obj):
        """Get total value of successful transactions"""
        from django.db.models import Sum
        total = obj.payment_set.filter(status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total']
        return float(total) if total else 0.0


class BillSerializer(serializers.ModelSerializer):
    reservation_number = serializers.CharField(source='reservation.reservation_number', read_only=True)
    guest_name = serializers.CharField(source='reservation.guest.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transactions = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    tax_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'reservation', 'reservation_number', 'guest_name',
            'subtotal', 'tax_amount', 'service_charge', 'discount_amount',
            'total_amount', 'paid_amount', 'remaining_balance', 'status',
            'status_display', 'due_date', 'is_overdue', 'notes', 'created_at',
            'updated_at', 'transactions', 'tax_breakdown'
        ]
        read_only_fields = ['bill_number', 'created_at', 'updated_at', 'paid_amount']

    def get_transactions(self, obj):
        """Get all transactions for this bill"""
        transactions = obj.transaction_set.all().order_by('-created_at')
        return PaymentSerializer(payments, many=True).data

    def get_remaining_balance(self, obj):
        """Get remaining balance"""
        return float(obj.total_amount - obj.paid_amount)

    def get_is_overdue(self, obj):
        """Check if bill is overdue"""
        from django.utils import timezone
        return obj.due_date and obj.due_date < timezone.now().date() and obj.status != 'PAID'

    def get_tax_breakdown(self, obj):
        """Get tax breakdown details"""
        # Assuming Indonesian tax structure
        subtotal = float(obj.subtotal)
        service_charge = float(obj.service_charge)
        
        # Service charge is typically 10% of subtotal
        service_charge_rate = 0.10
        
        # Tax is typically 11% PPN (VAT) on subtotal + service charge
        tax_rate = 0.11
        taxable_amount = subtotal + service_charge
        
        return {
            'subtotal': subtotal,
            'service_charge': service_charge,
            'service_charge_rate': service_charge_rate,
            'taxable_amount': float(taxable_amount),
            'tax_rate': tax_rate,
            'tax_amount': float(obj.tax_amount),
            'total_before_discount': float(subtotal + service_charge + obj.tax_amount),
            'discount_amount': float(obj.discount_amount),
            'final_total': float(obj.total_amount)
        }


class BillListSerializer(serializers.ModelSerializer):
    """Simplified serializer for bill listings"""
    reservation_number = serializers.CharField(source='reservation.reservation_number', read_only=True)
    guest_name = serializers.CharField(source='reservation.guest.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    remaining_balance = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'reservation_number', 'guest_name',
            'total_amount', 'paid_amount', 'remaining_balance', 'status',
            'status_display', 'due_date', 'is_overdue', 'created_at'
        ]

    def get_remaining_balance(self, obj):
        """Get remaining balance"""
        return float(obj.total_amount - obj.paid_amount)

    def get_is_overdue(self, obj):
        """Check if bill is overdue"""
        from django.utils import timezone
        return obj.due_date and obj.due_date < timezone.now().date() and obj.status != 'PAID'


class BillCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating bills"""
    class Meta:
        model = Bill
        fields = [
            'reservation', 'subtotal', 'tax_amount', 'service_charge',
            'discount_amount', 'total_amount', 'due_date', 'notes'
        ]

    def validate(self, data):
        """Validate bill data"""
        subtotal = data.get('subtotal', Decimal('0'))
        tax_amount = data.get('tax_amount', Decimal('0'))
        service_charge = data.get('service_charge', Decimal('0'))
        discount_amount = data.get('discount_amount', Decimal('0'))
        total_amount = data.get('total_amount', Decimal('0'))
        
        # Calculate expected total
        calculated_total = subtotal + tax_amount + service_charge - discount_amount
        
        if abs(calculated_total - total_amount) > Decimal('0.01'):  # Allow for rounding differences
            raise serializers.ValidationError(
                f"Total amount {total_amount} doesn't match calculated total {calculated_total}"
            )
        
        if subtotal < 0:
            raise serializers.ValidationError("Subtotal cannot be negative")
        
        if tax_amount < 0:
            raise serializers.ValidationError("Tax amount cannot be negative")
        
        if service_charge < 0:
            raise serializers.ValidationError("Service charge cannot be negative")
        
        if discount_amount < 0:
            raise serializers.ValidationError("Discount amount cannot be negative")
        
        return data


class PaymentSerializer(serializers.ModelSerializer):
    bill_number = serializers.CharField(source='bill.bill_number', read_only=True)
    guest_name = serializers.CharField(source='bill.reservation.guest.full_name', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'bill', 'bill_number', 'guest_name',
            'payment_method', 'payment_method_name', 'amount', 'status',
            'status_display', 'reference_number', 'notes', 'processed_at',
            'created_at'
        ]
        read_only_fields = ['transaction_id', 'processed_at', 'created_at']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transactions"""
    class Meta:
        model = Payment
        fields = [
            'bill', 'payment_method', 'amount', 'reference_number', 'notes'
        ]

    def validate(self, data):
        """Validate transaction data"""
        bill = data['bill']
        amount = data['amount']
        
        if amount <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero")
        
        # Check if bill is already paid
        if bill.status == 'PAID':
            raise serializers.ValidationError("Cannot add payment to already paid bill")
        
        # Check if amount exceeds remaining balance
        remaining_balance = bill.total_amount - bill.paid_amount
        if amount > remaining_balance:
            raise serializers.ValidationError(
                f"Payment amount {amount} exceeds remaining balance {remaining_balance}"
            )
        
        return data

    def create(self, validated_data):
        """Create transaction and update bill status"""
        from django.utils import timezone
        
        payment = Payment.objects.create(**validated_data)
        
        # Mark transaction as successful and set processed time
        transaction.status = 'SUCCESS'
        transaction.processed_at = timezone.now()
        transaction.save(update_fields=['status', 'processed_at'])
        
        # Update bill paid amount and status
        bill = transaction.bill
        bill.paid_amount += transaction.amount
        
        if bill.paid_amount >= bill.total_amount:
            bill.status = 'PAID'
        elif bill.paid_amount > 0:
            bill.status = 'PARTIALLY_PAID'
        
        bill.save(update_fields=['paid_amount', 'status', 'updated_at'])
        
        return transaction


class PaymentSummarySerializer(serializers.Serializer):
    """Serializer for payment summary statistics"""
    total_bills = serializers.IntegerField()
    paid_bills = serializers.IntegerField()
    partially_paid_bills = serializers.IntegerField()
    unpaid_bills = serializers.IntegerField()
    overdue_bills = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_bill_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class RevenueReportSerializer(serializers.Serializer):
    """Serializer for revenue reports"""
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()
    payment_method_breakdown = serializers.ListField()
    daily_revenue = serializers.ListField()
    top_revenue_days = serializers.ListField()


class PaymentMethodPerformanceSerializer(serializers.Serializer):
    """Serializer for payment method performance"""
    payment_method = serializers.CharField()
    total_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    success_rate = serializers.FloatField()
    average_transaction_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentage_of_total = serializers.FloatField()


class OutstandingPaymentsSerializer(serializers.Serializer):
    """Serializer for outstanding payments report"""
    bill_id = serializers.IntegerField()
    bill_number = serializers.CharField()
    reservation_number = serializers.CharField()
    guest_name = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    outstanding_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    due_date = serializers.DateField()
    days_overdue = serializers.IntegerField()
    status = serializers.CharField()


class DailyRevenueSerializer(serializers.Serializer):
    """Serializer for daily revenue data"""
    date = serializers.DateField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()
    cash_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    card_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    digital_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_transaction_amount = serializers.DecimalField(max_digits=10, decimal_places=2)