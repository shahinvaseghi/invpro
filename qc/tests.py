from decimal import Decimal

from django.test import TestCase

from inventory import models as inventory_models
from qc import models as qc_models
from shared import models as shared_models


class ReceiptInspectionTests(TestCase):
    def setUp(self):
        self.user = shared_models.User.objects.create_user(
            username="qc-tester",
            email="qc@example.com",
            password="secure-pass",
            first_name="QC",
            last_name="Tester",
        )
        self.company = shared_models.Company.objects.create(
            public_code="00000003",
            legal_name="QC Test Co.",
            display_name="QC Test",
            is_enabled=1,
            created_by=self.user,
        )
        self.inspector = shared_models.Person.objects.create(
            company=self.company,
            public_code="00000010",
            username="inspector1",
            first_name="Hossein",
            last_name="Moradi",
            is_enabled=1,
            sort_order=1,
        )
        self.approver = shared_models.Person.objects.create(
            company=self.company,
            public_code="00000011",
            username="approver1",
            first_name="Maryam",
            last_name="Ghasemi",
            is_enabled=1,
            sort_order=2,
        )

        self.item_type = inventory_models.ItemType.objects.create(
            company=self.company,
            public_code="003",
            name="QC Type",
            name_en="QC Type",
            is_enabled=1,
        )
        self.item_category = inventory_models.ItemCategory.objects.create(
            company=self.company,
            public_code="003",
            name="QC Category",
            name_en="QC Category",
            is_enabled=1,
        )
        self.item_subcategory = inventory_models.ItemSubcategory.objects.create(
            company=self.company,
            category=self.item_category,
            public_code="003",
            name="QC Subcategory",
            name_en="QC Subcategory",
            is_enabled=1,
        )
        self.item = inventory_models.Item.objects.create(
            company=self.company,
            type=self.item_type,
            category=self.item_category,
            subcategory=self.item_subcategory,
            user_segment="01",
            name="QC Item",
            name_en="QC Item",
            default_unit="EA",
            primary_unit="EA",
            requires_temporary_receipt=1,
            is_enabled=1,
        )
        self.warehouse = inventory_models.Warehouse.objects.create(
            company=self.company,
            public_code="70001",
            name="QC Warehouse",
            name_en="QC Warehouse",
            is_enabled=1,
        )
        self.supplier = inventory_models.Supplier.objects.create(
            company=self.company,
            public_code="500001",
            name="QC Supplier",
            is_enabled=1,
        )

        self.temporary_receipt = inventory_models.ReceiptTemporary.objects.create(
            company=self.company,
            document_code="TR-QC-001",
            item=self.item,
            warehouse=self.warehouse,
            unit="EA",
            quantity=Decimal("5"),
            supplier=self.supplier,
            is_enabled=1,
        )

    def test_receipt_inspection_autofills_codes(self):
        inspection = qc_models.ReceiptInspection.objects.create(
            company=self.company,
            temporary_receipt=self.temporary_receipt,
            inspection_code="QC-INS-001",
            inspector=self.inspector,
            approval_decision=qc_models.ReceiptInspection.ApprovalDecision.PENDING,
            is_enabled=1,
        )
        self.assertEqual(inspection.temporary_receipt_code, self.temporary_receipt.document_code)
        self.assertEqual(inspection.inspector_code, self.inspector.public_code)

    def test_receipt_inspection_approval_fields(self):
        inspection = qc_models.ReceiptInspection.objects.create(
            company=self.company,
            temporary_receipt=self.temporary_receipt,
            inspection_code="QC-INS-002",
            inspector=self.inspector,
            approval_decision=qc_models.ReceiptInspection.ApprovalDecision.APPROVED,
            approved_by=self.approver,
            is_enabled=1,
        )
        self.assertEqual(inspection.approved_by, self.approver)
        self.assertIn("QC-", inspection.inspection_code)
