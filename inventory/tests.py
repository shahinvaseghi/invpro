from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from inventory import models as inventory_models
from shared import models as shared_models


class InventoryModelTests(TestCase):
    def setUp(self):
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
        self.person = shared_models.Person.objects.create(
            company=self.company,
            public_code="00000001",
            username="person1",
            first_name="Ali",
            last_name="Ahmadi",
            is_enabled=1,
            sort_order=1,
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

    def create_item(self) -> inventory_models.Item:
        return inventory_models.Item.objects.create(
            company=self.company,
            type=self.item_type,
            category=self.item_category,
            subcategory=self.item_subcategory,
            user_segment="01",
            name="Sulfuric Acid",
            name_en="Sulfuric Acid",
            default_unit="L",
            primary_unit="L",
            is_enabled=1,
        )

    def test_item_code_and_batch_generation(self):
        item = self.create_item()
        self.assertTrue(item.item_code.startswith("00100100101"))
        self.assertEqual(len(item.sequence_segment), 5)
        self.assertIn("-", item.batch_number)

    def test_purchase_request_populates_codes(self):
        item = self.create_item()
        purchase_request = inventory_models.PurchaseRequest.objects.create(
            company=self.company,
            request_code="PR-001",
            requested_by=self.person,
            item=item,
            unit="L",
            quantity_requested=Decimal("100.000"),
            is_enabled=1,
        )
        self.assertEqual(purchase_request.item_code, item.item_code)
        self.assertEqual(purchase_request.requested_by_code, self.person.public_code)

    def test_receipt_permanent_auto_sets_codes(self):
        item = self.create_item()
        receipt = inventory_models.ReceiptPermanent.objects.create(
            company=self.company,
            document_code="RC-001",
            item=item,
            warehouse=self.warehouse,
            unit="L",
            quantity=Decimal("50.000"),
            is_enabled=1,
        )
        self.assertEqual(receipt.item_code, item.item_code)
        self.assertEqual(receipt.warehouse_code, self.warehouse.public_code)

    def test_item_lot_generation(self):
        item = self.create_item()
        receipt = inventory_models.ReceiptPermanent.objects.create(
            company=self.company,
            document_code="RC-LOT-001",
            item=item,
            warehouse=self.warehouse,
            unit="L",
            quantity=Decimal("10.000"),
            is_enabled=1,
        )
        lot = inventory_models.ItemLot.objects.create(
            company=self.company,
            item=item,
            receipt_document=receipt,
            unit="L",
            quantity=Decimal("10.000"),
            is_enabled=1,
        )
        self.assertTrue(lot.lot_code.startswith("LOT-"))
        self.assertEqual(lot.receipt_document_code, receipt.document_code)
        # ensure lot timestamp roughly equals now
        self.assertLess(abs((lot.created_at - timezone.now()).total_seconds()), 5)
