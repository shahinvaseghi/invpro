# Architecture Documentation

This document provides a comprehensive overview of the invproj platform architecture, including system design, module structure, data flow, and component relationships.

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Module Structure](#3-module-structure)
4. [Data Flow](#4-data-flow)
5. [Security Architecture](#5-security-architecture)
6. [Database Architecture](#6-database-architecture)
7. [API Architecture](#7-api-architecture)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Browser    │  │  Mobile App  │  │  API Client  │       │
│  │  (HTML/CSS/  │  │   (Future)   │  │  (Future)    │       │
│  │   JavaScript)│  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Django Application Layer                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              URL Routing (config/urls.py)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              View Layer (Views)                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │Inventory │  │Production│  │    QC    │           │   │
│  │  │  Views   │  │  Views   │  │  Views   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business Logic Layer                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Forms    │  │ Services │  │ Utils   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Model Layer (ORM)                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │Inventory │  │Production│  │  Shared  │           │   │
│  │  │  Models  │  │  Models  │  │  Models  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQL Queries
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              PostgreSQL Database                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │Inventory │  │Production│  │  Shared  │           │   │
│  │  │  Tables  │  │  Tables  │  │  Tables  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

- **Backend Framework**: Django 4.2
- **Database**: PostgreSQL (production), SQLite (development)
- **Language**: Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Authentication**: Django's built-in authentication with custom User model
- **Internationalization**: Django i18n with Persian (RTL) and English support
- **Date System**: Jalali (Persian) calendar with Gregorian storage

---

## 2. Architecture Diagram

### 2.1 Module Dependency Graph

```
┌─────────────┐
│   shared    │  (Base module - no dependencies)
│             │
│ - User      │
│ - Company   │
│ - Mixins    │
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
┌──────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐
│  inventory  │  │  production  │  │     qc      │
│             │  │               │  │             │
│ - Items     │  │ - BOM         │  │ - Inspection│
│ - Receipts  │  │ - Process     │  │             │
│ - Issues    │  │ - Personnel   │  │             │
│ - Warehouse │  │ - Machines    │  │             │
└─────────────┘  └───────┬───────┘  └──────┬──────┘
                         │                  │
                         │                  │
                    ┌────▼──────────────────▼────┐
                    │      ui (Templates)        │
                    │                             │
                    │ - Base templates            │
                    │ - Navigation                │
                    │ - Components                │
                    └─────────────────────────────┘
```

### 2.2 Request Flow Diagram

```
User Request
    │
    ▼
┌─────────────────┐
│  URL Router      │  (config/urls.py)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Middleware      │  (Authentication, CSRF, etc.)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  View            │  (Business logic)
│  - Permission    │
│  - Validation    │
│  - Processing    │
└────────┬─────────┘
         │
         ├─────────────────┬─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │  Form    │      │ Service │      │  Model   │
    │          │      │          │      │   ORM    │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┴─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Database    │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Template   │
                    │   Rendering  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  HTTP Response│
                    └──────────────┘
```

---

## 3. Module Structure

### 3.1 Shared Module

**Purpose**: Cross-cutting concerns and base functionality

**Key Components**:
- `models.py`: Base models (User, Company, CompanyUnit, AccessLevel)
- `mixins.py`: Reusable mixins (TimeStampedModel, CompanyScopedModel, etc.)
- `permissions.py`: Permission system definitions
- `context_processors.py`: Template context (active company, notifications)

**Dependencies**: None (base module)

### 3.2 Inventory Module

**Purpose**: Warehouse and inventory management

**Key Components**:
- `models.py`: Item, Warehouse, Receipt, Issue, Stocktaking models
- `views.py`: CRUD views for inventory operations
- `forms.py`: Form definitions for inventory documents
- `inventory_balance.py`: Balance calculation logic
- `services/serials.py`: Serial tracking service

**Dependencies**: `shared`

### 3.3 Production Module

**Purpose**: Production planning and manufacturing

**Key Components**:
- `models.py`: BOM, Process, Person, Machine, WorkLine
- `views.py`: Production management views
- `forms.py`: Production forms (BOM, Process, etc.)

**Dependencies**: `shared`, `inventory` (optional)

### 3.4 QC Module

**Purpose**: Quality control and inspection

**Key Components**:
- `models.py`: ReceiptInspection
- `views.py`: QC approval/rejection views

**Dependencies**: `shared`, `inventory`

### 3.5 UI Module

**Purpose**: Template rendering and navigation

**Key Components**:
- `views.py`: Dashboard and navigation views
- `templates/`: Base templates and components

**Dependencies**: All modules

---

## 4. Data Flow

### 4.1 Multi-Company Data Isolation

```
User Login
    │
    ▼
┌─────────────────┐
│  Select Company  │  (UserCompanyAccess)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Session Store   │  (active_company_id)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  All Queries     │  Filter by company_id
│  Filtered by     │
│  Company         │
└─────────────────┘
```

### 4.2 Document Workflow

```
Document Creation
    │
    ▼
┌─────────────────┐
│  Draft Status   │
│  - Editable     │
│  - Deletable    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lock Document  │
│  - Not Editable │
│  - Not Deletable│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Processed      │
│  - Final State  │
└─────────────────┘
```

### 4.3 Inventory Balance Calculation

```
Stocktaking Record (Baseline)
    │
    ▼
┌─────────────────┐
│  Calculate      │
│  Movements      │
│  After Baseline │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Balance =      │
│  Baseline +     │
│  Receipts -     │
│  Issues         │
└─────────────────┘
```

---

## 5. Security Architecture

### 5.1 Authentication Flow

```
User Request
    │
    ▼
┌─────────────────┐
│  LoginRequired  │  (Middleware)
│  Mixin          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Check Session │
│  - Valid?        │
│  - Active?     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    ▼         ▼
┌──────┐  ┌──────┐
│Allow │  │Redirect│
│      │  │to Login│
└──────┘  └──────┘
```

### 5.2 Permission System

```
User Request
    │
    ▼
┌─────────────────┐
│  Feature        │
│  Permission     │
│  Required Mixin │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Check Access   │
│  Level          │
│  - UserCompany  │
│    Access       │
│  - AccessLevel  │
│    Permission   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
  Allow    Deny
    │         │
    ▼         ▼
┌──────┐  ┌──────┐
│Allow │  │403   │
│      │  │Error │
└──────┘  └──────┘
```

### 5.3 Data Access Control

- **Company Scoping**: All queries filtered by `company_id` from session
- **Row-Level Security**: Users can only access data from their assigned companies
- **Document Locking**: Locked documents cannot be modified
- **Owner Restrictions**: Some documents can only be edited by creator

---

## 6. Database Architecture

### 6.1 Table Naming Convention

- **Shared Module**: `invproj_*` prefix
- **Inventory Module**: `inventory_*` prefix
- **Production Module**: `production_*` prefix
- **QC Module**: `qc_*` prefix

### 6.2 Key Relationships

```
Company (1) ──────< (N) UserCompanyAccess
    │
    ├───< (N) Item
    ├───< (N) Warehouse
    ├───< (N) Receipt
    ├───< (N) Issue
    └───< (N) BOM

Item (1) ──────< (N) ItemSerial
    │
    ├───< (N) ItemUnit
    ├───< (N) ItemWarehouse
    └───< (N) BOMMaterial

BOM (1) ──────< (N) BOMMaterial
    │
    └───< (N) Process

ReceiptPermanent (1) ──────< (N) ReceiptPermanentLine
    │
    └───< (1) ReceiptTemporary (optional)
```

### 6.3 Audit Trail

All models inherit from:
- `TimeStampedModel`: `created_at`, `created_by`, `edited_at`, `edited_by`
- `CompanyScopedModel`: `company`, `company_code`
- `MetadataModel`: `metadata` (JSON field for extensibility)

---

## 7. API Architecture

### 7.1 API Endpoints Structure

All API endpoints are JSON-based and follow RESTful principles:

```
/api/item-units/              GET  - Get units for an item
/api/item-allowed-warehouses/ GET  - Get allowed warehouses for an item
/api/filtered-categories/     GET  - Get categories filtered by type
/api/filtered-subcategories/  GET  - Get subcategories filtered by category
/api/filtered-items/          GET  - Get items filtered by type/category/subcategory
/api/item-available-serials/ GET  - Get available serials for an item
/api/warehouse-work-lines/    GET  - Get work lines for a warehouse
/api/temporary-receipt-data/  GET  - Get temporary receipt information
/api/serial/<id>/update-secondary/ POST - Update secondary serial code
```

### 7.2 API Response Format

**Success Response**:
```json
{
  "units": [...],
  "default_unit": "EA"
}
```

**Error Response**:
```json
{
  "error": "Error message",
  "status": 400
}
```

### 7.3 Authentication

- All API endpoints require authentication (`@login_required`)
- Company context from session (`active_company_id`)
- Permission checks via `FeaturePermissionRequiredMixin` where applicable

---

## 8. Deployment Architecture

### 8.1 Production Deployment

```
┌─────────────────┐
│   Load Balancer │
│   (Nginx)       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌───▼───┐
│ Django │ │ Django │  (Multiple instances)
│ App 1  │ │ App 2  │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
│   Database      │
└─────────────────┘
```

### 8.2 Static Files

- **Development**: Served by Django `runserver`
- **Production**: Served by Nginx or CDN
- **Collectstatic**: `python manage.py collectstatic`

---

## 9. Future Architecture Considerations

### 9.1 Microservices Migration Path

Current monolithic structure can be split into:

```
┌─────────────┐
│  API Gateway│
└──────┬──────┘
       │
   ┌───┴───┬──────────┬──────────┐
   │       │          │          │
┌──▼──┐ ┌──▼──┐  ┌───▼───┐  ┌───▼───┐
│Inv  │ │Prod │  │  QC   │  │Shared │
│Svc  │ │Svc  │  │ Svc   │  │ Svc   │
└─────┘ └─────┘  └───────┘  └───────┘
```

### 9.2 Caching Strategy

- **Redis**: Session storage, cache
- **Query Cache**: Frequently accessed data
- **Template Cache**: Rendered templates

### 9.3 Message Queue

- **Celery**: Background tasks
- **RabbitMQ/Redis**: Message broker

---

## 10. Best Practices

### 10.1 Code Organization

- **Separation of Concerns**: Models, Views, Forms in separate files
- **DRY Principle**: Reusable mixins and base classes
- **Single Responsibility**: Each class has one clear purpose

### 10.2 Database

- **Indexes**: On foreign keys and frequently queried fields
- **Constraints**: Unique constraints for business rules
- **Migrations**: Version controlled and reversible

### 10.3 Security

- **Input Validation**: All user input validated
- **SQL Injection**: ORM prevents SQL injection
- **XSS Protection**: Template auto-escaping
- **CSRF Protection**: Django CSRF middleware

---

**Last Updated**: 2025-11-21

