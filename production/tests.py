from decimal import Decimal

from django.test import TestCase

from inventory import models as inventory_models
from production import models as production_models
from shared import models as shared_models


class ProductionModelTests(TestCase):
    def setUp(self):
        self.user = shared_models.User.objects.create_user(
            username="prod-tester",
            email="prod@example.com",
            password="secure-pass",
            first_name="Prod",
            last_name="Tester",
        )
        self.company = shared_models.Company.objects.create(
            public_code="00000002",
            legal_name="Production Test Co.",
            display_name="Production Test",
            is_enabled=1,
            created_by=self.user,
        )
        self.person = shared_models.Person.objects.create(
            company=self.company,
            public_code="00000002",
            username="prod_person",
            first_name="Sara",
            last_name="Karimi",
            is_enabled=1,
            sort_order=1,
        )

        self.item_type = inventory_models.ItemType.objects.create(
            company=self.company,
            public_code="002",
            name="Semi Finished",
            name_en="Semi Finished",
            is_enabled=1,
        )
        self.item_category = inventory_models.ItemCategory.objects.create(
            company=self.company,
            public_code="002",
            name="Assemblies",
            name_en="Assemblies",
            is_enabled=1,
        )
        self.item_subcategory = inventory_models.ItemSubcategory.objects.create(
            company=self.company,
            category=self.item_category,
            public_code="002",
            name="Module",
            name_en="Module",
            is_enabled=1,
        )

        self.material_item = inventory_models.Item.objects.create(
            company=self.company,
            type=self.item_type,
            category=self.item_category,
            subcategory=self.item_subcategory,
            user_segment="01",
            name="Material Item",
            name_en="Material Item",
            default_unit="EA",
            primary_unit="EA",
            is_enabled=1,
        )
        self.finished_item = inventory_models.Item.objects.create(
            company=self.company,
            type=self.item_type,
            category=self.item_category,
            subcategory=self.item_subcategory,
            user_segment="01",
            name="Finished Item",
            name_en="Finished Item",
            default_unit="EA",
            primary_unit="EA",
            is_enabled=1,
        )
        self.work_center = production_models.WorkCenter.objects.create(
            company=self.company,
            public_code="100",
            name="Assembly Line",
            is_enabled=1,
        )

    def test_bom_material_populates_codes(self):
        bom = production_models.BOMMaterial.objects.create(
            company=self.company,
            finished_item=self.finished_item,
            material_item=self.material_item,
            quantity_per_unit=Decimal("2.5"),
            unit="EA",
            is_enabled=1,
        )
        self.assertEqual(bom.finished_item_code, self.finished_item.item_code)
        self.assertEqual(bom.material_item_code, self.material_item.item_code)

    def create_process(self):
        process = production_models.Process.objects.create(
            company=self.company,
            process_code="PROC-001",
            finished_item=self.finished_item,
            bom_code="BOM-001",
            revision="A",
            is_enabled=1,
        )
        production_models.ProcessStep.objects.create(
            company=self.company,
            process=process,
            work_center=self.work_center,
            sequence_order=1,
            labor_minutes_per_unit=Decimal("10"),
            machine_minutes_per_unit=Decimal("5"),
            is_enabled=1,
        )
        return process

    def test_process_populates_finished_item_code(self):
        process = self.create_process()
        self.assertEqual(process.finished_item_code, self.finished_item.item_code)
        step = process.steps.first()
        self.assertEqual(step.work_center_code, self.work_center.public_code)

    def test_product_order_autofill_codes(self):
        process = self.create_process()
        order = production_models.ProductOrder.objects.create(
            company=self.company,
            order_code="PO-001",
            finished_item=self.finished_item,
            bom_code="BOM-001",
            process=process,
            quantity_planned=Decimal("50"),
            unit="EA",
            is_enabled=1,
        )
        self.assertEqual(order.finished_item_code, self.finished_item.item_code)
        self.assertEqual(order.process_code, process.process_code)

    def test_order_performance_autofill(self):
        process = self.create_process()
        order = production_models.ProductOrder.objects.create(
            company=self.company,
            order_code="PO-002",
            finished_item=self.finished_item,
            bom_code="BOM-001",
            process=process,
            quantity_planned=Decimal("20"),
            unit="EA",
            is_enabled=1,
        )
        perf = production_models.OrderPerformance.objects.create(
            company=self.company,
            order=order,
            finished_item=self.finished_item,
            quantity_produced=Decimal("10"),
            is_enabled=1,
        )
        self.assertEqual(perf.order_code, order.order_code)
        self.assertEqual(perf.finished_item_code, self.finished_item.item_code)

    def test_transfer_to_line_item_codes(self):
        process = self.create_process()
        order = production_models.ProductOrder.objects.create(
            company=self.company,
            order_code="PO-003",
            finished_item=self.finished_item,
            bom_code="BOM-001",
            process=process,
            quantity_planned=Decimal("30"),
            unit="EA",
            is_enabled=1,
        )
        transfer = production_models.TransferToLine.objects.create(
            company=self.company,
            transfer_code="TR-001",
            order=order,
            is_enabled=1,
        )
        item = production_models.TransferToLineItem.objects.create(
            company=self.company,
            transfer=transfer,
            material_item=self.material_item,
            quantity_required=Decimal("30"),
            unit="EA",
            source_warehouse=inventory_models.Warehouse.objects.create(
                company=self.company,
                public_code="90001",
                name="Production WH",
                name_en="Production WH",
                is_enabled=1,
            ),
            destination_work_center=self.work_center,
            is_enabled=1,
        )
        self.assertEqual(item.material_item_code, self.material_item.item_code)
        self.assertEqual(item.source_warehouse_code, item.source_warehouse.public_code)
