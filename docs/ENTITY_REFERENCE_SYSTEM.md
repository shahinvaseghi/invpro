# Entity Reference System Documentation

## Overview

This document describes the **Entity Reference System** - a centralized action registry system that allows any part of the application to reference and execute actions from other modules using a standardized syntax. This system enables automation, dynamic workflows, and cross-module integrations throughout the entire platform.

## Code Structure

Each section/feature in the application has a **6-digit code** following this pattern:

```
XX YY ZZ
│  │  │
│  │  └─ Submenu number (2 digits)
│  └──── Menu number (2 digits)
└──────── Module number (2 digits)
```

### Module Numbers

- `00` - Dashboard/UI
- `01` - Shared
- `02` - Inventory
- `03` - Production
- `04` - Quality Control (QC)
- `05` - Ticketing (future)

---

## Module Registry

### Module 00 - Dashboard/UI

| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `000000` | `dashboard` | Dashboard | Main dashboard page |

---

### Module 01 - Shared

| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `010000` | `companies` | Companies | Company management |
| `010100` | `company_units` | Company Units | Organizational units |
| `010200` | `smtp_servers` | SMTP Servers | Email server configuration |

#### Users Menu (01 03 XX)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `010301` | `users` | Users | User management |
| `010302` | `access_levels` | Access Levels | Access level management |
| `010303` | `groups` | Groups | User groups |

---

### Module 02 - Inventory

#### Master Data Menu (02 01 XX)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `020101` | `item_types` | Item Types | Item type management |
| `020102` | `item_categories` | Item Categories | Item category management |
| `020103` | `item_subcategories` | Item Subcategories | Item subcategory management |
| `020104` | `warehouses` | Warehouses | Warehouse management |

#### Items Menu (02 02 XX)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `020201` | `items_create` | Create Item | Create new item |
| `020202` | `items` | Edit Items | Item list/edit |
| `020203` | `item_serials` | Item Serials | Serial number management |
| `020204` | `inventory_balance` | Inventory Balance | Inventory balance reports |

#### Suppliers Menu (02 03 XX)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `020301` | `supplier_categories` | Supplier Categories | Supplier category management |
| `020302` | `suppliers` | Supplier List | Supplier management |

#### Requests (Menu 04-05)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `020400` | `purchase_requests` | Purchase Requests | Purchase request management |
| `020500` | `warehouse_requests` | Warehouse Requests | Warehouse request management |

#### Receipts Menu (Menu 06)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `020601` | `receipt_temporary` | Temporary Receipts | Temporary receipt documents |
| `020602` | `receipt_permanent` | Permanent Receipts | Permanent receipt documents |
| `020603` | `receipt_consignment` | Consignment Receipts | Consignment receipt documents |

#### Issues Menu (Menu 07)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `020701` | `issue_permanent` | Permanent Issues | Permanent issue documents |
| `020702` | `issue_consumption` | Consumption Issues | Consumption issue documents |
| `020703` | `issue_consignment` | Consignment Issues | Consignment issue documents |

#### Stocktaking Menu (Menu 08)
| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `020801` | `stocktaking_deficit` | Deficit Records | Stocktaking deficit records |
| `020802` | `stocktaking_surplus` | Surplus Records | Stocktaking surplus records |
| `020803` | `stocktaking_records` | Stocktaking Records | Stocktaking confirmation records |

---

### Module 03 - Production

| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `030000` | `personnel` | Personnel | Personnel management |
| `030100` | `machines` | Machines | Machine management |
| `030200` | `work_lines` | Work Lines | Work line management |
| `030300` | `bom` | BOM | Bill of Materials |
| `030400` | `processes` | Processes | Process definitions |
| `036000` | `product_orders` | Product Orders | Production order management |
| `036100` | `transfer_requests` | Transfer to Line Requests | Transfer request management |
| `036800` | `performance_records` | Performance Records | Performance record management |

---

### Module 04 - Quality Control (QC)

| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `041000` | `inspections` | Inspections | QC inspection management (Temporary Receipts) |

---

### Module 05 - Ticketing

| Code | Nickname | Name | Description |
|------|----------|------|-------------|
| `050000` | `tickets` | Tickets | Ticket management |
| `050100` | `ticket_categories` | Ticket Categories | Ticket category management |
| `050200` | `ticket_templates` | Ticket Templates | Ticket template management |
| `050300` | `ticket_subcategories` | Ticket Subcategories | Ticket subcategory management |

---

## Action Syntax

Actions are referenced using the following syntax:

```
<code_or_nickname>:<action>:<parameters>
```

### Examples:

```
users:show:gp=superuser
010301:show:gp=superuser
0270:approve:code="PR-20250115-000001"
purchase_requests:approve:code={ticket.reference_code}
```

---

## Action Definitions

Each section can define multiple actions. Actions are defined per section with their parameters and permissions.

### Users (010301 / users)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `gp=<group_name>` | Show users from specific group |
| `showown` | - | Show own user profile |
| `add` | - | Add new user |
| `edit` | `id=<user_id>`, `code=<user_code>` (اختیاری) | Edit user - can use either id or code |
| `delete` | `id=<user_id>`, `code=<user_code>` (اختیاری) | Delete user - can use either id or code |
| `disable` | `id=<user_id>`, `code=<user_code>` (اختیاری) | Disable user - can use either id or code |
| `enable` | `id=<user_id>`, `code=<user_code>` (اختیاری) | Enable user - can use either id or code |

### Groups (010302 / groups)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show user groups |
| `add` | - | Create new group |
| `edit` | `id=<group_id>`, `code=<group_code>` (اختیاری) | Edit group - can use either id or code |
| `delete` | `id=<group_id>`, `code=<group_code>` (اختیاری) | Delete group - can use either id or code |

### Access Levels (010303 / access_levels)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show access levels |
| `add` | - | Create new access level |
| `edit` | `id=<access_level_id>`, `code=<access_level_code>` (اختیاری) | Edit access level - can use either id or code |
| `delete` | `id=<access_level_id>`, `code=<access_level_code>` (اختیاری) | Delete access level - can use either id or code |

### Purchase Requests (020400 / purchase_requests)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<pending\|approved\|rejected\|locked\|all>` | Show purchase requests with optional filters |
| `add` | - | Create new purchase request |
| `edit` | `id=<request_id>`, `code=<request_code>` (اختیاری) | Edit purchase request - can use either id or code |
| `approve` | `id=<request_id>`, `code=<request_code>` (اختیاری) | Approve purchase request - can use either id or code |
| `create_receipt_from` | `id=<request_id>`, `type=<temporary\|permanent\|consignment>` | Create receipt from approved purchase request |

**Special Actions:**
- **`create_receipt_from`**: This action allows creating receipt documents (temporary, permanent, or consignment) directly from an approved purchase request. The system will open an intermediate selection page where users can adjust quantities and add notes before creating the final receipt document.

### Warehouse Requests (020500 / warehouse_requests)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<pending\|approved\|rejected\|locked\|all>` | Show warehouse requests with optional filters |
| `add` | - | Create new warehouse request |
| `edit` | `id=<request_id>`, `code=<request_code>` (اختیاری) | Edit warehouse request - can use either id or code |
| `approve` | `id=<request_id>`, `code=<request_code>` (اختیاری) | Approve warehouse request - can use either id or code |
| `create_issue_from` | `id=<request_id>`, `type=<permanent\|consumption\|consignment>` | Create issue from approved warehouse request |

**Special Actions:**
- **`create_issue_from`**: This action allows creating issue documents (permanent, consumption, or consignment) directly from an approved warehouse request. Similar to receipt creation, the system provides an intermediate selection page for quantity adjustment and notes before creating the final issue document.

### Receipts

#### Temporary Receipts (020601 / receipt_temporary)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `unlocked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `qc_status=<pending\|approved\|rejected\|not_sent>`, `qc_approved=<yes\|no\|all>`, `qc_rejected=<yes\|no\|all>`, `qc_pending=<yes\|no\|all>`, `status=<draft\|locked\|qc_pending\|qc_approved\|qc_rejected\|all>` | Show temporary receipts with optional filters |
| `add` | - | Create new temporary receipt |
| `edit` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Edit temporary receipt - can use either id or code |
| `delete` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Delete temporary receipt - can use either id or code |
| `lock` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Lock temporary receipt - can use either id or code |
| `send_to_qc` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Send temporary receipt to QC for inspection - can use either id or code |

#### Permanent Receipts (020602 / receipt_permanent)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `unlocked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<draft\|locked\|all>` | Show permanent receipts with optional filters |
| `add` | - | Create new permanent receipt |
| `edit` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Edit permanent receipt - can use either id or code |
| `delete` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Delete permanent receipt - can use either id or code |
| `lock` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Lock permanent receipt - can use either id or code |

#### Consignment Receipts (020603 / receipt_consignment)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `unlocked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<draft\|locked\|all>` | Show consignment receipts with optional filters |
| `add` | - | Create new consignment receipt |
| `edit` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Edit consignment receipt - can use either id or code |
| `delete` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Delete consignment receipt - can use either id or code |
| `lock` | `id=<receipt_id>`, `code=<receipt_code>` (اختیاری) | Lock consignment receipt - can use either id or code |

### Issues

#### Permanent Issues (020701 / issue_permanent)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `unlocked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<draft\|locked\|all>` | Show permanent issues with optional filters |
| `add` | - | Create new permanent issue |
| `edit` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Edit permanent issue - can use either id or code |
| `delete` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Delete permanent issue - can use either id or code |
| `lock` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Lock permanent issue - can use either id or code |

#### Consumption Issues (020702 / issue_consumption)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `unlocked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<draft\|locked\|all>` | Show consumption issues with optional filters |
| `add` | - | Create new consumption issue |
| `edit` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Edit consumption issue - can use either id or code |
| `delete` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Delete consumption issue - can use either id or code |
| `lock` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Lock consumption issue - can use either id or code |

#### Consignment Issues (020703 / issue_consignment)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `unlocked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<draft\|locked\|all>` | Show consignment issues with optional filters |
| `add` | - | Create new consignment issue |
| `edit` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Edit consignment issue - can use either id or code |
| `delete` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Delete consignment issue - can use either id or code |
| `lock` | `id=<issue_id>`, `code=<issue_code>` (اختیاری) | Lock consignment issue - can use either id or code |

### Inspections (041000 / inspections)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | `approved=<yes\|no\|all>`, `rejected=<yes\|no\|all>`, `locked=<yes\|no\|all>`, `unlocked=<yes\|no\|all>`, `today=<yes\|no>`, `last_week=<yes\|no>`, `created_by_me=<yes\|no>`, `created=<today\|week\|month\|all>`, `status=<pending\|approved\|rejected\|all>` | Show inspections with optional filters |
| `showown` | - | Show own inspections |
| `approve` | `id=<inspection_id>`, `code=<inspection_code>` | Approve inspection |
| `reject` | `id=<inspection_id>`, `code=<inspection_code>` | Reject inspection |

---

### Ticketing

#### Tickets (050000 / tickets)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show tickets |
| `showown` | - | Show own tickets |
| `create` | `template_id=<template_id>`, `category_id=<category_id>` | Create new ticket |
| `respond` | `id=<ticket_id>`, `code=<ticket_code>` | Respond to ticket |
| `close` | `id=<ticket_id>`, `code=<ticket_code>` | Close ticket |
| `reopen` | `id=<ticket_id>`, `code=<ticket_code>` | Reopen closed ticket |

#### Ticket Categories (050100 / ticket_categories)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show ticket categories |
| `add` | - | Create new category |
| `edit` | `id=<category_id>` | Edit category |
| `delete` | `id=<category_id>` | Delete category |

#### Ticket Templates (050200 / ticket_templates)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show ticket templates |
| `add` | - | Create new template |
| `edit` | `id=<template_id>` | Edit template |
| `delete` | `id=<template_id>` | Delete template |

#### Ticket Subcategories (050300 / ticket_subcategories)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show ticket subcategories |
| `add` | - | Create new subcategory |
| `edit` | `id=<subcategory_id>` | Edit subcategory |
| `delete` | `id=<subcategory_id>` | Delete subcategory |

---

## Parameter Types

Parameters can be:

1. **Literal values**: `gp=superuser`
2. **From ticket context**: `code={ticket.reference_code}`
3. **From current context**: `user={current_user.id}`
4. **From document context**: `code={document.code}`, `id={document.id}`, `created_by={document.created_by}`

---

## Document Context Parameters

برای actions که در context یک سند اجرا می‌شوند (مثل approve، reject، lock، edit)، می‌توان از پارامترهای زیر استفاده کرد که از خود سند دریافت می‌شوند:

### پارامترهای قابل استفاده در Document Context:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `{document.id}` | integer | شناسه عددی سند | `id={document.id}` |
| `{document.code}` | string | کد عمومی سند | `code={document.code}` |
| `{document.created_by}` | integer | شناسه سازنده سند | `created_by={document.created_by}` |
| `{document.status}` | string | وضعیت سند | `status={document.status}` |
| `{document.company_id}` | integer | شناسه شرکت | `company_id={document.company_id}` |

### استفاده از Document Context Parameters:

این پارامترها زمانی استفاده می‌شوند که action در context یک سند خاص اجرا می‌شود. به عنوان مثال:

```
# در context یک ticket
purchase_requests:edit:code={ticket.reference_code}
receipt_temporary:approve:id={document.id}
warehouse_requests:lock:code={document.code}
```

**نکته مهم**: این پارامترها باید در زمان اجرای action resolve شوند و به مقادیر واقعی تبدیل شوند.

---

## Complete Actions List by Section

این بخش لیست کامل تمام actions تعریف شده برای هر section را نمایش می‌دهد. برای جزئیات کامل پارامترها، به بخش [Action Definitions](#action-definitions) مراجعه کنید.

| Section | Section Code | Actions |
|---------|--------------|---------|
| **Users** | 010301 | `show`, `showown`, `add`, `edit`, `delete` |
| **Groups** | 010302 | `show`, `add`, `edit`, `delete` |
| **Access Levels** | 010303 | `show`, `add`, `edit`, `delete` |
| **Purchase Requests** | 020400 | `show`, `add`, `edit`, `approve`, `create_receipt_from` |
| **Warehouse Requests** | 020500 | `show`, `add`, `edit`, `approve`, `create_issue_from` |
| **Receipts - Temporary** | 020601 | `show`, `add`, `edit`, `delete`, `lock`, `send_to_qc` |
| **Receipts - Permanent** | 020602 | `show`, `add`, `edit`, `delete`, `lock` |
| **Receipts - Consignment** | 020603 | `show`, `add`, `edit`, `delete`, `lock` |
| **Issues - Permanent** | 020701 | `show`, `add`, `edit`, `delete`, `lock` |
| **Issues - Consumption** | 020702 | `show`, `add`, `edit`, `delete`, `lock` |
| **Issues - Consignment** | 020703 | `show`, `add`, `edit`, `delete`, `lock` |
| **Inspections** | 041000 | `show`, `showown`, `approve`, `reject` |

**نکات مهم:**
- برای جزئیات کامل actions و پارامترهای آن‌ها، به بخش [Action Definitions](#action-definitions) مراجعه کنید
- لیست کامل با جزئیات بیشتر در فایل `docs/ACTIONS_LIST.md` موجود است
- برای actions `edit`, `delete`, `lock` و سایر actions که نیاز به شناسایی سند دارند، می‌توان از `id` یا `code` استفاده کرد (پارامتر `code` اختیاری است)

---

## Standard Filter Parameters for "show" Actions

This section defines standard filter parameters that should be available for all "show" (list/view) actions across different sections. These parameters allow users to filter results based on common criteria.

**Important**: 
- ⚠️ **این پارامترها هنوز فقط در مستندات تعریف شده‌اند** و باید به `parameter_schema` در `ActionRegistry` اضافه شوند.
- باید migration ایجاد شود تا این پارامترها به دیتابیس اضافه شوند.
- وقتی این پارامترها در Entity Reference UI استفاده می‌شوند، به صورت خودکار به dropdown/checkbox تبدیل می‌شوند.

### Common Filter Parameters (Available for All Sections)

These parameters can be used with any section's `show` action:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `approved` | enum | `yes`, `no`, `all` | Filter by approval status |
| `rejected` | enum | `yes`, `no`, `all` | Filter by rejection status |
| `locked` | enum | `yes`, `no`, `all` | Filter by lock status |
| `unlocked` | enum | `yes`, `no`, `all` | Filter by unlock status (inverse of locked) |
| `last_week` | enum | `yes`, `no` | Show items from the last 7 days |
| `today` | enum | `yes`, `no` | Show items created today |
| `created_by_me` | enum | `yes`, `no` | Show items created by current user |
| `created` | enum | `today`, `week`, `month`, `all` | Filter by creation date range |

**Note**: `approved` and `rejected` are mutually exclusive. `locked` and `unlocked` are mutually exclusive.

### Section-Specific Filter Parameters

#### Purchase Requests (020400 / purchase_requests)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `pending`, `approved`, `rejected`, `locked`, `all` | Filter by request status |

#### Warehouse Requests (020500 / warehouse_requests)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `pending`, `approved`, `rejected`, `locked`, `all` | Filter by request status |

#### Temporary Receipts (020601 / receipt_temporary)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `draft`, `locked`, `qc_pending`, `qc_approved`, `qc_rejected`, `all` | Filter by receipt status |
| `qc_status` | enum | `pending`, `approved`, `rejected`, `not_sent` | Filter by QC inspection status |
| `qc_approved` | enum | `yes`, `no`, `all` | Show QC-approved receipts |
| `qc_rejected` | enum | `yes`, `no`, `all` | Show QC-rejected receipts |
| `qc_pending` | enum | `yes`, `no`, `all` | Show receipts pending QC inspection |

**Special Parameters for Temporary Receipts:**
- `qc_status`: Combined QC status filter
  - `pending`: Sent to QC but not yet inspected
  - `approved`: QC inspection approved
  - `rejected`: QC inspection rejected
  - `not_sent`: Not yet sent to QC
- Individual QC filters (`qc_approved`, `qc_rejected`, `qc_pending`) can be used instead

#### Permanent Receipts (020602 / receipt_permanent)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `draft`, `locked`, `all` | Filter by receipt status |

#### Consignment Receipts (020603 / receipt_consignment)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `draft`, `locked`, `all` | Filter by receipt status |

#### Permanent Issues (020701 / issue_permanent)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `draft`, `locked`, `all` | Filter by issue status |

#### Consumption Issues (020702 / issue_consumption)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `draft`, `locked`, `all` | Filter by issue status |

#### Consignment Issues (020703 / issue_consignment)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `draft`, `locked`, `all` | Filter by issue status |

#### Inspections (041000 / inspections)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `status` | enum | `pending`, `approved`, `rejected`, `all` | Filter by inspection status |

#### BOM (Bill of Materials) (030300 / bom)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `approved` | enum | `yes`, `no`, `all` | Filter by approval status |
| `rejected` | enum | `yes`, `no`, `all` | Filter by rejection status |
| `locked` | enum | `yes`, `no`, `all` | Filter by lock status |
| `today` | enum | `yes`, `no` | Show items created today |
| `last_week` | enum | `yes`, `no` | Show items from the last 7 days |
| `created_by_me` | enum | `yes`, `no` | Show items created by current user |
| `created` | enum | `today`, `week`, `month`, `all` | Filter by creation date range |

#### Product Orders (036000 / product_orders)

For `show` action, in addition to common parameters:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `approved` | enum | `yes`, `no`, `all` | Filter by approval status |
| `rejected` | enum | `yes`, `no`, `all` | Filter by rejection status |
| `locked` | enum | `yes`, `no`, `all` | Filter by lock status |
| `today` | enum | `yes`, `no` | Show items created today |
| `last_week` | enum | `yes`, `no` | Show items from the last 7 days |
| `created_by_me` | enum | `yes`, `no` | Show items created by current user |
| `created` | enum | `today`, `week`, `month`, `all` | Filter by creation date range |
| `status` | enum | `draft`, `in_progress`, `completed`, `cancelled`, `all` | Filter by order status |

### Parameter Schema Format for Filters

When defining `parameter_schema` for `show` actions, use the following structure:

```python
parameter_schema = {
    # Common filters
    'approved': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by approval status',
        'enum': ['yes', 'no', 'all']
    },
    'rejected': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by rejection status',
        'enum': ['yes', 'no', 'all']
    },
    'locked': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by lock status',
        'enum': ['yes', 'no', 'all']
    },
    'today': {
        'type': 'enum',
        'required': False,
        'description': 'Show items created today',
        'enum': ['yes', 'no']
    },
    'last_week': {
        'type': 'enum',
        'required': False,
        'description': 'Show items from the last 7 days',
        'enum': ['yes', 'no']
    },
    'created_by_me': {
        'type': 'enum',
        'required': False,
        'description': 'Show items created by current user',
        'enum': ['yes', 'no']
    },
    'created': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by creation date range',
        'enum': ['today', 'week', 'month', 'all']
    },
    # Section-specific filters (add as needed)
    'qc_status': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by QC inspection status',
        'enum': ['pending', 'approved', 'rejected', 'not_sent']
    },
    # ... other section-specific parameters
}
```

### Example: Complete Parameter Schema for Temporary Receipts

```python
parameter_schema = {
    # Common filters
    'approved': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by approval status',
        'enum': ['yes', 'no', 'all']
    },
    'locked': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by lock status',
        'enum': ['yes', 'no', 'all']
    },
    'today': {
        'type': 'enum',
        'required': False,
        'description': 'Show items created today',
        'enum': ['yes', 'no']
    },
    'last_week': {
        'type': 'enum',
        'required': False,
        'description': 'Show items from the last 7 days',
        'enum': ['yes', 'no']
    },
    'created_by_me': {
        'type': 'enum',
        'required': False,
        'description': 'Show items created by current user',
        'enum': ['yes', 'no']
    },
    'created': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by creation date range',
        'enum': ['today', 'week', 'month', 'all']
    },
    # Temporary Receipts specific
    'qc_status': {
        'type': 'enum',
        'required': False,
        'description': 'Filter by QC inspection status',
        'enum': ['pending', 'approved', 'rejected', 'not_sent']
    },
    'qc_approved': {
        'type': 'enum',
        'required': False,
        'description': 'Show QC-approved receipts',
        'enum': ['yes', 'no', 'all']
    },
    'qc_rejected': {
        'type': 'enum',
        'required': False,
        'description': 'Show QC-rejected receipts',
        'enum': ['yes', 'no', 'all']
    },
    'qc_pending': {
        'type': 'enum',
        'required': False,
        'description': 'Show receipts pending QC inspection',
        'enum': ['yes', 'no', 'all']
    }
}
```

### Implementation Notes

1. **Multiple Parameters**: All filter parameters are optional and can be combined. For example: `show:locked=yes,today=yes,created_by_me=yes`

2. **Default Behavior**: If no filter parameters are provided, the action should return all visible items (respecting permissions and company scope).

3. **Parameter Values**:
   - Enum values should be displayed in the UI with friendly labels (e.g., "yes" → "بله", "no" → "خیر", "all" → "همه")
   - Date filters should automatically apply the correct date range when selected

4. **Performance**: When implementing filters in views, use database queries efficiently:
   - Use indexed fields for filtering (e.g., `created_at`, `is_locked`, `is_enabled`)
   - Combine multiple filters in a single query using Django ORM `filter()` chaining
   - Consider pagination for large result sets

---

## Implementation Status

- **Status**: ⚠️ **Partially Implemented**
- **Database Tables**: 
  - `invproj_section_registry`: Stores all section definitions (37 sections registered)
  - `invproj_action_registry`: Stores all action definitions (50 actions registered)
- **Migration**: Data migration `0012_populate_section_and_action_registry.py` populates initial data
- **Permission Checking**: Integrated with feature permission system
- **Parameter Validation**: JSON schema validation in `parameter_schema` field
- **Error Handling**: Graceful error handling via handler functions and URL routing

### ⚠️ Pending Tasks (وظایف باقی‌مانده):

1. **Actions Missing**: Sections `groups` (010302) and `access_levels` (010303) are registered in `SectionRegistry` but **have no actions defined in migration**. Actions must be added to `ActionRegistry`.
2. **Filter Parameters**: Standard filter parameters (approved, rejected, locked, today, last_week, created_by_me, created, etc.) are **documented but NOT YET added to database**. Needs migration to update `parameter_schema` for all `show` actions in `ActionRegistry`.
3. **Code Parameter**: `code` parameter for `edit`, `delete`, `lock` actions is documented but **NOT YET added to database**. Needs migration to add `code` as optional parameter to all document actions.
4. **Document Context Parameters**: Support for resolving `{document.*}` parameters needs implementation in the action execution handler.

---

## Adding New Sections and Actions

**Important**: Whenever a new menu item or section is added to the application, it **MUST** be registered in the Entity Reference System.

### Steps to Add a New Section:

1. **Determine the Section Code**:
   - Module number (2 digits): Based on the module (00=Dashboard, 01=Shared, 02=Inventory, etc.)
   - Menu number (2 digits): **Based on the order in the sidebar** (sequential: 01, 02, 03, etc.)
   - Submenu number (2 digits): If part of a submenu, use sequential numbers (01, 02, 03); otherwise use `00` or `NULL`

2. **Choose a Unique Nickname**:
   - Use snake_case format (e.g., `new_feature`, `my_section`)
   - Must be unique across all sections

3. **Add Section to Database**:
   - Create a new data migration in `shared/migrations/`
   - Add entry to `SectionRegistry` with:
     - `section_code`: 6-digit code (e.g., `020901`)
     - `nickname`: Unique identifier
     - `module_code`, `menu_number`, `submenu_number`: Based on sidebar position
     - `name`, `name_en`: Display names
     - `module`, `app_label`: Django app/module names
     - `list_url_name`, `detail_url_name`: URL names for list and detail views
     - `is_enabled`: Set to `1` (enabled)

4. **Define Actions for the Section**:
   - Add entries to `ActionRegistry` for each available action
   - Common actions include:
     - `show`: View/list items
     - `add`: Create new item
     - `edit`: Edit existing item
     - `delete`: Delete item
     - `approve`: Approve document/request
     - `reject`: Reject document/request
     - `lock`: Lock document
     - Custom actions specific to the section
   - For each action, define:
     - `action_name`: Action identifier
     - `action_label`, `action_label_en`: Display labels
     - `url_name`: Django URL name for the action
     - `parameter_schema`: JSON schema for parameters
     - `permission_required`: Required permission code
     - `requires_confirmation`: Whether confirmation is needed
     - `is_destructive`: Whether it's a destructive action

5. **Special Actions for Request-Based Workflows**:

   **For Purchase Requests (020400)**:
   - **`create_receipt_from`**: Creates receipt documents (temporary/permanent/consignment) from approved purchase requests
     - Parameters: `id=<request_id>`, `type=<temporary|permanent|consignment>`
     - Opens intermediate selection page for quantity adjustment and notes
     - Permission: `inventory.receipts.*:create_receipt_from_purchase_request`

   **For Warehouse Requests (020500)**:
   - **`create_issue_from`**: Creates issue documents (permanent/consumption/consignment) from approved warehouse requests
     - Parameters: `id=<request_id>`, `type=<permanent|consumption|consignment>`
     - Opens intermediate selection page for quantity adjustment and notes
     - Permission: `inventory.issues.*:create_issue_from_warehouse_request`

6. **Configure Access Level Permissions**:
   - **CRITICAL**: After creating a new section, you MUST configure its permissions in Access Levels
   - Go to `/shared/access-levels/`
   - Create or edit an Access Level
   - Configure permissions for your new section:
     - View (view_own / view_all)
     - Create
     - Edit (edit_own / edit_other)
     - Delete (delete_own / delete_other)
     - Approve/Reject (if applicable)
     - Lock/Unlock (if applicable)
   - Assign the Access Level to appropriate users or groups
   - **Without this step, users will not be able to access the new section, even if it appears in the sidebar**

7. **Update Documentation**:
   - Update this file (`ENTITY_REFERENCE_SYSTEM.md`) with the new section details
   - Add section to the appropriate module table
   - Document all actions for the section

### Example: Adding a New Inventory Section

```python
# In shared/migrations/XXXX_add_new_section.py

def populate_new_section(apps, schema_editor):
    SectionRegistry = apps.get_model('shared', 'SectionRegistry')
    ActionRegistry = apps.get_model('shared', 'ActionRegistry')
    
    # Add section (assuming it's the 9th menu item in Inventory)
    section = SectionRegistry.objects.create(
        section_code='020901',
        nickname='new_feature',
        module_code='02',
        menu_number='09',
        submenu_number=None,  # No submenu
        name='قابلیت جدید',
        name_en='New Feature',
        description='توضیحات قابلیت جدید',
        module='inventory',
        app_label='inventory',
        list_url_name='inventory:new_feature_list',
        detail_url_name='inventory:new_feature_edit',
        is_enabled=1,
        sort_order=0,
    )
    
    # Add actions
    ActionRegistry.objects.create(
        section=section,
        action_name='show',
        action_label='مشاهده',
        action_label_en='View',
        url_name='inventory:new_feature_list',
        parameter_schema={},
        permission_required='inventory.new_feature:view_all',
        requires_confirmation=0,
        is_destructive=0,
        sort_order=1,
        is_enabled=1,
    )
    # ... add more actions
```

### Important Notes:

- **Menu numbering is based on sidebar order**: The menu number must reflect the actual position in the sidebar, not arbitrary numbers
- **All sections must be registered**: Any section accessible via URL must have an entry in `SectionRegistry`
- **All actions must be registered**: Every action available in a section must be defined in `ActionRegistry`
- **Migration must run on deployment**: The data migration should always run during deployment to ensure registry is up-to-date
- **Cross-module actions**: Actions like `create_receipt_from` and `create_issue_from` enable workflow automation between related modules
- **Access Level configuration is MANDATORY**: After creating a new section, permissions MUST be configured in Access Levels (`/shared/access-levels/`). Without this configuration, users cannot access the new section, even if it appears in the sidebar. This is a critical step that must be completed for every new section.
- **Parameter `code` for document actions**: For actions that require document identification (`edit`, `delete`, `lock`, `approve`, `reject`), both `id` (integer) and `code` (string) parameters should be available. The `code` parameter is optional but recommended as it's more user-friendly.

---

## UI Implementation Guide for Entity Reference Selection

This section describes the standard UI pattern for implementing Entity Reference selection in forms throughout the application. This three-level cascading dropdown system allows users to select sections, actions, and configure parameters in a user-friendly way.

### Overview

The Entity Reference UI consists of three cascading levels:

1. **Section Selection**: Choose a module/section from the application (e.g., "users", "inventory.items")
2. **Action Selection**: Choose an action for the selected section (e.g., "show", "edit", "approve")
3. **Parameters Configuration**: Configure parameters for the selected action (e.g., `gp=superuser`, `id=123`, `type=temporary`)

### API Endpoints

The following API endpoints are required for the Entity Reference UI:

#### 1. Get All Sections
- **URL**: `/ticketing/api/entity-reference/sections/` (or equivalent in your module)
- **Method**: GET
- **Authentication**: Required (login_required)
- **Response**:
  ```json
  {
    "sections": [
      {
        "code": "010301",
        "nickname": "users",
        "name": "کاربران",
        "name_en": "Users"
      },
      ...
    ]
  }
  ```

**Implementation Location**: `ticketing/views/entity_reference.py::EntityReferenceSectionsView`

#### 2. Get Actions for a Section
- **URL**: `/ticketing/api/entity-reference/actions/?section_code=<section_code_or_nickname>`
- **Method**: GET
- **Authentication**: Required
- **Query Parameters**:
  - `section_code`: Section code (e.g., "010301") or nickname (e.g., "users")
- **Response**:
  ```json
  {
    "actions": [
      {
        "action_name": "show",
        "action_label": "مشاهده",
        "action_label_en": "View",
        "parameter_schema": {
          "gp": {
            "type": "string",
            "required": false,
            "description": "Group name filter"
          }
        }
      },
      ...
    ]
  }
  ```

**Implementation Location**: `ticketing/views/entity_reference.py::EntityReferenceActionsView`

#### 3. Get Parameter Values
- **URL**: `/ticketing/api/entity-reference/parameter-values/?parameter_name=<name>&parameter_type=<type>&section_code=<code>&action_name=<action>`
- **Method**: GET
- **Authentication**: Required
- **Query Parameters**:
  - `parameter_name`: Name of the parameter (e.g., "gp", "type", "id")
  - `parameter_type`: Type of parameter (e.g., "string", "integer", "enum")
  - `parameter_enum`: JSON array of enum values (optional, if type is enum)
  - `section_code`: Section code (optional, for context-specific values)
  - `action_name`: Action name (optional, for context-specific values)
- **Response**:
  ```json
  {
    "values": [
      {"value": "value1", "label": "Label 1"},
      {"value": "value2", "label": "Label 2"},
      ...
    ]
  }
  ```

**Implementation Location**: `ticketing/views/entity_reference.py::EntityReferenceParameterValuesView`

### HTML Structure

The UI consists of three dropdowns and a parameters container:

```html
<!-- Entity Reference Configuration -->
<div class="entity-reference-panel" data-field-index="${index}" style="display: none;">
  <!-- Level 1: Section Selection -->
  <div class="form-field" style="margin-bottom: 1rem;">
    <label>Section</label>
    <select name="fields-${index}-entity_section" 
            class="form-control entity-section-select" 
            data-field-index="${index}">
      <option value="">Select section...</option>
      <!-- Options loaded via JavaScript -->
    </select>
  </div>
  
  <!-- Level 2: Action Selection -->
  <div class="form-field" style="margin-bottom: 1rem;">
    <label>Action</label>
    <select name="fields-${index}-entity_action" 
            class="form-control entity-action-select" 
            data-field-index="${index}" 
            disabled>
      <option value="">Select action...</option>
      <!-- Options loaded when section is selected -->
    </select>
  </div>
  
  <!-- Level 3: Parameters Configuration -->
  <div class="entity-parameters-container" data-field-index="${index}">
    <label>Parameters</label>
    <div class="entity-parameters-list" data-field-index="${index}">
      <!-- Parameters dynamically added when action is selected -->
    </div>
  </div>
  
  <!-- Hidden input for storing final entity reference string -->
  <input type="hidden" 
         name="fields-${index}-entity_reference" 
         class="entity-reference-hidden" 
         data-field-index="${index}"
         value="" />
</div>
```

### JavaScript Implementation

The JavaScript implementation requires the following functions:

#### 1. Load Sections
```javascript
function loadEntityReferenceSections(fieldIndex) {
  const sectionSelect = document.querySelector(`select.entity-section-select[data-field-index="${fieldIndex}"]`);
  if (!sectionSelect) return;
  
  fetch('/ticketing/api/entity-reference/sections/', {
    method: 'GET',
    headers: {
      'X-CSRFToken': getCsrfToken(),
      'Content-Type': 'application/json',
    },
    credentials: 'same-origin',
  })
    .then(response => response.json())
    .then(data => {
      data.sections.forEach(section => {
        const option = document.createElement('option');
        option.value = section.nickname; // Or section.code
        option.textContent = section.name + ' (' + section.nickname + ')';
        option.setAttribute('data-code', section.code);
        sectionSelect.appendChild(option);
      });
    })
    .catch(error => console.error('Error loading sections:', error));
}
```

#### 2. Load Actions
```javascript
function loadEntityReferenceActions(fieldIndex, sectionIdentifier) {
  const actionSelect = document.querySelector(`select.entity-action-select[data-field-index="${fieldIndex}"]`);
  if (!actionSelect || !sectionIdentifier) return;
  
  actionSelect.innerHTML = '<option value="">Select action...</option>';
  actionSelect.disabled = true;
  
  fetch(`/ticketing/api/entity-reference/actions/?section_code=${encodeURIComponent(sectionIdentifier)}`)
    .then(response => response.json())
    .then(data => {
      data.actions.forEach(action => {
        const option = document.createElement('option');
        option.value = action.action_name;
        option.textContent = action.action_label;
        option.setAttribute('data-schema', JSON.stringify(action.parameter_schema));
        actionSelect.appendChild(option);
      });
      actionSelect.disabled = false;
    })
    .catch(error => console.error('Error loading actions:', error));
}
```

#### 3. Load Parameters
```javascript
function loadEntityReferenceParameters(fieldIndex, actionOption) {
  const paramsContainer = document.querySelector(`.entity-parameters-list[data-field-index="${fieldIndex}"]`);
  if (!paramsContainer || !actionOption) return;
  
  paramsContainer.innerHTML = '';
  const parameterSchema = JSON.parse(actionOption.getAttribute('data-schema') || '{}');
  
  if (!parameterSchema || Object.keys(parameterSchema).length === 0) {
    paramsContainer.innerHTML = '<p>No parameters required for this action</p>';
    return;
  }
  
  // Create input for each parameter
  Object.keys(parameterSchema).forEach(paramName => {
    const paramDef = parameterSchema[paramName];
    // Create appropriate input based on paramDef.type and paramDef.enum
    // See full implementation in ticketing templates
  });
}
```

#### 4. Update Entity Reference Value
```javascript
function updateEntityReferenceValue(fieldIndex) {
  const sectionSelect = document.querySelector(`select.entity-section-select[data-field-index="${fieldIndex}"]`);
  const actionSelect = document.querySelector(`select.entity-action-select[data-field-index="${fieldIndex}"]`);
  const hiddenInput = document.querySelector(`input.entity-reference-hidden[data-field-index="${fieldIndex}"]`);
  
  if (!sectionSelect || !actionSelect || !hiddenInput) return;
  
  const sectionValue = sectionSelect.value;
  const actionValue = actionSelect.value;
  
  if (!sectionValue || !actionValue) {
    hiddenInput.value = '';
    return;
  }
  
  // Build entity reference string: section:action:params
  let entityRef = sectionValue + ':' + actionValue;
  
  // Collect parameters
  const params = [];
  const paramInputs = document.querySelectorAll(`.entity-parameter-input[data-field-index="${fieldIndex}"]`);
  paramInputs.forEach(input => {
    if (input.value) {
      const paramName = input.getAttribute('data-param-name');
      params.push(paramName + '=' + input.value);
    }
  });
  
  if (params.length > 0) {
    entityRef += ':' + params.join(',');
  }
  
  hiddenInput.value = entityRef;
}
```

### Event Listeners

```javascript
// Section selection change
document.addEventListener('change', function(e) {
  if (e.target.matches('.entity-section-select')) {
    const fieldIndex = e.target.getAttribute('data-field-index');
    loadEntityReferenceActions(fieldIndex, e.target.value);
    updateEntityReferenceValue(fieldIndex);
  }
  
  // Action selection change
  if (e.target.matches('.entity-action-select')) {
    const fieldIndex = e.target.getAttribute('data-field-index');
    const selectedOption = e.target.options[e.target.selectedIndex];
    loadEntityReferenceParameters(fieldIndex, selectedOption);
    updateEntityReferenceValue(fieldIndex);
  }
  
  // Parameter value change
  if (e.target.matches('.entity-parameter-input')) {
    const fieldIndex = e.target.getAttribute('data-field-index');
    updateEntityReferenceValue(fieldIndex);
  }
});
```

### Integration Steps

To implement Entity Reference UI in a new module:

1. **Copy API Views**: Copy `ticketing/views/entity_reference.py` to your module's views directory
2. **Add URLs**: Add the three API endpoints to your module's `urls.py`:
   ```python
   path('api/entity-reference/sections/', entity_reference.EntityReferenceSectionsView.as_view(), name='api_entity_reference_sections'),
   path('api/entity-reference/actions/', entity_reference.EntityReferenceActionsView.as_view(), name='api_entity_reference_actions'),
   path('api/entity-reference/parameter-values/', entity_reference.EntityReferenceParameterValuesView.as_view(), name='api_entity_reference_parameter_values'),
   ```
3. **Add HTML Structure**: Add the Entity Reference panel HTML to your template
4. **Add JavaScript**: Copy the JavaScript functions from `ticketing/templates/template_form.html` to your template
5. **Update URL References**: Update the API URLs in JavaScript to match your module's URLs

### Parameter Schema Format

When defining actions in `ActionRegistry`, use the following format for `parameter_schema`:

```python
parameter_schema = {
    'param_name': {
        'type': 'string' | 'integer' | 'number' | 'enum',
        'required': True | False,
        'description': 'Human-readable description',
        'enum': ['value1', 'value2', ...]  # Required if type is 'enum'
    },
    ...
}
```

**Example**:
```python
parameter_schema = {
    'gp': {
        'type': 'string',
        'required': False,
        'description': 'Group name filter'
    },
    'type': {
        'type': 'enum',
        'required': True,
        'description': 'Document type',
        'enum': ['temporary', 'permanent', 'consignment']
    },
    'id': {
        'type': 'integer',
        'required': True,
        'description': 'Record ID'
    }
}
```

### Parameter Value Loading

The `EntityReferenceParameterValuesView` handles special parameter types:

- **Enum parameters**: Values are automatically generated from the enum array
- **`gp` parameter**: Returns list of all user groups
- **`type` parameter**: Returns context-specific types (e.g., receipt types, issue types) based on section code
- **Custom parameters**: Can be extended to load values from specific models

### Example: Complete Implementation

See `ticketing/templates/ticketing/template_form.html` for a complete working example of the Entity Reference UI implementation, including:
- HTML structure for Entity Reference panel
- JavaScript functions for loading sections, actions, and parameters
- Event listeners for cascading dropdowns
- Integration with form submission
- Loading existing entity reference values on edit

### Notes

- **Display Format**: Sections can be displayed using either `nickname` (e.g., "users") or `section_code` (e.g., "010301"), but not both. Choose one format consistently throughout your UI.
- **Parameter Storage**: The final entity reference string is stored in format: `section:action:param1=value1,param2=value2`
- **Lazy Loading**: Sections are loaded only when the Entity Reference panel becomes visible to improve initial page load performance
- **Error Handling**: Always include error handling in fetch calls and display user-friendly error messages
