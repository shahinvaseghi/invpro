"""
Invoice Converter Service
سرویس تبدیل AccountingDocument به فرمت Invoice سامانه مودیان
"""
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
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
        
        header = {
            "taxid": tax_id,
            "indatim": indatim,  # تاریخ صورتحساب (YYYYMMDD)
            "indati2m": indati2m,  # Timestamp
            "inty": 1,  # نوع صورتحساب (1=فروش، 2=خرید، ...)
            "inno": self._generate_invoice_number(),
            "irtaxid": tax_id,  # شناسه مالیاتی فروشنده
            "inp": 1,  # الگوی صورتحساب
            "ins": 1,  # موضوع صورتحساب
            "tins": "",  # شناسه مالیاتی خریدار (اگر خالی باشد، حقیقی است)
            "tob": "",  # نوع شخص خریدار
            "bid": "",  # شناسه ملی/اقتصادی خریدار
            "tinb": "",  # شناسه مالیاتی خریدار
            "sbc": "",  # کد پستی خریدار
            "bpc": "",  # کد پستی خریدار
            "bpn": "",  # نام خریدار
            "bpb": "",  # نام خانوادگی/نام شرکت خریدار
            "bcb": "",  # نام تجاری خریدار
            "bbs": "",  # استان خریدار
            "bci": "",  # شهر خریدار
            "cap": Decimal('0.00'),  # مبلغ کل قبل از تخفیف
            "insp": Decimal('0.00'),  # مبلغ کل بعد از تخفیف
            "tvop": Decimal('0.00'),  # جمع کل پرداخت‌ها
            "tax17": Decimal('0.00'),  # مالیات بر ارزش افزوده
            "taxid": tax_id,
        }
        
        return header
    
    def _build_body_item(self, line, index: int) -> Optional[Dict[str, Any]]:
        """
        ساخت یک آیتم در Body
        Build a body item from document line
        
        Note: این متد نیاز به اطلاعات کامل‌تری دارد که باید از مدل‌های دیگر استخراج شود
        """
        # این یک پیاده‌سازی ساده است
        # در عمل باید اطلاعات کالا/خدمات از مدل‌های دیگر استخراج شود
        
        # Placeholder - باید کامل شود
        item = {
            "sstid": "",  # شناسه کالا/خدمات
            "sstt": "",  # عنوان کالا/خدمات
            "mu": "",  # واحد اندازه‌گیری
            "am": Decimal('0.00'),  # مقدار
            "fee": Decimal('0.00'),  # مبلغ واحد
            "cfeeon": "",  # نرخ ارز
            "cut": "",  # نوع ارز
            "exr": Decimal('1.00'),  # نرخ تبدیل ارز
            "prdis": Decimal('0.00'),  # مبلغ قبل از تخفیف
            "dis": Decimal('0.00'),  # مبلغ تخفیف
            "adis": Decimal('0.00'),  # مبلغ تخفیف اضافی
            "vra": Decimal('0.00'),  # نرخ مالیات بر ارزش افزوده
            "vam": Decimal('0.00'),  # مبلغ مالیات بر ارزش افزوده
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
            "vop": Decimal('0.00'),  # جمع قیمت فروش
            "bsrn": "",  # شماره سریال کالا
            "tsstam": Decimal('0.00'),  # جمع مبلغ آیتم
        }
        
        return item
    
    def _build_body(self) -> List[Dict[str, Any]]:
        """
        ساخت Body صورتحساب
        Build invoice body
        """
        body = []
        
        # این بخش نیاز به اطلاعات کامل‌تری دارد
        # باید از document lines یا مدل‌های مرتبط (مثل SalesInvoice) استفاده شود
        
        # Placeholder - باید کامل شود
        for idx, line in enumerate(self.document.lines.all()[:10]):  # محدود به 10 خط برای نمونه
            item = self._build_body_item(line, idx)
            if item:
                body.append(item)
        
        return body
    
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
            invoice_data = {
                "header": self._build_header(),
                "body": self._build_body(),
                "payment": self._build_payment(),
                "voucher": self._build_voucher(),
            }
            
            return invoice_data
        except Exception as e:
            logger.error(f"Error converting document to invoice: {e}")
            raise ValueError(f"خطا در تبدیل سند به صورتحساب: {e}")

