from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import InventoryCategory, InventoryItem, StockMovement, Supplier


class InventoryCategoryModelTest(TestCase):
    def test_create_category(self):
        """Test creating inventory category"""
        category = InventoryCategory.objects.create(
            name='Amenities',
            description='Room amenities and supplies'
        )
        self.assertEqual(category.name, 'Amenities')
        self.assertTrue(category.is_active)

    def test_category_str_representation(self):
        """Test string representation of category"""
        category = InventoryCategory(name='Linens')
        self.assertEqual(str(category), 'Linens')


class SupplierModelTest(TestCase):
    def test_create_supplier(self):
        """Test creating supplier"""
        supplier = Supplier.objects.create(
            name='ABC Supplies',
            contact_person='John Doe',
            phone='+628123456789',
            email='john@abcsupplies.com'
        )
        self.assertEqual(supplier.name, 'ABC Supplies')
        self.assertEqual(supplier.contact_person, 'John Doe')
        self.assertTrue(supplier.is_active)


class InventoryItemModelTest(TestCase):
    def setUp(self):
        self.category = InventoryCategory.objects.create(
            name='Amenities',
            description='Room amenities'
        )
        self.supplier = Supplier.objects.create(
            name='XYZ Supplier',
            contact_person='Jane Smith'
        )

    def test_create_inventory_item(self):
        """Test creating inventory item"""
        item = InventoryItem.objects.create(
            name='Towel',
            category=self.category,
            unit='piece',
            current_stock=100,
            minimum_stock=20,
            unit_cost=Decimal('15.00'),
            supplier=self.supplier
        )
        self.assertEqual(item.name, 'Towel')
        self.assertEqual(item.current_stock, 100)
        self.assertEqual(item.minimum_stock, 20)
        self.assertEqual(item.unit_cost, Decimal('15.00'))

    def test_is_low_stock(self):
        """Test low stock detection"""
        item = InventoryItem.objects.create(
            name='Shampoo',
            category=self.category,
            current_stock=10,
            minimum_stock=20
        )
        self.assertTrue(item.is_low_stock())

        item.current_stock = 30
        self.assertFalse(item.is_low_stock())

    def test_item_str_representation(self):
        """Test string representation of item"""
        item = InventoryItem(name='Soap')
        self.assertEqual(str(item), 'Soap')


class StockMovementModelTest(TestCase):
    def setUp(self):
        self.category = InventoryCategory.objects.create(name='Cleaning')
        self.item = InventoryItem.objects.create(
            name='Toilet Paper',
            category=self.category,
            current_stock=50
        )

    def test_create_stock_in(self):
        """Test stock in movement"""
        movement = StockMovement.objects.create(
            item=self.item,
            movement_type='IN',
            quantity=20,
            reason='Purchase',
            notes='Weekly stock replenishment'
        )
        self.assertEqual(movement.movement_type, 'IN')
        self.assertEqual(movement.quantity, 20)
        
        # Check stock updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, 70)

    def test_create_stock_out(self):
        """Test stock out movement"""
        movement = StockMovement.objects.create(
            item=self.item,
            movement_type='OUT',
            quantity=15,
            reason='Room Usage',
            notes='Daily housekeeping consumption'
        )
        self.assertEqual(movement.movement_type, 'OUT')
        self.assertEqual(movement.quantity, 15)
        
        # Check stock updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, 35)

    def test_stock_movement_validation(self):
        """Test stock movement validation"""
        # Cannot have negative stock out more than available
        with self.assertRaises(ValidationError):
            movement = StockMovement(
                item=self.item,
                movement_type='OUT',
                quantity=100,  # More than current stock (50)
                reason='Test'
            )
            movement.full_clean()

    def test_movement_str_representation(self):
        """Test string representation of movement"""
        movement = StockMovement(
            item=self.item,
            movement_type='IN',
            quantity=10
        )
        expected = 'Toilet Paper - IN: 10'
        self.assertEqual(str(movement), expected)
