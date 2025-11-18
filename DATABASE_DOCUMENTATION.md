# Database Documentation - Inventory Management System

## Table of Contents
1. [Overview](#overview)
2. [Menu Structure and Database Mapping](#menu-structure-and-database-mapping)
3. [Database Tables and Fields](#database-tables-and-fields)
4. [Entity Relationships (ER Diagram)](#entity-relationships-er-diagram)
5. [Operations and Related Tables](#operations-and-related-tables)
6. [Business Logic and Workflows](#business-logic-and-workflows)

---

## Overview

This document provides a comprehensive mapping between the user interface (menus, views) and the database structure (tables, fields, relationships) for the Inventory Management System. It includes detailed field descriptions, relationships, operations, and business logic.

**System Architecture:**
- **Framework**: Django (Python)
- **Database**: PostgreSQL
- **Multi-tenant**: Company-scoped data
- **Multi-language**: Persian (RTL) and English support

---

## Menu Structure and Database Mapping

### Shared Module

#### Dashboard
- **Menu**: `Dashboard`
- **URL**: `/ui/dashboard/`
- **View**: `ui.views.DashboardView`
- **Database Tables**: None (aggregated data from multiple tables)
- **Purpose**: Displays summary statistics and overview

#### Companies
- **Menu**: `Companies`
- **URL**: `/shared/companies/`
- **View**: `shared.views.CompanyListView`
- **Model**: `shared.models.Company`
- **Database Table**: `shared_company`
- **Operations**: Create, Edit, Delete, List

#### Company Units
- **Menu**: `Company Units`
- **URL**: `/shared/company-units/`
- **View**: `shared.views.CompanyUnitListView`
- **Model**: `shared.models.CompanyUnit`
- **Database Table**: `shared_companyunit`
- **Operations**: Create, Edit, Delete, List

#### Personnel
- **Menu**: `Personnel`
- **URL**: `/production/personnel/`
- **View**: `production.views.PersonnelListView`
- **Model**: `production.models.Person`
- **Database Table**: `production_person`
- **Operations**: Create, Edit, Delete, List

#### Machines
- **Menu**: `Machines`
- **URL**: `/production/machines/`
- **View**: `production.views.MachineListView`
- **Model**: `production.models.Machine`
- **Database Table**: `production_machine`
- **Operations**: Create, Edit, Delete, List

#### Users
- **Menu**: `Users` → `Users`
- **URL**: `/shared/users/`
- **View**: `shared.views.UserListView`
- **Model**: `shared.models.User`
- **Database Table**: `shared_user` (extends Django's AbstractUser)
- **Operations**: Create, Edit, Delete, List

#### Groups
- **Menu**: `Users` → `Groups`
- **URL**: `/shared/groups/`
- **View**: `shared.views.GroupListView`
- **Model**: `django.contrib.auth.models.Group` + `shared.models.GroupProfile`
- **Database Tables**: `auth_group`, `shared_groupprofile`
- **Operations**: Create, Edit, Delete, List

#### Access Levels
- **Menu**: `Users` → `Access Levels`
- **URL**: `/shared/access-levels/`
- **View**: `shared.views.AccessLevelListView`
- **Model**: `shared.models.AccessLevel`
- **Database Table**: `shared_accesslevel`
- **Operations**: Create, Edit, Delete, List

---

### Inventory Module

#### Master Data

##### Item Types
- **Menu**: `Inventory` → `Master Data` → `Item Types`
- **URL**: `/inventory/item-types/`
- **View**: `inventory.views.ItemTypeListView`
- **Model**: `inventory.models.ItemType`
- **Database Table**: `inventory_itemtype`
- **Operations**: 
  - **List**: `ItemTypeListView` → `GET /inventory/item-types/`
  - **Create**: `ItemTypeCreateView` → `GET/POST /inventory/item-types/create/`
  - **Edit**: `ItemTypeUpdateView` → `GET/POST /inventory/item-types/<pk>/edit/`
  - **Delete**: `ItemTypeDeleteView` → `POST /inventory/item-types/<pk>/delete/`

##### Item Categories
- **Menu**: `Inventory` → `Master Data` → `Item Categories`
- **URL**: `/inventory/item-categories/`
- **View**: `inventory.views.ItemCategoryListView`
- **Model**: `inventory.models.ItemCategory`
- **Database Table**: `inventory_itemcategory`
- **Operations**: Create, Edit, Delete, List

##### Item Subcategories
- **Menu**: `Inventory` → `Master Data` → `Item Subcategories`
- **URL**: `/inventory/item-subcategories/`
- **View**: `inventory.views.ItemSubcategoryListView`
- **Model**: `inventory.models.ItemSubcategory`
- **Database Table**: `inventory_itemsubcategory`
- **Operations**: Create, Edit, Delete, List

##### Warehouses
- **Menu**: `Inventory` → `Master Data` → `Warehouses`
- **URL**: `/inventory/warehouses/`
- **View**: `inventory.views.WarehouseListView`
- **Model**: `inventory.models.Warehouse`
- **Database Table**: `inventory_warehouse`
- **Operations**: Create, Edit, Delete, List

#### Items

##### Create Item
- **Menu**: `Inventory` → `Items` → `Create Item`
- **URL**: `/inventory/items/create/`
- **View**: `inventory.views.ItemCreateView`
- **Model**: `inventory.models.Item`
- **Database Table**: `inventory_item`
- **Operations**: Create (with inline ItemUnit formset)

##### Edit Items
- **Menu**: `Inventory` → `Items` → `Edit Items`
- **URL**: `/inventory/items/`
- **View**: `inventory.views.ItemListView`
- **Model**: `inventory.models.Item`
- **Database Table**: `inventory_item`
- **Operations**: List, Edit, Delete

##### Item Serials
- **Menu**: `Inventory` → `Items` → `Item Serials`
- **URL**: `/inventory/item-serials/`
- **View**: `inventory.views.ItemSerialListView`
- **Model**: `inventory.models.ItemSerial`
- **Database Table**: `inventory_itemserial`
- **Operations**: List, View

##### Inventory Balance
- **Menu**: `Inventory` → `Items` → `Inventory Balance`
- **URL**: `/inventory/balance/`
- **View**: `inventory.views.InventoryBalanceView`
- **Database Tables**: Calculated on-demand from receipts, issues, stocktaking
- **Operations**: View (calculated, not stored)

#### Suppliers

##### Supplier Categories
- **Menu**: `Inventory` → `Suppliers` → `Supplier Categories`
- **URL**: `/inventory/supplier-categories/`
- **View**: `inventory.views.SupplierCategoryListView`
- **Model**: `inventory.models.SupplierCategory`
- **Database Table**: `inventory_suppliercategory`
- **Operations**: Create, Edit, Delete, List

##### Supplier List
- **Menu**: `Inventory` → `Suppliers` → `Supplier List`
- **URL**: `/inventory/suppliers/`
- **View**: `inventory.views.SupplierListView`
- **Model**: `inventory.models.Supplier`
- **Database Table**: `inventory_supplier`
- **Operations**: Create, Edit, Delete, List

#### Purchase Requests
- **Menu**: `Inventory` → `Purchase Requests`
- **URL**: `/inventory/purchase-requests/`
- **View**: `inventory.views.PurchaseRequestListView`
- **Model**: `inventory.models.PurchaseRequest`
- **Database Table**: `inventory_purchaserequest`
- **Operations**: 
  - **List**: `PurchaseRequestListView` → `GET /inventory/purchase-requests/`
  - **Create**: `PurchaseRequestCreateView` → `GET/POST /inventory/purchase-requests/create/`
  - **Edit**: `PurchaseRequestUpdateView` → `GET/POST /inventory/purchase-requests/<pk>/edit/`
  - **Approve**: `PurchaseRequestApproveView` → `POST /inventory/purchase-requests/<pk>/approve/`

#### Warehouse Requests
- **Menu**: `Inventory` → `Warehouse Requests`
- **URL**: `/inventory/warehouse-requests/`
- **View**: `inventory.views.WarehouseRequestListView`
- **Model**: `inventory.models.WarehouseRequest`
- **Database Table**: `inventory_warehouserequest`
- **Operations**: Create, Edit, Approve, List

#### Receipts

##### Temporary Receipts
- **Menu**: `Inventory` → `Receipts` → `Temporary Receipts`
- **URL**: `/inventory/receipts/temporary/`
- **View**: `inventory.views.ReceiptTemporaryListView`
- **Model**: `inventory.models.ReceiptTemporary`
- **Database Table**: `inventory_receipttemporary`
- **Operations**: 
  - **List**: `ReceiptTemporaryListView` → `GET /inventory/receipts/temporary/`
  - **Create**: `ReceiptTemporaryCreateView` → `GET/POST /inventory/receipts/temporary/create/`
  - **Edit**: `ReceiptTemporaryUpdateView` → `GET/POST /inventory/receipts/temporary/<pk>/edit/`
  - **Lock**: `ReceiptTemporaryLockView` → `POST /inventory/receipts/temporary/<pk>/lock/`

##### Permanent Receipts
- **Menu**: `Inventory` → `Receipts` → `Permanent Receipts`
- **URL**: `/inventory/receipts/permanent/`
- **View**: `inventory.views.ReceiptPermanentListView`
- **Model**: `inventory.models.ReceiptPermanent` (header) + `inventory.models.ReceiptPermanentLine` (lines)
- **Database Tables**: 
  - `inventory_receiptpermanent` (header)
  - `inventory_receiptpermanentline` (lines)
- **Operations**: 
  - **List**: `ReceiptPermanentListView` → `GET /inventory/receipts/permanent/`
  - **Create**: `ReceiptPermanentCreateView` → `GET/POST /inventory/receipts/permanent/create/`
  - **Edit**: `ReceiptPermanentUpdateView` → `GET/POST /inventory/receipts/permanent/<pk>/edit/`
  - **Lock**: `ReceiptPermanentLockView` → `POST /inventory/receipts/permanent/<pk>/lock/`
  - **Line Serials**: `ReceiptPermanentLineSerialAssignmentView` → `GET/POST /inventory/receipts/permanent/<pk>/lines/<line_id>/serials/`

##### Consignment Receipts
- **Menu**: `Inventory` → `Receipts` → `Consignment Receipts`
- **URL**: `/inventory/receipts/consignment/`
- **View**: `inventory.views.ReceiptConsignmentListView`
- **Model**: `inventory.models.ReceiptConsignment` (header) + `inventory.models.ReceiptConsignmentLine` (lines)
- **Database Tables**: 
  - `inventory_receiptconsignment` (header)
  - `inventory_receiptconsignmentline` (lines)
- **Operations**: Create, Edit, Lock, List, Line Serials

#### Issues

##### Permanent Issues
- **Menu**: `Inventory` → `Issues` → `Permanent Issues`
- **URL**: `/inventory/issues/permanent/`
- **View**: `inventory.views.IssuePermanentListView`
- **Model**: `inventory.models.IssuePermanent` (header) + `inventory.models.IssuePermanentLine` (lines)
- **Database Tables**: 
  - `inventory_issuepermanent` (header)
  - `inventory_issuepermanentline` (lines)
- **Operations**: Create, Edit, Lock, List, Line Serials

##### Consumption Issues
- **Menu**: `Inventory` → `Issues` → `Consumption Issues`
- **URL**: `/inventory/issues/consumption/`
- **View**: `inventory.views.IssueConsumptionListView`
- **Model**: `inventory.models.IssueConsumption` (header) + `inventory.models.IssueConsumptionLine` (lines)
- **Database Tables**: 
  - `inventory_issueconsumption` (header)
  - `inventory_issueconsumptionline` (lines)
- **Operations**: Create, Edit, Lock, List, Line Serials

##### Consignment Issues
- **Menu**: `Inventory` → `Issues` → `Consignment Issues`
- **URL**: `/inventory/issues/consignment/`
- **View**: `inventory.views.IssueConsignmentListView`
- **Model**: `inventory.models.IssueConsignment` (header) + `inventory.models.IssueConsignmentLine` (lines)
- **Database Tables**: 
  - `inventory_issueconsignment` (header)
  - `inventory_issueconsignmentline` (lines)
- **Operations**: Create, Edit, Lock, List, Line Serials

#### Stocktaking

##### Deficit Records
- **Menu**: `Inventory` → `Stocktaking` → `Deficit Records`
- **URL**: `/inventory/stocktaking/deficit/`
- **View**: `inventory.views.StocktakingDeficitListView`
- **Model**: `inventory.models.StocktakingDeficit`
- **Database Table**: `inventory_stocktakingdeficit`
- **Operations**: Create, Edit, Lock, List

##### Surplus Records
- **Menu**: `Inventory` → `Stocktaking` → `Surplus Records`
- **URL**: `/inventory/stocktaking/surplus/`
- **View**: `inventory.views.StocktakingSurplusListView`
- **Model**: `inventory.models.StocktakingSurplus`
- **Database Table**: `inventory_stocktakingsurplus`
- **Operations**: Create, Edit, Lock, List

##### Stocktaking Records
- **Menu**: `Inventory` → `Stocktaking` → `Stocktaking Records`
- **URL**: `/inventory/stocktaking/records/`
- **View**: `inventory.views.StocktakingRecordListView`
- **Model**: `inventory.models.StocktakingRecord`
- **Database Table**: `inventory_stocktakingrecord`
- **Operations**: Create, Edit, Lock, List

#### Production

##### Work Lines
- **Menu**: `Production` → `Work Lines`
- **URL**: `/inventory/work-lines/`
- **View**: `inventory.views.WorkLineListView`
- **Model**: `inventory.models.WorkLine`
- **Database Table**: `inventory_workline`
- **Operations**: List (read-only)

---

## Database Tables and Fields

### Shared Module Tables

#### shared_company
**Purpose**: Stores company/organization master data

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| public_code | CharField(3) | Unique company code (numeric) | Unique, Not null |
| legal_name | CharField(180) | Legal company name | Unique, Not null |
| display_name | CharField(180) | Display name | Unique, Not null |
| display_name_en | CharField(180) | English display name | Optional |
| registration_number | CharField(60) | Business registration number | Unique, Optional |
| tax_id | CharField(60) | Tax identification number | Unique, Optional |
| phone_number | CharField(30) | Phone number | Optional |
| email | EmailField | Email address | Optional |
| website | URLField | Website URL | Optional |
| address | TextField | Physical address | Optional |
| city | CharField(120) | City | Optional |
| state | CharField(120) | State/Province | Optional |
| country | CharField(3) | Country code | Optional |
| is_enabled | SmallInt | Active status (0=Disabled, 1=Enabled) | Default: 1 |
| enabled_at | DateTime | When enabled | Optional |
| enabled_by_id | BigInt | User who enabled | FK to shared_user, Optional |
| disabled_at | DateTime | When disabled | Optional |
| disabled_by_id | BigInt | User who disabled | FK to shared_user, Optional |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- One-to-Many: `Company` → `CompanyUnit`, `Item`, `Warehouse`, etc. (all company-scoped models)
- One-to-Many: `Company` → `Person` (via production module)

#### shared_companyunit
**Purpose**: Stores organizational units/departments within a company

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| public_code | CharField(5) | Unique unit code within company | Unique per company, Not null |
| name | CharField(180) | Unit name | Unique per company, Not null |
| name_en | CharField(180) | English name | Optional |
| unit_type | CharField(30) | Type of unit (e.g., "department", "division") | Not null |
| parent_unit_id | BigInt | Parent unit (hierarchical) | FK to self, Optional |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `CompanyUnit` → `Company` (company_id)
- One-to-Many: `CompanyUnit` → `CompanyUnit` (parent_unit_id, self-referential)
- Many-to-Many: `CompanyUnit` ↔ `Person` (via production_person_company_units)

#### production_person
**Purpose**: Stores personnel/employee information (moved from shared module to production module)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| public_code | CharField(8) | Unique person code within company | Unique per company, Not null |
| username | CharField(150) | Username | Unique per company, Not null |
| first_name | CharField(120) | First name | Not null |
| last_name | CharField(120) | Last name | Not null |
| first_name_en | CharField(120) | English first name | Optional |
| last_name_en | CharField(120) | English last name | Optional |
| national_id | CharField(20) | National ID number | Unique, Optional |
| personnel_code | CharField(30) | Personnel code | Unique, Optional |
| email | EmailField | Email address | Unique, Optional |
| phone_number | CharField(30) | Phone number | Optional |
| mobile_number | CharField(30) | Mobile number | Optional |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| user_id | BigInt | Linked user account | FK to shared_user, OneToOne, Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `Person` → `Company` (company_id)
- One-to-One: `Person` → `User` (user_id)
- Many-to-Many: `Person` ↔ `CompanyUnit` (via production_person_company_units)

#### shared_user
**Purpose**: User authentication and authorization (extends Django's AbstractUser)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| username | CharField(150) | Username | Unique, Not null |
| email | EmailField | Email address | Unique, Not null |
| password | CharField(128) | Hashed password | Not null |
| first_name | CharField(150) | First name | Optional |
| last_name | CharField(150) | Last name | Optional |
| is_staff | Boolean | Staff status | Default: False |
| is_active | Boolean | Active status | Default: True |
| is_superuser | Boolean | Superuser status | Default: False |
| date_joined | DateTime | Registration date | Auto-set |
| last_login | DateTime | Last login timestamp | Optional |
| phone_number | CharField(30) | Phone number | Optional |
| mobile_number | CharField(30) | Mobile number | Optional |
| first_name_en | CharField(120) | English first name | Optional |
| last_name_en | CharField(120) | English last name | Optional |
| default_company_id | BigInt | Default company | FK to shared_company, Optional |
| metadata | JSONField | Additional metadata | Default: {} |

**Relationships:**
- Many-to-One: `User` → `Company` (default_company_id)
- One-to-One: `User` → `Person` (via production_person.user_id)
- Many-to-Many: `User` ↔ `Company` (via shared_usercompanyaccess)

---

### Inventory Module Tables

#### inventory_itemtype
**Purpose**: Item type classification (e.g., "Raw Material", "Finished Good")

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| public_code | CharField(3) | Unique type code within company | Unique per company, Not null |
| name | CharField(120) | Type name | Unique per company, Not null |
| name_en | CharField(120) | English name | Unique per company, Not null |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ItemType` → `Company` (company_id)
- One-to-Many: `ItemType` → `Item` (items)

#### inventory_itemcategory
**Purpose**: Item category classification (e.g., "Electronics", "Mechanical")

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| public_code | CharField(3) | Unique category code within company | Unique per company, Not null |
| name | CharField(120) | Category name | Unique per company, Not null |
| name_en | CharField(120) | English name | Unique per company, Not null |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ItemCategory` → `Company` (company_id)
- One-to-Many: `ItemCategory` → `Item` (items)
- One-to-Many: `ItemCategory` → `ItemSubcategory` (subcategories)

#### inventory_itemsubcategory
**Purpose**: Item subcategory classification (e.g., "Resistors", "Bolts")

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| category_id | BigInt | Parent category | FK to inventory_itemcategory, Not null |
| public_code | CharField(3) | Unique subcategory code within company | Unique per company, Not null |
| name | CharField(120) | Subcategory name | Unique per company, Not null |
| name_en | CharField(120) | English name | Unique per company, Not null |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ItemSubcategory` → `Company` (company_id)
- Many-to-One: `ItemSubcategory` → `ItemCategory` (category_id)
- One-to-Many: `ItemSubcategory` → `Item` (items)

#### inventory_warehouse
**Purpose**: Warehouse/storage location master data

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| public_code | CharField(5) | Unique warehouse code within company | Unique per company, Not null |
| name | CharField(150) | Warehouse name | Unique per company, Not null |
| name_en | CharField(150) | English name | Unique per company, Not null |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `Warehouse` → `Company` (company_id)
- One-to-Many: `Warehouse` → `WorkLine` (work_lines)
- One-to-Many: `Warehouse` → `ItemWarehouse` (items)
- One-to-Many: `Warehouse` → `ReceiptTemporary` (temporary_receipts)
- One-to-Many: `Warehouse` → `ReceiptPermanentLine` (receiptpermanentline_set)
- One-to-Many: `Warehouse` → `IssuePermanentLine` (issuepermanentline_set)

#### inventory_item
**Purpose**: Item/product master data (central entity)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| type_id | BigInt | Item type | FK to inventory_itemtype, Not null, PROTECT |
| category_id | BigInt | Item category | FK to inventory_itemcategory, Not null, PROTECT |
| subcategory_id | BigInt | Item subcategory | FK to inventory_itemsubcategory, Not null, PROTECT |
| type_code | CharField(3) | Type code (cached) | Not null, Editable=False |
| category_code | CharField(3) | Category code (cached) | Not null, Editable=False |
| subcategory_code | CharField(3) | Subcategory code (cached) | Not null, Editable=False |
| user_segment | CharField(2) | User segment (2 digits) | Not null |
| sequence_segment | CharField(5) | Sequence segment (5 digits) | Not null, Editable=False |
| item_code | CharField(7) | Item code (User(2) + Sequence(5)) | Not null, Unique |
| full_item_code | CharField(16) | Full code (Type(3) + Category(3) + SubCategory(3) + ItemCode(7)) | Unique, Not null |
| batch_number | CharField(20) | Batch number (MMYY-XXXXXX format) | Not null |
| name | CharField(180) | Item name | Unique, Not null |
| name_en | CharField(180) | English name | Unique, Not null |
| is_sellable | SmallInt | Sellable flag (0=No, 1=Yes) | Default: 0 |
| has_lot_tracking | SmallInt | Lot tracking flag | Default: 0 |
| requires_temporary_receipt | SmallInt | Requires temp receipt flag | Default: 0 |
| tax_id | CharField(30) | Tax ID | Optional |
| tax_title | CharField(120) | Tax title | Optional |
| min_stock | Decimal(18,6) | Minimum stock level | Optional |
| default_unit | CharField(30) | Default unit (e.g., "EA", "KG") | Not null |
| default_unit_id | BigInt | Default unit conversion ID | FK to inventory_itemunit, Optional |
| primary_unit | CharField(30) | Primary unit | Not null |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `Item` → `Company` (company_id)
- Many-to-One: `Item` → `ItemType` (type_id)
- Many-to-One: `Item` → `ItemCategory` (category_id)
- Many-to-One: `Item` → `ItemSubcategory` (subcategory_id)
- One-to-Many: `Item` → `ItemSpec` (specifications)
- One-to-Many: `Item` → `ItemUnit` (units)
- One-to-Many: `Item` → `ItemWarehouse` (warehouses)
- One-to-Many: `Item` → `ItemSubstitute` (substitutes)
- One-to-Many: `Item` → `ReceiptTemporary` (temporary_receipts)
- One-to-Many: `Item` → `ReceiptPermanentLine` (receiptpermanentline_set)
- One-to-Many: `Item` → `IssuePermanentLine` (issuepermanentline_set)

**Business Logic:**
- `item_code` is auto-generated: `user_segment` (2 digits) + `sequence_segment` (5 digits) = 7 digits
- `full_item_code` is auto-generated: `type_code` (3) + `category_code` (3) + `subcategory_code` (3) + `item_code` (7) = 16 digits
- `batch_number` is auto-generated: `MMYY-XXXXXX` format based on current month/year
- `sequence_segment` is auto-incremented per type/category/subcategory/user_segment combination
- **Warehouse Restrictions**: Item can only be received/issued in warehouses explicitly configured in `ItemWarehouse` relationship (strict validation)

#### inventory_itemunit
**Purpose**: Unit conversion definitions for items (e.g., 1 BOX = 100 EA)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| item_id | BigInt | Item reference | FK to inventory_item, Not null, CASCADE |
| item_code | CharField(30) | Item code (cached) | Not null |
| public_code | CharField(6) | Unique unit code within company | Unique per company, Not null |
| from_unit | CharField(30) | Source unit name | Not null |
| from_quantity | Decimal(18,6) | Source quantity | Default: 1.0, Not null |
| to_unit | CharField(30) | Target unit name | Not null |
| to_quantity | Decimal(18,6) | Target quantity | Not null |
| is_primary | SmallInt | Primary unit flag | Default: 0 |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ItemUnit` → `Company` (company_id)
- Many-to-One: `ItemUnit` → `Item` (item_id, CASCADE)

**Business Logic:**
- Conversion factor: `to_quantity / from_quantity` (e.g., if 1 BOX = 100 EA, then from_quantity=1, to_quantity=100)
- Unit conversion uses graph traversal algorithm to find conversion path between any two units
- Unique constraint: (company, item, from_unit, to_unit) - prevents duplicate conversions

#### inventory_itemwarehouse
**Purpose**: Mapping between items and warehouses - defines which warehouses an item can be received/issued from (strict restriction)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| item_id | BigInt | Item reference | FK to inventory_item, Not null, CASCADE |
| warehouse_id | BigInt | Warehouse reference | FK to inventory_warehouse, Not null, CASCADE |
| is_primary | SmallInt | Primary warehouse flag (first selected warehouse) | Default: 0 |
| notes | TextField | Optional notes | Optional |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ItemWarehouse` → `Company` (company_id)
- Many-to-One: `ItemWarehouse` → `Item` (item_id, CASCADE)
- Many-to-One: `ItemWarehouse` → `Warehouse` (warehouse_id, CASCADE)

**Business Logic:**
- **Strict Warehouse Restriction**: Items can ONLY be received/issued in warehouses explicitly listed in this table
- First selected warehouse is marked as primary (`is_primary=1`)
- If no warehouses configured for item → Item cannot be received/issued anywhere (error shown)
- Used by forms to filter warehouse dropdowns dynamically
- Validation enforced in both server-side (Python) and client-side (JavaScript)

**Constraints:**
- Unique constraint: `(company, item, warehouse)` - prevents duplicate mappings

#### inventory_supplier
**Purpose**: Supplier/vendor master data

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| public_code | CharField(6) | Unique supplier code within company | Unique per company, Not null |
| name | CharField(180) | Supplier name | Unique per company, Not null |
| name_en | CharField(180) | English name | Unique per company, Not null |
| contact_person | CharField(120) | Contact person name | Optional |
| phone_number | CharField(30) | Phone number | Optional |
| email | EmailField | Email address | Optional |
| address | TextField | Address | Optional |
| tax_id | CharField(30) | Tax ID | Optional |
| description | CharField(255) | Description | Optional |
| notes | TextField | Notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| is_enabled | SmallInt | Active status | Default: 1 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `Supplier` → `Company` (company_id)
- One-to-Many: `Supplier` → `SupplierCategory` (categories)
- One-to-Many: `Supplier` → `SupplierSubcategory` (subcategories)
- One-to-Many: `Supplier` → `SupplierItem` (items)
- One-to-Many: `Supplier` → `ReceiptTemporary` (temporary_receipts)
- One-to-Many: `Supplier` → `ReceiptPermanentLine` (permanent_receipt_lines)

#### inventory_receipttemporary
**Purpose**: Temporary receipt documents (single-line, pre-inspection)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| document_code | CharField(20) | Unique document code | Unique, Not null |
| document_date | Date | Document date | Default: today, Not null |
| item_id | BigInt | Item reference | FK to inventory_item, Not null, PROTECT |
| item_code | CharField(16) | Item code (cached) | Not null |
| warehouse_id | BigInt | Warehouse reference | FK to inventory_warehouse, Not null, PROTECT |
| warehouse_code | CharField(5) | Warehouse code (cached) | Not null |
| unit | CharField(30) | Unit (default unit) | Not null |
| quantity | Decimal(18,6) | Quantity (in default unit) | Not null |
| entered_unit | CharField(30) | User-entered unit | Optional |
| entered_quantity | Decimal(18,6) | User-entered quantity | Optional |
| expected_receipt_date | Date | Expected receipt date | Optional |
| supplier_id | BigInt | Supplier reference | FK to inventory_supplier, Optional, SET_NULL |
| supplier_code | CharField(6) | Supplier code (cached) | Optional |
| source_document_type | CharField(60) | Source document type | Optional |
| source_document_code | CharField(30) | Source document code | Optional |
| status | SmallInt | Status (0=Draft, 1=Awaiting inspection, 2=Closed) | Default: 0 |
| inspection_result | JSONField | QC inspection results | Default: {} |
| document_metadata | JSONField | Additional metadata | Default: {} |
| qc_approved_by_id | BigInt | QC approver | FK to shared_user, Optional |
| qc_approved_at | DateTime | QC approval timestamp | Optional |
| qc_approval_notes | TextField | QC approval notes | Optional |
| is_converted | SmallInt | Converted to permanent flag | Default: 0 |
| converted_receipt_id | BigInt | Converted permanent receipt | FK to inventory_receiptpermanent, OneToOne, Optional |
| converted_receipt_code | CharField(20) | Converted receipt code (cached) | Optional |
| is_locked | SmallInt | Locked flag | Default: 0 |
| locked_at | DateTime | Lock timestamp | Optional |
| locked_by_id | BigInt | User who locked | FK to shared_user, Optional |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ReceiptTemporary` → `Company` (company_id)
- Many-to-One: `ReceiptTemporary` → `Item` (item_id, PROTECT)
- Many-to-One: `ReceiptTemporary` → `Warehouse` (warehouse_id, PROTECT)
- Many-to-One: `ReceiptTemporary` → `Supplier` (supplier_id, SET_NULL)
- One-to-One: `ReceiptTemporary` → `ReceiptPermanent` (converted_receipt_id)

**Business Logic:**
- Single-line document (item, warehouse, quantity stored directly in header)
- Status workflow: Draft → Awaiting inspection → Closed
- Can be converted to `ReceiptPermanent` (one-to-one relationship)
- When locked, creates `ItemSerial` records for serial-tracked items

#### inventory_receiptpermanent
**Purpose**: Permanent receipt document header (multi-line support)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| document_code | CharField(20) | Unique document code | Unique, Not null |
| document_date | Date | Document date | Default: today, Not null |
| notes | TextField | Document notes | Optional |
| requires_temporary_receipt | SmallInt | Requires temp receipt flag | Default: 0 |
| temporary_receipt_id | BigInt | Source temporary receipt | FK to inventory_receipttemporary, Optional, SET_NULL |
| temporary_receipt_code | CharField(20) | Temp receipt code (cached) | Optional |
| purchase_request_id | BigInt | Source purchase request | FK to inventory_purchaserequest, Optional, SET_NULL |
| purchase_request_code | CharField(20) | Purchase request code (cached) | Optional |
| warehouse_request_id | BigInt | Source warehouse request | FK to inventory_warehouserequest, Optional, SET_NULL |
| warehouse_request_code | CharField(20) | Warehouse request code (cached) | Optional |
| document_metadata | JSONField | Additional metadata | Default: {} |
| is_locked | SmallInt | Locked flag | Default: 0 |
| locked_at | DateTime | Lock timestamp | Optional |
| locked_by_id | BigInt | User who locked | FK to shared_user, Optional |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ReceiptPermanent` → `Company` (company_id)
- Many-to-One: `ReceiptPermanent` → `ReceiptTemporary` (temporary_receipt_id, SET_NULL)
- Many-to-One: `ReceiptPermanent` → `PurchaseRequest` (purchase_request_id, SET_NULL)
- Many-to-One: `ReceiptPermanent` → `WarehouseRequest` (warehouse_request_id, SET_NULL)
- One-to-Many: `ReceiptPermanent` → `ReceiptPermanentLine` (lines)
- One-to-One: `ReceiptPermanent` → `ReceiptTemporary` (via ReceiptTemporary.converted_receipt_id)

**Business Logic:**
- Header-only document; line items stored in `inventory_receiptpermanentline`
- Can be created from `ReceiptTemporary`, `PurchaseRequest`, or `WarehouseRequest`
- When locked, creates `ItemSerial` records for serial-tracked items
- Sorting: `-id, -document_date, document_code` (latest first)

#### inventory_receiptpermanentline
**Purpose**: Line items for permanent receipt documents

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| document_id | BigInt | Parent document | FK to inventory_receiptpermanent, Not null, CASCADE |
| item_id | BigInt | Item reference | FK to inventory_item, Not null, PROTECT |
| item_code | CharField(16) | Item code (cached) | Not null |
| warehouse_id | BigInt | Warehouse reference | FK to inventory_warehouse, Not null, PROTECT |
| warehouse_code | CharField(5) | Warehouse code (cached) | Not null |
| unit | CharField(30) | Unit (default unit) | Not null |
| quantity | Decimal(18,6) | Quantity (in default unit) | Not null |
| entered_unit | CharField(30) | User-entered unit | Optional |
| entered_quantity | Decimal(18,6) | User-entered quantity | Optional |
| entered_unit_price | Decimal(18,6) | User-entered unit price | Optional |
| entered_price_unit | CharField(30) | Unit for entered price | Optional |
| supplier_id | BigInt | Supplier reference | FK to inventory_supplier, Optional, SET_NULL |
| supplier_code | CharField(6) | Supplier code (cached) | Optional |
| unit_price | Decimal(18,6) | Unit price (in default unit) | Optional |
| currency | CharField(3) | Currency (IRT/IRR/USD) | Optional |
| tax_amount | Decimal(18,6) | Tax amount | Optional |
| discount_amount | Decimal(18,6) | Discount amount | Optional |
| total_amount | Decimal(18,6) | Total amount | Optional |
| line_notes | TextField | Line notes | Optional |
| sort_order | SmallInt | Display order | Default: 0 |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ReceiptPermanentLine` → `Company` (company_id)
- Many-to-One: `ReceiptPermanentLine` → `ReceiptPermanent` (document_id, CASCADE)
- Many-to-One: `ReceiptPermanentLine` → `Item` (item_id, PROTECT)
- Many-to-One: `ReceiptPermanentLine` → `Warehouse` (warehouse_id, PROTECT)
- Many-to-One: `ReceiptPermanentLine` → `Supplier` (supplier_id, SET_NULL)
- Many-to-Many: `ReceiptPermanentLine` ↔ `ItemSerial` (serials, via inventory_receiptpermanentline_serials)

**Business Logic:**
- Unit conversion: User enters `entered_quantity` and `entered_unit`, system converts to `quantity` and `unit` (default unit)
- Price conversion: User enters `entered_unit_price` in `entered_price_unit`, system may convert to `unit_price` in default unit
- When document is locked, serials are assigned to this line (Many-to-Many relationship)
- Minimum 1 line required per document
- **Warehouse Validation**: Warehouse must be in item's allowed warehouses list (enforced in form validation)

#### inventory_itemserial
**Purpose**: Serial number tracking for serialized items

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BigInt | Primary key | Auto-increment |
| company_id | BigInt | Company reference | FK to shared_company, Not null |
| company_code | CharField(8) | Company code (cached) | Optional |
| item_id | BigInt | Item reference | FK to inventory_item, Not null, PROTECT |
| item_code | CharField(16) | Item code (cached) | Not null |
| serial_number | CharField(100) | Serial number | Unique, Not null |
| current_status | CharField(30) | Current status (reserved/released/issued/consumed/returned) | Not null |
| current_location_type | CharField(30) | Location type (warehouse/document) | Optional |
| current_location_id | BigInt | Location ID | Optional |
| current_warehouse_id | BigInt | Current warehouse | FK to inventory_warehouse, Optional |
| receipt_document_id | BigInt | Receipt document | FK to inventory_receiptpermanent, Optional |
| receipt_document_code | CharField(20) | Receipt code (cached) | Optional |
| issue_document_id | BigInt | Issue document | Optional |
| issue_document_code | CharField(20) | Issue code (cached) | Optional |
| lot_id | BigInt | Lot reference | FK to inventory_itemlot, Optional |
| lot_code | CharField(30) | Lot code (cached) | Optional |
| metadata | JSONField | Additional metadata | Default: {} |
| created_at | DateTime | Creation timestamp | Auto-set |
| created_by_id | BigInt | Creator user | FK to shared_user, Optional |
| edited_at | DateTime | Last edit timestamp | Auto-update |
| edited_by_id | BigInt | Last editor user | FK to shared_user, Optional |

**Relationships:**
- Many-to-One: `ItemSerial` → `Company` (company_id)
- Many-to-One: `ItemSerial` → `Item` (item_id, PROTECT)
- Many-to-One: `ItemSerial` → `Warehouse` (current_warehouse_id, Optional)
- Many-to-One: `ItemSerial` → `ReceiptPermanent` (receipt_document_id, Optional)
- Many-to-One: `ItemSerial` → `ItemLot` (lot_id, Optional)
- Many-to-Many: `ItemSerial` ↔ `ReceiptPermanentLine` (via inventory_receiptpermanentline_serials)
- Many-to-Many: `ItemSerial` ↔ `IssuePermanentLine` (via inventory_issuepermanentline_serials)

**Business Logic:**
- Created automatically when a receipt document is locked (for serial-tracked items)
- Status workflow: reserved → released → issued/consumed → returned
- Each serial number is unique globally
- History tracked in `inventory_itemserialhistory`

---

## Entity Relationships (ER Diagram)

### Core Relationships

```
shared_company (1) ──< (N) inventory_item
                    └─< (N) inventory_warehouse
                    └─< (N) inventory_supplier
                    └─< (N) shared_companyunit
                    └─< (N) production_person
                    └─< (N) production_machine

inventory_itemtype (1) ──< (N) inventory_item
inventory_itemcategory (1) ──< (N) inventory_item
inventory_itemsubcategory (1) ──< (N) inventory_item

inventory_item (1) ──< (N) inventory_itemunit
                └─< (N) inventory_itemwarehouse
                └─< (N) inventory_receipttemporary
                └─< (N) inventory_receiptpermanentline
                └─< (N) inventory_issuepermanentline
                └─< (N) inventory_itemserial

inventory_warehouse (1) ──< (N) inventory_workline
                      └─< (N) inventory_receipttemporary
                      └─< (N) inventory_receiptpermanentline
                      └─< (N) inventory_issuepermanentline

inventory_supplier (1) ──< (N) inventory_receipttemporary
                     └─< (N) inventory_receiptpermanentline

inventory_receiptpermanent (1) ──< (N) inventory_receiptpermanentline
                            └─< (N) inventory_itemserial

inventory_receiptpermanentline (N) ──> (M) inventory_itemserial
                                    (Many-to-Many via inventory_receiptpermanentline_serials)

inventory_issuepermanent (1) ──< (N) inventory_issuepermanentline

inventory_issuepermanentline (N) ──> (M) inventory_itemserial
                                    (Many-to-Many via inventory_issuepermanentline_serials)

inventory_receipttemporary (1) ──> (1) inventory_receiptpermanent
                                  (One-to-One via converted_receipt_id)
```

### Relationship Types

1. **One-to-Many (1:N)**: 
   - `Company` → `Item`, `Warehouse`, `Supplier`
   - `ItemType` → `Item`
   - `ReceiptPermanent` → `ReceiptPermanentLine`
   - `IssuePermanent` → `IssuePermanentLine`

2. **Many-to-One (N:1)**:
   - `Item` → `Company`, `ItemType`, `ItemCategory`, `ItemSubcategory`
   - `ReceiptPermanentLine` → `ReceiptPermanent`, `Item`, `Warehouse`, `Supplier`

3. **Many-to-Many (N:M)**:
   - `ReceiptPermanentLine` ↔ `ItemSerial` (via junction table)
   - `IssuePermanentLine` ↔ `ItemSerial` (via junction table)
   - `Person` ↔ `CompanyUnit` (via production_person_company_units junction table)

4. **One-to-One (1:1)**:
   - `ReceiptTemporary` → `ReceiptPermanent` (converted_receipt_id)
   - `Person` → `User` (user_id)

---

## Operations and Related Tables

### Create Operations

#### Create Permanent Receipt
**URL**: `POST /inventory/receipts/permanent/create/`
**View**: `ReceiptPermanentCreateView`
**Tables Affected**:
1. **inventory_receiptpermanent** (header)
   - Insert new record with `document_code`, `document_date`, `company_id`
   - Auto-generate `document_code` if not provided
2. **inventory_receiptpermanentline** (lines)
   - Insert one or more line records
   - Each line: `item_id`, `warehouse_id`, `quantity`, `unit`, `entered_quantity`, `entered_unit`, `supplier_id`, `unit_price`
   - Validate: At least 1 line required
   - Unit conversion: Convert `entered_quantity`/`entered_unit` to `quantity`/`unit` (default unit)
   - Price conversion: Convert `entered_unit_price`/`entered_price_unit` to `unit_price` (if applicable)

**Business Logic**:
- If no valid lines submitted, delete the header record and show error
- Unit must be from item's `default_unit`, `primary_unit`, or `ItemUnit` conversions
- If item has no units configured, show error (no default unit added)

#### Create Temporary Receipt
**URL**: `POST /inventory/receipts/temporary/create/`
**View**: `ReceiptTemporaryCreateView`
**Tables Affected**:
1. **inventory_receipttemporary** (single record)
   - Insert record with `item_id`, `warehouse_id`, `quantity`, `unit`, `entered_quantity`, `entered_unit`, `supplier_id`
   - Status: `DRAFT` (0)
   - Unit conversion: Convert `entered_quantity`/`entered_unit` to `quantity`/`unit`

**Business Logic**:
- Single-line document (item/warehouse/quantity in header)
- Can be converted to `ReceiptPermanent` later

#### Create Item
**URL**: `POST /inventory/items/create/`
**View**: `ItemCreateView`
**Tables Affected**:
1. **inventory_item** (main record)
   - Insert with `type_id`, `category_id`, `subcategory_id`, `name`, `default_unit`, `primary_unit`
   - Auto-generate: `item_code`, `full_item_code`, `batch_number`, `sequence_segment`
2. **inventory_itemunit** (inline formset)
   - Insert unit conversion records
   - At least one unit conversion should exist (or `default_unit` must be set)

**Business Logic**:
- `item_code`: `user_segment` (2) + `sequence_segment` (5) = 7 digits
- `full_item_code`: `type_code` (3) + `category_code` (3) + `subcategory_code` (3) + `item_code` (7) = 16 digits
- `batch_number`: `MMYY-XXXXXX` format
- `sequence_segment`: Auto-increment per type/category/subcategory/user_segment

### Edit Operations

#### Edit Permanent Receipt
**URL**: `POST /inventory/receipts/permanent/<pk>/edit/`
**View**: `ReceiptPermanentUpdateView`
**Tables Affected**:
1. **inventory_receiptpermanent** (header)
   - Update `document_date`, `notes`, `document_metadata`
   - Cannot edit if `is_locked = 1`
2. **inventory_receiptpermanentline** (lines)
   - Update existing lines
   - Insert new lines
   - Delete lines (if `DELETE` flag set)
   - Validate: At least 1 line required after edit

**Business Logic**:
- Lock protection: If `is_locked = 1`, redirect with error
- Owner protection: Only `created_by` can edit (unless superuser)
- Line formset: Use `ReceiptPermanentLineFormSet` with `can_delete=True`, `min_num=1`

#### Edit Item
**URL**: `POST /inventory/items/<pk>/edit/`
**View**: `ItemUpdateView`
**Tables Affected**:
1. **inventory_item** (main record)
   - Update fields (except `item_code`, `full_item_code` - these are immutable)
2. **inventory_itemunit** (inline formset)
   - Update, insert, delete unit conversions

**Business Logic**:
- `item_code` and `full_item_code` cannot be changed after creation
- `type_id`, `category_id`, `subcategory_id` are PROTECT (cannot delete if items exist)

### Delete Operations

#### Delete Permanent Receipt
**URL**: `POST /inventory/receipts/permanent/<pk>/delete/`
**View**: `ReceiptPermanentDeleteView` (if exists)
**Tables Affected**:
1. **inventory_receiptpermanentline** (cascade)
   - Delete all lines (CASCADE)
2. **inventory_receiptpermanent** (header)
   - Delete header record
   - Cannot delete if `is_locked = 1`

**Business Logic**:
- Lock protection: Cannot delete locked documents
- Foreign key constraints: If `ItemSerial.receipt_document_id` references this receipt, deletion may fail

#### Delete Item
**URL**: `POST /inventory/items/<pk>/delete/`
**View**: `ItemDeleteView`
**Tables Affected**:
1. **inventory_itemunit** (cascade)
   - Delete all unit conversions
2. **inventory_itemwarehouse** (cascade)
   - Delete all warehouse assignments
3. **inventory_item** (main record)
   - Delete item
   - Cannot delete if referenced by receipts, issues, or serials (PROTECT)

**Business Logic**:
- PROTECT constraint: Cannot delete if `ReceiptTemporary.item_id`, `ReceiptPermanentLine.item_id`, `ItemSerial.item_id` reference this item

### Lock Operations

#### Lock Permanent Receipt
**URL**: `POST /inventory/receipts/permanent/<pk>/lock/`
**View**: `ReceiptPermanentLockView`
**Tables Affected**:
1. **inventory_receiptpermanent** (header)
   - Update: `is_locked = 1`, `locked_at = now()`, `locked_by_id = request.user.id`
2. **inventory_itemserial** (if serial-tracked items)
   - Insert serial records for each serial number assigned to lines
   - Set `current_status = 'released'`, `current_warehouse_id`, `receipt_document_id`

**Business Logic**:
- After locking, document cannot be edited or deleted
- For serial-tracked items, creates `ItemSerial` records
- For lot-tracked items, may create `ItemLot` records

---

## Business Logic and Workflows

### Warehouse Restriction Logic (Allowed Warehouses)

**Purpose**: Enforce strict warehouse restrictions for items - items can only be received in warehouses explicitly configured for them.

**Implementation**: 
- Item-Warehouse mapping stored in `inventory_itemwarehouse` table
- Each item can have multiple allowed warehouses
- First selected warehouse marked as primary (`is_primary=1`)

**Validation**:
1. **Form Level**: 
   - `_get_item_allowed_warehouses()`: Returns only explicitly configured warehouses for an item
   - `_set_warehouse_queryset()`: Filters warehouse dropdown to show only allowed warehouses
   - `clean_warehouse()`: Validates selected warehouse is in allowed list
   
2. **Client-Side (JavaScript)**:
   - `updateWarehouseChoices()`: Dynamically updates warehouse dropdown when item changes
   - API endpoint: `/inventory/api/item-allowed-warehouses/?item_id=X`
   
3. **Strict Enforcement**:
   - If no warehouses configured for item → Error: "این کالا هیچ انبار مجازی ندارد"
   - If warehouse selected not in allowed list → Error: "انبار انتخاب شده برای این کالا مجاز نیست"
   - No fallback to all warehouses (strict restriction)

**Business Logic**:
- When creating/editing item, user must select at least one allowed warehouse
- First selected warehouse is marked as primary (`is_primary=1`)
- Receipt documents can only use warehouses from item's allowed list
- Issue documents can only use warehouses from item's allowed list

**Database Table**: `inventory_itemwarehouse`
- `item_id` (FK to `inventory_item`)
- `warehouse_id` (FK to `inventory_warehouse`)
- `is_primary` (SmallInt): First warehouse is marked as primary
- `notes` (TextField): Optional notes

**Example**:
- Item: "Monitor" (id=11)
- Allowed Warehouses: Only "003 - IT" warehouse
- User tries to receive in "002 - Facilities" → **Error**: Warehouse not allowed

---

### Date Handling (Jalali/Gregorian Conversion)

**Purpose**: Display dates in Jalali (Persian) format in UI while storing in Gregorian (Miladi) format in database.

**Implementation**:
- **Storage**: All dates stored as Gregorian in database (`DateField`, `DateTimeField`)
- **Display**: Converted to Jalali format in templates using custom template tags
- **Input**: User enters Jalali dates, converted to Gregorian before saving

**Custom Widget**: `JalaliDateInput` (`inventory/widgets.py`)
- Extends Django's `DateInput`
- Template: `inventory/widgets/jalali_date_input.html`
- Methods:
  - `format_value()`: Converts Gregorian date to Jalali string for display
  - `value_from_datadict()`: Converts Jalali string from form to Gregorian date

**Custom Field**: `JalaliDateField` (`inventory/fields.py`)
- Extends Django's `DateField`
- Uses `JalaliDateInput` widget automatically

**Template Tags**: `jalali_tags` (`inventory/templatetags/jalali_tags.py`)
- `{% load jalali_tags %}` in templates
- `{{ date|jalali_date }}`: Format date as Jalali (e.g., "1404/08/24")
- `{{ date|jalali_datetime }}`: Format datetime as Jalali with time

**Utilities**: `inventory/utils/jalali.py`
- `gregorian_to_jalali()`: Convert Gregorian date/datetime to Jalali string
- `jalali_to_gregorian()`: Convert Jalali string to Gregorian date
- `today_jalali()`: Get today's date in Jalali format

**Forms Using Jalali Dates**:
- `ReceiptPermanentForm`: `document_date` field
- `ReceiptConsignmentForm`: `document_date` field
- `IssuePermanentForm`: `document_date` field
- `IssueConsumptionForm`: `document_date` field
- `IssueConsignmentForm`: `document_date` field
- `PurchaseRequestForm`: `request_date`, `needed_by_date` fields
- `WarehouseRequestForm`: `request_date`, `needed_by_date` fields

**Benefits**:
- Users see familiar Jalali calendar in UI
- Database maintains standard Gregorian dates
- Easy filtering and querying (no dual date fields needed)
- No additional database fields required

**Example**:
- User enters: "1404/08/24" (Jalali)
- Stored in DB: "2025-11-15" (Gregorian)
- Displayed in UI: "1404/08/24" (Jalali)

---

### Unit Conversion Logic

**Purpose**: Convert user-entered quantity/unit to system default unit

**Algorithm**: Graph Traversal (`_get_unit_factor` in `inventory/forms.py`)

1. **Direct Conversion**: Check if `ItemUnit` exists with `from_unit = entered_unit` and `to_unit = default_unit`
   - Factor = `to_quantity / from_quantity`

2. **Indirect Conversion**: If no direct conversion, traverse conversion graph
   - Build graph from `ItemUnit` records
   - Find shortest path from `entered_unit` to `default_unit`
   - Multiply factors along path

3. **Validation**: 
   - `entered_unit` must be in: `default_unit`, `primary_unit`, or any `ItemUnit.from_unit` or `ItemUnit.to_unit`
   - If item has no units configured, raise error (no default unit added)

4. **Storage**:
   - `entered_quantity`, `entered_unit`: User's input (preserved)
   - `quantity`, `unit`: Converted to default unit (for calculations)

**Example**:
- Item: "Screw" (default_unit = "EA")
- User enters: `entered_quantity = 2`, `entered_unit = "BOX"`
- Conversion: `ItemUnit`: 1 BOX = 100 EA
- Result: `quantity = 200`, `unit = "EA"`, `entered_quantity = 2`, `entered_unit = "BOX"`

### Price Conversion Logic

**Purpose**: Convert user-entered price/unit to system default unit price

**Algorithm**: Similar to quantity conversion

1. User enters: `entered_unit_price = 500000`, `entered_price_unit = "BOX"`
2. System converts to: `unit_price` in default unit ("EA")
3. If `entered_price_unit = entered_unit`, use direct conversion factor
4. If different, may require additional conversion

**Example**:
- Item: "Screw" (default_unit = "EA")
- User enters: `entered_unit_price = 500000`, `entered_price_unit = "BOX"`, `entered_quantity = 2`, `entered_unit = "BOX"`
- Conversion: 1 BOX = 100 EA
- Result: `unit_price = 5000` (per EA), `entered_unit_price = 500000` (per BOX)

### Receipt Workflow

#### Temporary Receipt Workflow
1. **Create** (`status = DRAFT`)
   - User creates temporary receipt
   - Single item, warehouse, quantity
   - Can be linked to supplier, purchase request

2. **Awaiting Inspection** (`status = AWAITING_INSPECTION`)
   - User submits for QC inspection
   - QC team inspects items
   - Results stored in `inspection_result` JSONField

3. **QC Approval**
   - QC approves: `qc_approved_by_id`, `qc_approved_at` set
   - Can be converted to permanent receipt

4. **Convert to Permanent**
   - User converts temporary receipt to permanent
   - Creates `ReceiptPermanent` with one-to-one link
   - `ReceiptTemporary.is_converted = 1`, `converted_receipt_id` set

5. **Close** (`status = CLOSED`)
   - Receipt closed/cancelled

#### Permanent Receipt Workflow
1. **Create**
   - User creates header + lines
   - Can be created from: Temporary Receipt, Purchase Request, Warehouse Request, or manually
   - Minimum 1 line required

2. **Edit**
   - User can add/edit/delete lines
   - Cannot edit if `is_locked = 1`
   - Only `created_by` can edit (unless superuser)

3. **Lock**
   - User locks document (`is_locked = 1`)
   - For serial-tracked items: Creates `ItemSerial` records
   - For lot-tracked items: May create `ItemLot` records
   - After locking, document is immutable

### Serial Number Assignment

**Purpose**: Assign serial numbers to receipt/issue lines for serial-tracked items

**Workflow**:
1. User creates receipt/issue document with serial-tracked item
2. User locks document
3. System creates `ItemSerial` records:
   - `item_id`: Item reference
   - `serial_number`: User-entered or auto-generated
   - `current_status`: "released" (for receipts) or "issued" (for issues)
   - `current_warehouse_id`: Warehouse from line
   - `receipt_document_id`: Receipt document (for receipts)
   - `issue_document_id`: Issue document (for issues)
4. Many-to-Many relationship: `ReceiptPermanentLine` ↔ `ItemSerial`
   - Junction table: `inventory_receiptpermanentline_serials`

**Line-based Assignment**:
- Serials are assigned per line, not per document
- Each line can have multiple serials
- Serials can be assigned via: `/inventory/receipts/permanent/<pk>/lines/<line_id>/serials/`

### Inventory Balance Calculation

**Purpose**: Calculate on-demand inventory balance (not stored in table)

**Algorithm**: (`inventory/inventory_balance.py`)

1. **Receipts** (increase stock):
   - `ReceiptPermanentLine`: `quantity` (in default unit) added to balance
   - `ReceiptTemporary`: `quantity` added (if converted or closed)
   - `ReceiptConsignmentLine`: `quantity` added (if ownership = "owned")

2. **Issues** (decrease stock):
   - `IssuePermanentLine`: `quantity` subtracted
   - `IssueConsumptionLine`: `quantity` subtracted
   - `IssueConsignmentLine`: `quantity` subtracted

3. **Stocktaking** (adjustments):
   - `StocktakingDeficit`: `quantity_adjusted` subtracted
   - `StocktakingSurplus`: `quantity_adjusted` added

4. **Formula**:
   ```
   Balance = Sum(Receipts) - Sum(Issues) + Sum(Stocktaking Adjustments)
   ```

5. **Grouping**:
   - By `item_id`, `warehouse_id`, `unit` (default unit)
   - Filtered by `company_id`

**API Endpoints**:

1. **Balance Calculation**: `/inventory/api/balance/`
   - Returns JSON with balance for each item/warehouse combination
   - Calculated on-demand (not stored)

2. **Item Allowed Units**: `/inventory/api/item-allowed-units/?item_id=X`
   - Returns JSON with allowed units for an item
   - Used by JavaScript to populate unit dropdown dynamically
   - Response: `{'units': [...], 'default_unit': 'EA'}`

3. **Item Allowed Warehouses**: `/inventory/api/item-allowed-warehouses/?item_id=X`
   - Returns JSON with allowed warehouses for an item
   - Used by JavaScript to populate warehouse dropdown dynamically
   - Response: `{'warehouses': [{'value': '1', 'label': '001 - Warehouse Name'}, ...]}`
   - **Important**: Returns empty list if no warehouses configured (strict restriction)

### Document Code Generation

**Pattern**: `{PREFIX}-{YYYYMM}-{XXXXXX}`

**Examples**:
- Permanent Receipt: `RCP-202401-000001`
- Temporary Receipt: `TRC-202401-000001`
- Issue Permanent: `ISS-202401-000001`
- Purchase Request: `PRQ-202401-000001`

**Algorithm**: (`inventory/utils/codes.py` - `generate_sequential_code`)
1. Get prefix from model configuration
2. Get current month: `YYYYMM`
3. Find last document with same prefix and month
4. Increment sequence: `XXXXXX` (6 digits, zero-padded)
5. Return: `{PREFIX}-{YYYYMM}-{XXXXXX}`

### Multi-Company (Multi-Tenant) Logic

**Purpose**: Isolate data per company

**Implementation**:
- All inventory models extend `CompanyScopedModel`
- `company_id` field in all tables
- Views filter by `request.session.get('active_company_id')`
- Unique constraints: `(company_id, field)` instead of just `(field)`

**Example**:
- `inventory_itemtype`: `UniqueConstraint(fields=("company", "public_code"))`
- Two companies can have `public_code = "001"` for different item types

### Lock Protection Logic

**Purpose**: Prevent modification of finalized documents

**Implementation**: `DocumentLockProtectedMixin` in `inventory/views.py`

**Checks**:
1. If `is_locked = 1`, redirect with error
2. Only `created_by` can edit (unless superuser)
3. Applied to: Edit, Delete operations

**Lock Operation**:
- Sets `is_locked = 1`, `locked_at = now()`, `locked_by_id = request.user.id`
- After locking, document is immutable

---

## Summary

This documentation provides a comprehensive mapping between:
- **UI Menus** → **URLs** → **Views** → **Models** → **Database Tables**
- **Field Descriptions** for all major tables
- **Entity Relationships** (ER diagram)
- **Operations** (Create, Edit, Delete, Lock) and affected tables
- **Business Logic** and workflows

**Key Points**:
1. Multi-company architecture with company-scoped data
2. Unit conversion system with graph traversal algorithm
3. Document-based transactions (receipts, issues) with header/line structure
4. Serial and lot tracking support
5. On-demand inventory balance calculation
6. Lock protection for finalized documents
7. Status workflows for temporary receipts and serials
8. Strict warehouse restrictions (allowed warehouses per item)
9. Jalali date display with Gregorian storage

For additional details, refer to:
- `inventory/models.py`: Model definitions
- `inventory/views.py`: View logic
- `inventory/forms.py`: Form validation and unit conversion
- `inventory/inventory_balance.py`: Balance calculation logic

