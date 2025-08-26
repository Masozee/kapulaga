from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from .models import Bill, Payment, PaymentMethod


class PaymentMethodModelTest(TestCase):
    def test_create_payment_method(self):
        """Test creating payment method"""
        method = PaymentMethod.objects.create(
            name='Credit Card',
            code='CREDIT_CARD',
            description='Visa/Mastercard payments'
        )
        self.assertEqual(method.name, 'Credit Card')
        self.assertEqual(method.code, 'CREDIT_CARD')
        self.assertTrue(method.is_active)


class BillModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        self.reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
            total_amount=Decimal('300.00')
        )

    def test_create_bill(self):
        """Test creating a bill"""
        bill = Bill.objects.create(
            reservation=self.reservation,
            subtotal=Decimal('300.00'),
            tax_amount=Decimal('30.00'),
            service_charge=Decimal('15.00'),
            total_amount=Decimal('345.00')
        )
        self.assertEqual(bill.reservation, self.reservation)
        self.assertEqual(bill.subtotal, Decimal('300.00'))
        self.assertEqual(bill.total_amount, Decimal('345.00'))
        self.assertEqual(bill.status, 'PENDING')

    def test_bill_str_representation(self):
        """Test string representation of bill"""
        bill = Bill.objects.create(
            reservation=self.reservation,
            total_amount=Decimal('345.00')
        )
        expected = f"Bill {bill.bill_number} - John Doe - $345.00"
        self.assertEqual(str(bill), expected)

    def test_bill_generate_number(self):
        """Test bill number generation"""
        bill = Bill.objects.create(
            reservation=self.reservation,
            total_amount=Decimal('345.00')
        )
        self.assertTrue(bill.bill_number.startswith('BILL'))
        self.assertEqual(len(bill.bill_number), 10)  # BILL + 6 digits

    def test_bill_payment_status(self):
        """Test bill payment status calculation"""
        bill = Bill.objects.create(
            reservation=self.reservation,
            total_amount=Decimal('300.00')
        )
        
        # No payments - pending
        self.assertEqual(bill.payment_status, 'PENDING')
        
        # Partial payment
        payment_method = PaymentMethod.objects.create(name='Cash', code='CASH')
        Payment.objects.create(
            bill=bill,
            payment_method=payment_method,
            amount=Decimal('100.00'),
            status='COMPLETED'
        )
        self.assertEqual(bill.payment_status, 'PARTIAL')
        
        # Full payment
        Payment.objects.create(
            bill=bill,
            payment_method=payment_method,
            amount=Decimal('200.00'),
            status='COMPLETED'
        )
        self.assertEqual(bill.payment_status, 'PAID')


class PaymentModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )
        self.reservation = Reservation.objects.create(
            guest=self.guest,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=1),
            total_amount=Decimal('200.00')
        )
        self.bill = Bill.objects.create(
            reservation=self.reservation,
            total_amount=Decimal('200.00')
        )
        self.payment_method = PaymentMethod.objects.create(
            name='QRIS',
            code='QRIS'
        )

    def test_create_payment(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            bill=self.bill,
            payment_method=self.payment_method,
            amount=Decimal('200.00'),
            reference_number='QR123456789',
            status='COMPLETED'
        )
        self.assertEqual(payment.bill, self.bill)
        self.assertEqual(payment.amount, Decimal('200.00'))
        self.assertEqual(payment.status, 'COMPLETED')

    def test_payment_str_representation(self):
        """Test string representation of payment"""
        payment = Payment.objects.create(
            bill=self.bill,
            payment_method=self.payment_method,
            amount=Decimal('200.00')
        )
        expected = f"Payment {payment.transaction_id} - $200.00 via QRIS"
        self.assertEqual(str(payment), expected)

    def test_payment_transaction_id_generation(self):
        """Test payment transaction ID generation"""
        payment = Payment.objects.create(
            bill=self.bill,
            payment_method=self.payment_method,
            amount=Decimal('200.00')
        )
        self.assertTrue(payment.transaction_id.startswith('PAY'))
        self.assertEqual(len(payment.transaction_id), 12)  # PAY + 9 digits

    def test_overpayment_validation(self):
        """Test that overpayment is prevented"""
        Payment.objects.create(
            bill=self.bill,
            payment_method=self.payment_method,
            amount=Decimal('150.00'),
            status='COMPLETED'
        )
        
        with self.assertRaises(ValidationError):
            payment = Payment(
                bill=self.bill,
                payment_method=self.payment_method,
                amount=Decimal('100.00')  # Would exceed bill total
            )
            payment.full_clean()
