from django.core.management.base import BaseCommand
from inventory.models import ReceiptPermanent, ReceiptPermanentLine


class Command(BaseCommand):
    help = 'Delete all test receipts and their lines, or show receipt data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show',
            action='store_true',
            help='Show receipt data instead of deleting',
        )

    def handle(self, *args, **options):
        if options['show']:
            self._show_data()
        else:
            self._delete_all()

    def _show_data(self):
        """Show receipt data from database."""
        self.stdout.write("=" * 80)
        self.stdout.write("RECEIPTPERMANENT TABLE")
        self.stdout.write("=" * 80)
        receipts = ReceiptPermanent.objects.all().order_by('-id')[:20]
        total = ReceiptPermanent.objects.count()
        self.stdout.write(f"Total receipts: {total}\n")
        
        for r in receipts:
            self.stdout.write(f"ID: {r.id}")
            self.stdout.write(f"  Code: {r.document_code}")
            self.stdout.write(f"  Date: {r.document_date}")
            self.stdout.write(f"  Company ID: {r.company_id}")
            if hasattr(r, 'created_by_id') and r.created_by_id:
                self.stdout.write(f"  Created By: {r.created_by_id}")
            lines_count = r.lines.count()
            self.stdout.write(f"  Lines Count: {lines_count}")
            self.stdout.write("")
        
        self.stdout.write("=" * 80)
        self.stdout.write("RECEIPTPERMANENTLINE TABLE")
        self.stdout.write("=" * 80)
        lines = ReceiptPermanentLine.objects.all().order_by('-id')[:30]
        total_lines = ReceiptPermanentLine.objects.count()
        self.stdout.write(f"Total lines: {total_lines}\n")
        
        for l in lines:
            self.stdout.write(f"ID: {l.id}")
            self.stdout.write(f"  Receipt ID: {l.document_id if l.document_id else 'None'}")
            if l.document:
                self.stdout.write(f"  Receipt Code: {l.document.document_code}")
            self.stdout.write(f"  Item ID: {l.item_id if l.item_id else 'None'}")
            if l.item:
                self.stdout.write(f"  Item Name: {l.item.name}")
            self.stdout.write(f"  Quantity: {l.quantity}")
            self.stdout.write(f"  Unit: {l.unit}")
            self.stdout.write(f"  Entered Quantity: {l.entered_quantity}")
            self.stdout.write(f"  Entered Unit: {l.entered_unit}")
            self.stdout.write(f"  Warehouse ID: {l.warehouse_id if l.warehouse_id else 'None'}")
            self.stdout.write("")
        
        self.stdout.write("=" * 80)
        self.stdout.write("RECENT RECEIPTS WITH LINES")
        self.stdout.write("=" * 80)
        recent_receipts = ReceiptPermanent.objects.all().order_by('-id')[:5]
        for r in recent_receipts:
            self.stdout.write(f"\nReceipt: {r.document_code} (ID: {r.id})")
            receipt_lines = r.lines.all()
            if receipt_lines.exists():
                for line in receipt_lines:
                    self.stdout.write(f"  Line {line.id}: Item={line.item_id} ({line.item.name if line.item else 'None'}), Qty={line.quantity}, Unit={line.unit}, Entered Qty={line.entered_quantity}, Entered Unit={line.entered_unit}")
            else:
                self.stdout.write(f"  ⚠️  No lines found!")

    def _delete_all(self):
        """Delete all test receipts and their lines."""
        # Delete all receipt lines first (CASCADE will handle this, but explicit is better)
        line_count = ReceiptPermanentLine.objects.count()
        ReceiptPermanentLine.objects.all().delete()
        
        # Delete all receipts
        receipt_count = ReceiptPermanent.objects.count()
        ReceiptPermanent.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {receipt_count} receipts and {line_count} receipt lines.'
            )
        )

