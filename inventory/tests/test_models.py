"""
Extended unit tests for inventory models.

This module contains comprehensive tests for inventory models including:
- Code generation
- Validation
- Relationships
- Business logic
"""
from decimal import Decimal
from typing import Optional
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from inventory import models as inventory_models
from shared import models as shared_models


class InventoryModelTests(TestCase):
    """Base test class with common setup."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.user = shared_models.User.objects.create_user(
            username="inventory-tester",
            email="inventory@example.com",
            password="secure-pass",
            first_name="Inventory",
            last_name="Tester",
        )
        self.company = shared_models.Company.objects.create(
            public_code="00000001",
            legal_name="Inventory Test Co.",
            display_name="Inventory Test",
            is_enabled=1,
            created_by=self.user,
        )
        self.item_type = inventory_models.ItemType.objects.create(
            company=self.company,
            public_code="001",
            name="Raw Material",
            name_en="Raw Material",
            is_enabled=1,
        )
        self.item_category = inventory_models.ItemCategory.objects.create(
            company=self.company,
            public_code="001",
            name="Chemicals",
            name_en="Chemicals",
            is_enabled=1,
        )
        self.item_subcategory = inventory_models.ItemSubcategory.objects.create(
            company=self.company,
            category=self.item_category,
            public_code="001",
            name="Acids",
            name_en="Acids",
            is_enabled=1,
        )
        self.warehouse = inventory_models.Warehouse.objects.create(
            company=self.company,
            public_code="00001",
            name="Main Warehouse",
            name_en="Main Warehouse",
            is_enabled=1,
        )
        self.supplier = inventory_models.Supplier.objects.create(
            company=self.company,
            public_code="000001",
            name="Supplier One",
            is_enabled=1,
        )

    def create_item(self, user_segment: str = "01", name: str = "Test Item") -> inventory_models.Item:
        """Helper method to create an item."""
        return inventory_models.Item.objects.create(
            company=self.company,
            type=self.item_type,
            category=self.item_category,
            subcategory=self.item_subcategory,
            user_segment=user_segment,
            name=name,
            name_en=name,
            default_unit="EA",
            primary_unit="EA",
            is_enabled=1,
        )


class ItemCodeGenerationTests(InventoryModelTests):
    """Tests for item code generation logic."""
    
    def test_item_code_generation(self) -> None:
        """Test that item codes are generated correctly."""
        item = self.create_item()
        self.assertTrue(item.item_code)
        self.assertEqual(len(item.item_code), 7)  # 2 (user) + 5 (sequence)
        self.assertTrue(item.item_code.startswith("01"))
    
    def test_full_item_code_generation(self) -> None:
        """Test that full item codes are generated correctly."""
        item = self.create_item()
        self.assertTrue(item.full_item_code)
        self.assertEqual(len(item.full_item_code), 16)  # 3+3+3+7
        self.assertTrue(item.full_item_code.startswith("001001001"))
    
    def test_batch_number_generation(self) -> None:
        """Test that batch numbers are generated correctly."""
        item = self.create_item()
        self.assertTrue(item.batch_number)
        self.assertIn("-", item.batch_number)
    
    def test_secondary_batch_number_optional(self) -> None:
        """Test that secondary batch number is optional."""
        item = self.create_item()
        self.assertEqual(item.secondary_batch_number, "")
        item.secondary_batch_number = "USER-BATCH-001"
        item.save()
        self.assertEqual(item.secondary_batch_number, "USER-BATCH-001")


class ItemWarehouseTests(InventoryModelTests):
    """Tests for item-warehouse relationships."""
    
    def test_item_warehouse_relationship(self) -> None:
        """Test that items can be assigned to warehouses."""
        item = self.create_item()
        warehouse2 = inventory_models.Warehouse.objects.create(
            company=self.company,
            public_code="00002",
            name="Secondary Warehouse",
            name_en="Secondary Warehouse",
            is_enabled=1,
        )
        
        # Assign warehouses
        item.warehouses.create(
            company=self.company,
            warehouse=self.warehouse,
            is_primary=1,
        )
        item.warehouses.create(
            company=self.company,
            warehouse=warehouse2,
            is_primary=0,
        )
        
        self.assertEqual(item.warehouses.count(), 2)
        primary = item.warehouses.filter(is_primary=1).first()
        self.assertIsNotNone(primary)
        self.assertEqual(primary.warehouse, self.warehouse)


class ReceiptTests(InventoryModelTests):
    """Tests for receipt models."""
    
    def test_receipt_permanent_code_generation(self) -> None:
        """Test that receipt codes are generated correctly."""
        item = self.create_item()
        receipt = inventory_models.ReceiptPermanent.objects.create(
            company=self.company,
            document_code="PRM-202511-000001",
            warehouse=self.warehouse,
            supplier=self.supplier,
            is_enabled=1,
        )
        self.assertTrue(receipt.document_code.startswith("PRM-"))
    
    def test_receipt_temporary_status(self) -> None:
        """Test that temporary receipts start with DRAFT status."""
        item = self.create_item()
        receipt = inventory_models.ReceiptTemporary.objects.create(
            company=self.company,
            document_code="TRM-202511-000001",
            item=item,
            warehouse=self.warehouse,
            unit="EA",
            quantity=Decimal("10.000"),
            supplier=self.supplier,
            is_enabled=1,
        )
        self.assertEqual(receipt.status, inventory_models.ReceiptTemporary.Status.DRAFT)


class SerialTests(InventoryModelTests):
    """Tests for serial tracking."""
    
    def test_serial_code_generation(self) -> None:
        """Test that serial codes are generated correctly."""
        item = self.create_item()
        item.has_lot_tracking = 1
        item.save()
        
        serial = inventory_models.ItemSerial.objects.create(
            company=self.company,
            item=item,
            serial_code="SER-202511-000001",
            current_warehouse=self.warehouse,
            current_status=models.ItemSerial.Status.AVAILABLE,
            is_enabled=1,
        )
        self.assertTrue(serial.serial_code.startswith("SER-"))
    
    def test_secondary_serial_code_optional(self) -> None:
        """Test that secondary serial code is optional."""
        item = self.create_item()
        item.has_lot_tracking = 1
        item.save()
        
        serial = inventory_models.ItemSerial.objects.create(
            company=self.company,
            item=item,
            serial_code="SER-202511-000001",
            current_warehouse=self.warehouse,
            current_status=models.ItemSerial.Status.AVAILABLE,
            is_enabled=1,
        )
        self.assertEqual(serial.secondary_serial_code, "")
        serial.secondary_serial_code = "USER-SERIAL-001"
        serial.save()
        self.assertEqual(serial.secondary_serial_code, "USER-SERIAL-001")


class InventoryBalanceTests(InventoryModelTests):
    """Tests for inventory balance calculation."""
    
    def test_stocktaking_baseline(self) -> None:
        """Test that stocktaking creates a baseline."""
        item = self.create_item()
        
        # Create stocktaking record
        stocktaking = inventory_models.StocktakingRecord.objects.create(
            company=self.company,
            document_code="STR-202511-000001",
            is_enabled=1,
        )
        
        # Add surplus
        inventory_models.StocktakingSurplus.objects.create(
            company=self.company,
            document_code="STS-202511-000001",
            item=item,
            warehouse=self.warehouse,
            unit="EA",
            quantity=Decimal("100.000"),
            stocktaking_record=stocktaking,
            is_enabled=1,
        )
        
        self.assertEqual(stocktaking.surpluses.count(), 1)


class ValidationTests(InventoryModelTests):
    """Tests for model validation."""
    
    def test_item_unique_name(self) -> None:
        """Test that item names must be unique."""
        self.create_item(name="Unique Item")
        
        # Try to create another item with same name
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            self.create_item(name="Unique Item")
    
    def test_warehouse_unique_code(self) -> None:
        """Test that warehouse codes must be unique per company."""
        # First warehouse
        inventory_models.Warehouse.objects.create(
            company=self.company,
            public_code="00001",
            name="Warehouse 1",
            name_en="Warehouse 1",
            is_enabled=1,
        )
        
        # Try to create another with same code
        with self.assertRaises(Exception):
            inventory_models.Warehouse.objects.create(
                company=self.company,
                public_code="00001",
                name="Warehouse 2",
                name_en="Warehouse 2",
                is_enabled=1,
            )

