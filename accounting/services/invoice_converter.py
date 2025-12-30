"""
Invoice Converter Service
سرویس تبدیل AccountingDocument به فرمت Invoice سامانه مودیان
"""
import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime
import jdatetime

from ..models import AccountingDocument, FiscalMemoryConfig
from shared.models import Company

logger = logging.getLogger('accounting.services.invoice_converter')


class InvoiceConverter:
    """
    تبدیل AccountingDocument به فرمت Invoice سامانه مودیان
    Convert AccountingDocument to Moadian Invoice format
    """
    
    def __init__(self, document: AccountingDocument, fiscal_memory: FiscalMemoryConfig):
        """
        Initialize converter.
        
        Args:
            document: AccountingDocument instance
            fiscal_memory: FiscalMemoryConfig instance
        """
        self.document = document
        self.fiscal_memory = fiscal_memory
        self.company = document.company
    
    def _get_company_tax_id(self) -> str:
        """Get company tax ID."""
        if self.company.tax_id:
            return self.company.tax_id
        raise ValueError("شناسه مالیاتی شرکت یافت نشد. لطفاً در تنظیمات شرکت اضافه کنید.")
    
    def _convert_date_to_timestamp(self, date_obj) -> int:
        """
        تبدیل تاریخ به timestamp (milliseconds)
        Convert date to timestamp in milliseconds
        """
        if isinstance(date_obj, datetime):
            dt = date_obj
        else:
            dt = datetime.combine(date_obj, datetime.min.time())
        
        return int(dt.timestamp() * 1000)
    
    def _convert_jalali_date(self, date_obj) -> tuple[int, int, int]:
        """
        تبدیل تاریخ به شمسی
        Convert date to Jalali (Persian) calendar
        """
        if isinstance(date_obj, datetime):
            jdate = jdatetime.datetime.fromgregorian(datetime=date_obj)
        else:
            jdate = jdatetime.date.fromgregorian(date=date_obj)
        
        return jdate.year, jdate.month, jdate.day
    
    def _generate_invoice_number(self) -> str:
        """
        تولید شماره فاکتور
        Generate invoice number from document number
        """
        # Use document number as invoice number
        return self.document.document_number
    
    def _get_buyer_party(self):
        """Get buyer party from document lines (first tafsili account that has a party)."""
        from ..models import PartyAccount
        
        # Try to find party from document lines
        for line in self.document.lines.all():
            if line.tafsili_account:
                # Try to find party account linked to this tafsili account
                party_account = PartyAccount.objects.filter(
                    company=self.company,
                    account=line.tafsili_account
                ).select_related('party').first()
                
                if party_account and party_account.party:
                    return party_account.party
        
        return None
    
    def _build_header(self) -> Dict[str, Any]:
        """
        ساخت Header صورتحساب
        Build invoice header
        """
        tax_id = self._get_company_tax_id()
        year, month, day = self._convert_jalali_date(self.document.document_date)
        
        # Convert date to required format
        indatim = f"{year:04d}{month:02d}{day:02d}"
        indati2m = self._convert_date_to_timestamp(self.document.document_date)
        
        # Get buyer information
        buyer_party = self._get_buyer_party()
        
        header = {
            "taxid": tax_id,
            "indatim": indatim,  # تاریخ صورتحساب (YYYYMMDD)
            "indati2m": indati2m,  # Timestamp
            "inty": 1,  # نوع صورتحساب (1=فروش، 2=خرید، ...)
            "inno": self._generate_invoice_number(),
            "irtaxid": tax_id,  # شناسه مالیاتی فروشنده
            "inp": 1,  # الگوی صورتحساب
            "ins": 1,  # موضوع صورتحساب
            "tins": buyer_party.tax_id if buyer_party and buyer_party.tax_id else "",  # شناسه مالیاتی خریدار
            "tob": "1" if buyer_party and buyer_party.party_type == 'customer' else "2",  # نوع شخص خریدار (1=حقیقی، 2=حقوقی)
            "bid": buyer_party.national_id if buyer_party and buyer_party.national_id else "",  # شناسه ملی/اقتصادی خریدار
            "tinb": buyer_party.tax_id if buyer_party and buyer_party.tax_id else "",  # شناسه مالیاتی خریدار
            "sbc": "",  # کد پستی خریدار (از آدرس استخراج شود)
            "bpc": "",  # کد پستی خریدار
            "bpn": buyer_party.party_name if buyer_party else "",  # نام خریدار
            "bpb": "",  # نام خانوادگی/نام شرکت خریدار
            "bcb": buyer_party.party_name if buyer_party else "",  # نام تجاری خریدار
            "bbs": "",  # استان خریدار
            "bci": "",  # شهر خریدار
            "cap": Decimal('0.00'),  # مبلغ کل قبل از تخفیف (باید محاسبه شود)
            "insp": Decimal('0.00'),  # مبلغ کل بعد از تخفیف (باید محاسبه شود)
            "tvop": Decimal('0.00'),  # جمع کل پرداخت‌ها (باید محاسبه شود)
            "tax17": Decimal('0.00'),  # مالیات بر ارزش افزوده (باید محاسبه شود)
        }
        
        return header
    
    def _build_body_item(self, line, index: int) -> Optional[Dict[str, Any]]:
        """
        ساخت یک آیتم در Body
        Build a body item from document line
        
        Note: این پیاده‌سازی از AccountingDocumentLine استفاده می‌کند
        که یک ساختار عمومی است. برای اطلاعات دقیق‌تر باید از مدل‌های Sales/Invoice استفاده شود.
        """
        # Get amount from line (use debit or credit, whichever is positive)
        amount = line.debit if line.debit > 0 else line.credit
        if amount <= 0:
            return None  # Skip zero-amount lines
        
        # Default VAT rate (9% is common in Iran)
        vat_rate = Decimal('9.00')
        
        # Calculate amounts
        prdis = amount / (Decimal('1') + vat_rate / Decimal('100'))  # Price before VAT
        vam = amount - prdis  # VAT amount
        
        item = {
            "sstid": str(line.tafsili_account.id) if line.tafsili_account else str(line.id),  # شناسه کالا/خدمات (از tafsili account)
            "sstt": line.description or (line.tafsili_account.account_name if line.tafsili_account else f"آیتم {index + 1}"),  # عنوان
            "mu": "عدد",  # واحد اندازه‌گیری (default)
            "am": Decimal('1.00'),  # مقدار (default 1)
            "fee": prdis,  # مبلغ واحد (قبل از مالیات)
            "cfeeon": "",  # نرخ ارز
            "cut": "",  # نوع ارز
            "exr": Decimal('1.00'),  # نرخ تبدیل ارز
            "prdis": prdis,  # مبلغ قبل از تخفیف
            "dis": Decimal('0.00'),  # مبلغ تخفیف
            "adis": Decimal('0.00'),  # مبلغ تخفیف اضافی
            "vra": vat_rate,  # نرخ مالیات بر ارزش افزوده
            "vam": vam,  # مبلغ مالیات بر ارزش افزوده
            "odt": "",  # نوع عوارض
            "odr": Decimal('0.00'),  # نرخ عوارض
            "odam": Decimal('0.00'),  # مبلغ عوارض
            "olt": "",  # نوع سایر مالیات‌ها
            "olr": Decimal('0.00'),  # نرخ سایر مالیات‌ها
            "olam": Decimal('0.00'),  # مبلغ سایر مالیات‌ها
            "consfee": Decimal('0.00'),  # حق العمل
            "spro": Decimal('0.00'),  # سود
            "bros": Decimal('0.00'),  # بروکری
            "tcpbs": Decimal('0.00'),  # جمع سایر هزینه‌ها
            "cop": Decimal('0.00'),  # جمع قیمت خرید
            "vop": prdis,  # جمع قیمت فروش
            "bsrn": "",  # شماره سریال کالا
            "tsstam": amount,  # جمع مبلغ آیتم (شامل مالیات)
        }
        
        return item
    
    def _build_body(self) -> List[Dict[str, Any]]:
        """
        ساخت Body صورتحساب
        Build invoice body
        """
        body = []
        
        # Get all document lines ordered by line_number
        lines = self.document.lines.all().order_by('line_number')
        
        for idx, line in enumerate(lines):
            item = self._build_body_item(line, idx)
            if item:
                body.append(item)
        
        return body
    
    def _calculate_totals(self, body: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """Calculate invoice totals from body items."""
        cap = Decimal('0.00')  # Total before discount
        insp = Decimal('0.00')  # Total after discount
        tvop = Decimal('0.00')  # Total payments
        tax17 = Decimal('0.00')  # Total VAT
        
        for item in body:
            prdis = Decimal(str(item.get('prdis', 0)))
            dis = Decimal(str(item.get('dis', 0)))
            adis = Decimal(str(item.get('adis', 0)))
            vam = Decimal(str(item.get('vam', 0)))
            
            cap += prdis
            insp += prdis - dis - adis
            tax17 += vam
        
        tvop = insp + tax17  # Total = after discount + VAT
        
        return {
            'cap': cap,
            'insp': insp,
            'tvop': tvop,
            'tax17': tax17
        }
    
    def _build_payment(self) -> List[Dict[str, Any]]:
        """
        ساخت Payment صورتحساب
        Build invoice payment section
        """
        # Placeholder - باید کامل شود
        return []
    
    def _build_voucher(self) -> List[Dict[str, Any]]:
        """
        ساخت Voucher صورتحساب
        Build invoice voucher section
        """
        # Placeholder - باید کامل شود
        return []
    
    def convert(self) -> Dict[str, Any]:
        """
        تبدیل کامل AccountingDocument به فرمت Invoice
        Complete conversion to Invoice format
        
        Returns:
            Dict containing invoice data in Moadian format
        """
        try:
            # Build body first to calculate totals
            body = self._build_body()
            
            # Calculate totals
            totals = self._calculate_totals(body)
            
            # Build header with calculated totals
            header = self._build_header()
            header['cap'] = totals['cap']
            header['insp'] = totals['insp']
            header['tvop'] = totals['tvop']
            header['tax17'] = totals['tax17']
            
            invoice_data = {
                "header": header,
                "body": body,
                "payment": self._build_payment(),
                "voucher": self._build_voucher(),
            }
            
            return invoice_data
        except Exception as e:
            logger.error(f"Error converting document to invoice: {e}")
            raise ValueError(f"خطا در تبدیل سند به صورتحساب: {e}")

