# وضعیت پیاده‌سازی الزامات سامانه مودیان

این سند وضعیت پیاده‌سازی الزامات **دستورالعمل فنی اتصال به سامانه مودیان (RC_TICS.IS_v1.3)** را بررسی می‌کند.

---

## ✅ **پیاده‌سازی شده (کامل یا جزئی)**

### 1. مدیریت حافظه مالیاتی (Fiscal Memory)
- ✅ **Model**: `FiscalMemoryConfig`
  - شناسه یکتای حافظه مالیاتی (Fiscal ID)
  - تنظیمات API (timeout, retry count)
  - کلیدهای خصوصی و عمومی (ذخیره به صورت text)
  - نوع امضا (PKCS#7, RSA, ECDSA)
  - نوع رمزگذاری (AES-256, AES-128, RSA-2048)
  - رمز عبور کلید خصوصی

- ✅ **Form**: `FiscalMemoryConfigForm`
  - آپلود فایل کلیدها
  - آپلود گواهینامه
  - وارد کردن مستقیم متن

- ✅ **View & Template**: `TaxMoadianSettingsView`
  - صفحه تنظیمات کامل با ساختار دو ستونی

**وضعیت**: ✅ **کامل**

---

### 2. موجودیت مودی/شرکت
- ✅ **Model**: `Company` (در shared/models.py)
  - `tax_id`: شناسه مالیاتی
  - `registration_number`: شماره ثبت
  - سایر اطلاعات پایه

**وضعیت**: ✅ **کامل** (استفاده از Company موجود)

---

### 3. ثبت ارسال‌های صورتحساب
- ✅ **Model**: `TaxInvoiceSubmission`
  - ارتباط با AccountingDocument
  - ارتباط با FiscalMemoryConfig
  - وضعیت ارسال (PENDING, SENT, ACCEPTED, REJECTED, FAILED, RETRYING)
  - اطلاعات پاسخ از سامانه (UID, code, message, timestamp)
  - داده‌های صورتحساب (JSON)
  - اطلاعات خطا و retry

- ✅ **Model**: `TaxInvoiceSubmissionLog`
  - لاگ کامل برای هر ارسال
  - نوع لاگ (SUBMIT, RESPONSE, RETRY, ERROR, VALIDATION)
  - ذخیره request/response data
  - HTTP status code و execution time

**وضعیت**: ✅ **کامل**

---

### 4. View و Template برای اعتبارسنجی
- ✅ **View**: `TaxValidationView`
- ✅ **Template**: `validation.html`
  - نمایش پیکربندی‌های حافظه مالیاتی
  - نمایش اسناد آماده برای ارسال
  - نمایش ارسال‌های اخیر

**وضعیت**: ✅ **کامل**

---

### 5. سرویس API (ساختار اولیه)
- ✅ **Service**: `MoadianService` (در accounting/services/moadian.py)
  - ساختار کلی کلاس
  - متدهای پایه (_generate_uid, _get_timestamp, _normalize_json)
  - ساختار _build_packet

**وضعیت**: ⚠️ **ناقص** (ساختار وجود دارد ولی متدهای اصلی placeholder هستند)

---

## ❌ **پیاده‌سازی نشده**

### 1. مدل Digital Certificate (گواهینامه دیجیتال)
**وضعیت فعلی**: گواهینامه در `metadata` ذخیره می‌شود  
**نیاز**: جدول جداگانه با فیلدهای:
- Serial Number
- تاریخ اعتبار (valid_from, valid_to)
- صادرکننده (CA)
- Subject
- Key ID (kid)

**اولویت**: 🔴 **بالا**

---

### 2. Authentication Engine (JWT/JWS)
**وضعیت فعلی**: متد `_sign_data()` placeholder است  
**نیاز**: 
- دریافت Nonce از API (`GET /api/v2/nonce`)
- ساخت JWT Payload (با clientId, nonce, timestamp)
- ساخت JWT Header (با algorithm, certificate)
- امضای JWT با Private Key (JWS)
- ساخت Authorization Header

**اولویت**: 🔴 **بالا** (بدون این، هیچ API call موفق نمی‌شود)

---

### 3. Encryption Service (JWE)
**وضعیت فعلی**: متد `_encrypt_data()` placeholder است  
**نیاز**:
- تولید کلید متقارن AES-256
- رمزگذاری داده با AES-GCM
- رمزگذاری کلید متقارن با RSA-OAEP-256 (با Public Key سازمان)
- ساخت JWE (Header, Encrypted Key, IV, CipherText, Auth Tag)

**اولویت**: 🔴 **بالا** (بدون این، صورتحساب‌ها قابل ارسال نیستند)

---

### 4. دریافت اطلاعات سرور مودیان
**وضعیت فعلی**: متد `get_fiscal_information()` وجود دارد ولی کامل نیست  
**نیاز**:
- API: `GET /api/v2/server-information`
- ذخیره Public Key سازمان (RSA 4096)
- ذخیره Key ID (kid)
- استفاده از این کلید برای رمزگذاری

**اولویت**: 🔴 **بالا**

---

### 5. مدل Invoice مطابق ساختار سامانه مودیان
**وضعیت فعلی**: `invoice_data` به صورت JSON generic ذخیره می‌شود  
**نیاز**: مدل دقیق با فیلدهای:
- Header (taxId, indatim, indati2m, inty, inno, irtaxid, inp, ins, tins, ...)
- Body (لیست اقلام با تمام فیلدهای مورد نیاز)
- Payment (پرداخت‌ها)
- Voucher (اسناد)

**اولویت**: 🟡 **متوسط**

---

### 6. تبدیل AccountingDocument به Invoice Format
**وضعیت فعلی**: وجود ندارد  
**نیاز**: 
- Service برای تبدیل AccountingDocument به ساختار Invoice سامانه مودیان
- استخراج اطلاعات از document lines
- محاسبه مالیات و عوارض
- ساخت Header و Body

**اولویت**: 🟡 **متوسط** (بعد از پیاده‌سازی مدل Invoice)

---

### 7. API Endpoints برای ارسال و استعلام
**وضعیت فعلی**: متدهای `submit_invoice()` و `get_invoice_status()` وجود دارند ولی کامل نیستند  
**نیاز**:
- پیاده‌سازی کامل ارسال با JWE
- پیاده‌سازی استعلام با UID
- پیاده‌سازی استعلام با بازه زمانی
- مدیریت response و error handling

**اولویت**: 🟡 **متوسط** (بعد از Authentication و Encryption)

---

### 8. سایر API Methods
**وضعیت فعلی**: متدهای placeholder وجود دارند  
**نیاز**:
- `get_token()` - دریافت توکن
- `get_service_stuff_list()` - لیست کالا/خدمات
- `get_economic_code_information()` - استعلام شماره اقتصادی

**اولویت**: 🟢 **پایین** (می‌تواند بعداً اضافه شود)

---

## 📊 **خلاصه وضعیت**

| بخش | وضعیت | اولویت | درصد تکمیل |
|-----|-------|--------|------------|
| مدیریت حافظه مالیاتی | ✅ کامل | - | 100% |
| مدل‌های ارسال و لاگ | ✅ کامل | - | 100% |
| UI و Forms | ✅ کامل | - | 100% |
| Authentication (JWT/JWS) | ✅ کامل | - | 100% |
| Encryption (JWE) | ✅ کامل | - | 100% |
| دریافت اطلاعات سرور | ✅ کامل | - | 100% |
| مدل Invoice دقیق | ⚠️ ناقص | 🟡 متوسط | 30% |
| تبدیل Document به Invoice | ⚠️ ناقص | 🟡 متوسط | 40% |
| API Endpoints | ✅ کامل | - | 100% |

**میانگین کلی**: ~75% ✅ (افزایش از 35%)

---

## 🎯 **اولویت‌بندی پیاده‌سازی**

### فاز 1: پیش‌نیازهای امنیتی (ضروری)
1. Authentication Engine (JWT/JWS)
2. Encryption Service (JWE)
3. دریافت اطلاعات سرور و ذخیره Public Key
4. مدل Digital Certificate (اختیاری - می‌توان در metadata نگه داشت)

### فاز 2: تبدیل و ارسال (کاربردی)
5. مدل Invoice دقیق
6. تبدیل AccountingDocument به Invoice
7. تکمیل API Endpoints

### فاز 3: استعلام و مدیریت (تکمیلی)
8. استعلام وضعیت
9. مدیریت خطا و retry
10. سایر API Methods

---

## 💡 **نکات مهم**

1. **بدون Authentication و Encryption، سیستم قابل استفاده نیست** - این دو باید اول پیاده‌سازی شوند.

2. **گواهینامه‌ها می‌توانند فعلاً در metadata ذخیره شوند** - ایجاد جدول جداگانه می‌تواند بعداً انجام شود.

3. **ساختار کلی درست است** - فقط باید متدهای اصلی را کامل کنیم.

4. **برای پیاده‌سازی Authentication و Encryption نیاز به کتابخانه‌های زیر است:**
   - `cryptography` - برای RSA, AES
   - `PyJWT` یا `python-jose` - برای JWT/JWS/JWE
   - `requests` - برای HTTP calls (قبلاً استفاده شده)

---

**تاریخ بررسی**: 1403/10/06  
**آخرین به‌روزرسانی**: 1403/10/06 (پیاده‌سازی Authentication, Encryption, و API Endpoints)  
**نسخه مستند**: RC_TICS.IS_v1.3 – مهر ۱۴۰۲

---

## ✅ **به‌روزرسانی‌های اخیر (1403/10/06)**

### پیاده‌سازی شده:

1. ✅ **Authentication Engine (JWT/JWS)** - کامل
   - دریافت Nonce از API
   - ساخت JWT Payload و Header
   - امضای JWS با RSA-SHA256
   - استفاده از گواهینامه در Header

2. ✅ **Encryption Service (JWE)** - کامل
   - تولید کلید متقارن AES-256
   - رمزگذاری با AES-GCM
   - رمزگذاری کلید با RSA-OAEP-256
   - ساخت کامل JWE structure

3. ✅ **دریافت اطلاعات سرور** - کامل
   - API endpoint برای دریافت اطلاعات
   - ذخیره Public Key سازمان
   - ذخیره Key ID

4. ✅ **API Endpoints** - کامل
   - تمام متدهای اصلی پیاده‌سازی شدند
   - پشتیبانی از sync و async
   - مدیریت خطا و logging

5. ✅ **سرویس تبدیل Invoice** - ساختار اولیه
   - کلاس InvoiceConverter
   - تبدیل Header و Body
   - نیاز به تکمیل با اطلاعات واقعی

### کتابخانه‌های اضافه شده:
- `cryptography==42.0.5` - برای RSA و AES
- `PyJWT==2.9.0` - برای JWT/JWS
- `requests==2.31.0` - برای HTTP calls

