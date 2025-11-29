# لیست کامل Actions برای هر Section

این فایل لیست کامل تمام actions تعریف شده برای هر section در Entity Reference System را نمایش می‌دهد.

## Users (010301 / users)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | `gp=<group_name>` | + پارامترهای فیلتر استاندارد |
| `showown` | - | - |
| `add` | - | - |
| `edit` | `id=<user_id>` | `id=<user_id>`, `code=<user_code>` (اختیاری) |
| `delete` | `id=<user_id>` | `id=<user_id>`, `code=<user_code>` (اختیاری) |

## Groups (010302 / groups)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | ⚠️ **هنوز در migration تعریف نشده** |
| `add` | - | ⚠️ **هنوز در migration تعریف نشده** |
| `edit` | - | ⚠️ **هنوز در migration تعریف نشده** - باید `id=<group_id>`, `code=<group_code>` (اختیاری) |
| `delete` | - | ⚠️ **هنوز در migration تعریف نشده** - باید `id=<group_id>`, `code=<group_code>` (اختیاری) |

## Access Levels (010303 / access_levels)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | ⚠️ **هنوز در migration تعریف نشده** |
| `add` | - | ⚠️ **هنوز در migration تعریف نشده** |
| `edit` | - | ⚠️ **هنوز در migration تعریف نشده** - باید `id=<access_level_id>`, `code=<access_level_code>` (اختیاری) |
| `delete` | - | ⚠️ **هنوز در migration تعریف نشده** - باید `id=<access_level_id>`, `code=<access_level_code>` (اختیاری) |

## Purchase Requests (020400 / purchase_requests)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد + `status` |
| `add` | - | - |
| `edit` | `id=<request_id>` | `id=<request_id>`, `code=<request_code>` (اختیاری) |
| `approve` | `id=<request_id>`, `code=<request_code>` | بدون تغییر |
| `create_receipt_from` | `id=<request_id>`, `type=<temporary\|permanent\|consignment>` | بدون تغییر |

## Warehouse Requests (020500 / warehouse_requests)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد + `status` |
| `add` | - | - |
| `edit` | `id=<request_id>` | `id=<request_id>`, `code=<request_code>` (اختیاری) |
| `approve` | `id=<request_id>`, `code=<request_code>` | بدون تغییر |
| `create_issue_from` | `id=<request_id>`, `type=<permanent\|consumption\|consignment>` | بدون تغییر |

## Receipts - Temporary (020601 / receipt_temporary)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد + `qc_status`, `qc_approved`, `qc_rejected`, `qc_pending` |
| `add` | - | - |
| `edit` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |
| `delete` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |
| `lock` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |
| `send_to_qc` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |

## Receipts - Permanent (020602 / receipt_permanent)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد |
| `add` | - | - |
| `edit` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |
| `delete` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |
| `lock` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |

## Receipts - Consignment (020603 / receipt_consignment)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد |
| `add` | - | - |
| `edit` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |
| `delete` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |
| `lock` | `id=<receipt_id>` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) |

## Issues - Permanent (020701 / issue_permanent)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد |
| `add` | - | - |
| `edit` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |
| `delete` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |
| `lock` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |

## Issues - Consumption (020702 / issue_consumption)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد |
| `add` | - | - |
| `edit` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |
| `delete` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |
| `lock` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |

## Issues - Consignment (020703 / issue_consignment)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد |
| `add` | - | - |
| `edit` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |
| `delete` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |
| `lock` | `id=<issue_id>` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) |

## Inspections (041000 / inspections)

| Action | Parameters (فعلی) | Parameters (پیشنهادی) |
|--------|-------------------|----------------------|
| `show` | - | + پارامترهای فیلتر استاندارد |
| `showown` | - | - |
| `approve` | `id=<inspection_id>`, `code=<inspection_code>` | بدون تغییر |
| `reject` | `id=<inspection_id>`, `code=<inspection_code>` | بدون تغییر |

---

## نکات مهم:

### 1. پارامتر `code` برای Actions `edit`, `delete`, `lock`:

برای همه actions که نیاز به شناسایی سند دارند (`edit`, `delete`, `lock`، و غیره)، باید پارامتر `code` به عنوان جایگزین یا مکمل `id` اضافه شود:

- **`id`**: شناسه عددی (integer)
- **`code`**: کد عمومی سند (string) - اختیاری

**مثال:**
```python
'edit': {
    'id': {'type': 'integer', 'required': True, 'description': 'Document ID'},
    'code': {'type': 'string', 'required': False, 'description': 'Document code (alternative to id)'}
}
```

### 2. پارامترهای دریافت شده از سند (Document Context):

برای actions که در context یک سند اجرا می‌شوند (مثل approve، reject، lock)، می‌توان از پارامترهای زیر استفاده کرد:

- `{document.id}` - شناسه سند
- `{document.code}` - کد سند
- `{document.created_by}` - شناسه سازنده
- `{document.status}` - وضعیت سند
- و سایر فیلدهای سند

این پارامترها در زمان اجرای action از context سند دریافت می‌شوند (بعداً توضیح داده خواهد شد).

### 3. Actions اضافه نشده:

بسیاری از sections هنوز actions ندارند. باید برای آن‌ها نیز actions اضافه شود:

- **Master Data Sections** (item_types, item_categories, warehouses, etc.)
- **Production Sections** (personnel, machines, work_lines, bom, processes, product_orders, etc.)
- **Stocktaking Sections** (stocktaking_deficit, stocktaking_surplus, stocktaking_records)

### 4. پارامترهای فیلتر برای `show` actions:

همه `show` actions باید پارامترهای فیلتر استاندارد را داشته باشند (approved, rejected, locked, today, last_week, created_by_me, created).

