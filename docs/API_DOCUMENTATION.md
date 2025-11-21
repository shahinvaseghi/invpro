# API Documentation

This document provides comprehensive documentation for all API endpoints in the invproj platform.

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Response Format](#3-response-format)
4. [Error Handling](#4-error-handling)
5. [API Endpoints](#5-api-endpoints)
   - [Item APIs](#51-item-apis)
   - [Category & Subcategory APIs](#52-category--subcategory-apis)
   - [Warehouse APIs](#53-warehouse-apis)
   - [Serial APIs](#54-serial-apis)
   - [Receipt APIs](#55-receipt-apis)
   - [Inventory Balance APIs](#56-inventory-balance-apis)

---

## 1. Overview

All API endpoints are JSON-based and follow RESTful principles. They are designed to support dynamic form interactions and data filtering in the web interface.

**Base URL**: `/fa/inventory/api/` (for inventory APIs)

**Content-Type**: `application/json`

**Authentication**: All endpoints require user authentication via Django session.

---

## 2. Authentication

All API endpoints require:
- User must be logged in (`@login_required` decorator)
- Active company must be set in session (`active_company_id`)
- User must have access to the active company

**Unauthorized Response** (401):
```json
{
  "error": "Unauthorized"
}
```

**No Active Company Response** (400):
```json
{
  "error": "No active company"
}
```

---

## 3. Response Format

### Success Response

All successful responses return JSON with relevant data:

```json
{
  "units": [...],
  "default_unit": "EA"
}
```

### Error Response

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (missing parameters, validation errors)
- `401`: Unauthorized (not logged in)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

---

## 4. Error Handling

All endpoints use try-except blocks to catch exceptions and return appropriate error responses:

```json
{
  "error": "Detailed error message",
  "status": 500
}
```

Common error scenarios:
- Missing required parameters → `400 Bad Request`
- Resource not found → `404 Not Found`
- Permission denied → `401 Unauthorized`
- Server errors → `500 Internal Server Error`

---

## 5. API Endpoints

### 5.1 Item APIs

#### 5.1.1 Get Item Allowed Units

**Endpoint**: `GET /fa/inventory/api/item-allowed-units/`

**Description**: Returns list of allowed units for an item (primary unit + conversion units).

**Query Parameters**:
- `item_id` (required): Item ID

**Response**:
```json
{
  "units": [
    {"value": "EA", "label": "Each"},
    {"value": "1", "label": "Box (10 EA = 1 Box)"}
  ],
  "default_unit": "EA"
}
```

**Example**:
```bash
GET /fa/inventory/api/item-allowed-units/?item_id=123
```

---

#### 5.1.2 Get Item Units (Detailed)

**Endpoint**: `GET /fa/inventory/api/item-units/`

**Description**: Returns detailed unit information for an item, including base unit and conversion units. Also returns item type, category, and subcategory IDs for auto-filling forms.

**Query Parameters**:
- `item_id` (required): Item ID

**Response**:
```json
{
  "units": [
    {
      "value": "base_EA",
      "label": "EA (واحد اصلی)",
      "is_base": true,
      "unit_name": "EA"
    },
    {
      "value": "1",
      "label": "Box (10 EA = 1 Box)",
      "is_base": false,
      "unit_name": "Box"
    }
  ],
  "item_type_id": 1,
  "item_type_name": "Raw Material",
  "category_id": 2,
  "subcategory_id": 3
}
```

**Example**:
```bash
GET /fa/inventory/api/item-units/?item_id=123
```

---

#### 5.1.3 Get Item Allowed Warehouses

**Endpoint**: `GET /fa/inventory/api/item-allowed-warehouses/`

**Description**: Returns list of warehouses where an item can be stored (based on ItemWarehouse configuration).

**Query Parameters**:
- `item_id` (required): Item ID

**Response**:
```json
{
  "warehouses": [
    {"value": "1", "label": "00001 - Main Warehouse"},
    {"value": "2", "label": "00002 - Secondary Warehouse"}
  ]
}
```

**Note**: If no warehouses are configured for an item, returns empty array. This enforces strict warehouse restrictions.

**Example**:
```bash
GET /fa/inventory/api/item-allowed-warehouses/?item_id=123
```

---

#### 5.1.4 Get Filtered Items

**Endpoint**: `GET /fa/inventory/api/filtered-items/`

**Description**: Returns items filtered by type, category, and/or subcategory.

**Query Parameters**:
- `type_id` (optional): Filter by item type
- `category_id` (optional): Filter by category
- `subcategory_id` (optional): Filter by subcategory

**Response**:
```json
{
  "items": [
    {
      "value": "123",
      "label": "001-002-003-0001 - Item Name",
      "type_id": "1",
      "category_id": "2",
      "subcategory_id": "3"
    }
  ]
}
```

**Example**:
```bash
GET /fa/inventory/api/filtered-items/?type_id=1&category_id=2&subcategory_id=3
```

---

### 5.2 Category & Subcategory APIs

#### 5.2.1 Get Filtered Categories

**Endpoint**: `GET /fa/inventory/api/filtered-categories/`

**Description**: Returns categories that contain items of a specific type (or all categories with items if no type specified).

**Query Parameters**:
- `type_id` (optional): Filter categories by item type

**Response**:
```json
{
  "categories": [
    {"value": "1", "label": "Raw Materials"},
    {"value": "2", "label": "Components"}
  ]
}
```

**Example**:
```bash
GET /fa/inventory/api/filtered-categories/?type_id=1
```

---

#### 5.2.2 Get Filtered Subcategories

**Endpoint**: `GET /fa/inventory/api/filtered-subcategories/`

**Description**: Returns subcategories filtered by category (and optionally by type).

**Query Parameters**:
- `category_id` (required): Filter by category
- `type_id` (optional): Optional type filter (hint only, doesn't require items to exist)

**Response**:
```json
{
  "subcategories": [
    {"value": "1", "label": "25"},
    {"value": "2", "label": "27"}
  ]
}
```

**Note**: Returns all subcategories of the given category, even if they don't have items yet. This allows creating items in new subcategories.

**Example**:
```bash
GET /fa/inventory/api/filtered-subcategories/?category_id=2&type_id=1
```

---

### 5.3 Warehouse APIs

#### 5.3.1 Get Warehouse Work Lines

**Endpoint**: `GET /fa/inventory/api/warehouse-work-lines/`

**Description**: Returns work lines associated with a warehouse (from production module).

**Query Parameters**:
- `warehouse_id` (required): Warehouse ID

**Response**:
```json
{
  "work_lines": [
    {"value": "1", "label": "00001 · Production Line 1"},
    {"value": "2", "label": "00002 · Production Line 2"}
  ],
  "count": 2
}
```

**Note**: Returns empty array if production module is not installed.

**Example**:
```bash
GET /fa/inventory/api/warehouse-work-lines/?warehouse_id=1
```

---

### 5.4 Serial APIs

#### 5.4.1 Get Item Available Serials

**Endpoint**: `GET /fa/inventory/api/item-available-serials/`

**Description**: Returns available serial numbers for an item in a specific warehouse.

**Query Parameters**:
- `item_id` (required): Item ID
- `warehouse_id` (required): Warehouse ID

**Response**:
```json
{
  "serials": [
    {
      "value": "1",
      "label": "SER-202511-000001",
      "status": "available"
    }
  ],
  "has_lot_tracking": true,
  "count": 1
}
```

**Note**: Only returns serials with `AVAILABLE` status (excludes `RESERVED`, `ISSUED`, etc.).

**Example**:
```bash
GET /fa/inventory/api/item-available-serials/?item_id=123&warehouse_id=1
```

---

#### 5.4.2 Update Serial Secondary Code

**Endpoint**: `POST /fa/inventory/api/serial/<serial_id>/update-secondary/`

**Description**: Updates the secondary serial code for a serial number.

**URL Parameters**:
- `serial_id` (required): Serial ID

**Request Body**:
```json
{
  "secondary_serial_code": "USER-INPUT-CODE"
}
```

**Response**:
```json
{
  "success": true
}
```

**Error Response**:
```json
{
  "error": "Error message",
  "success": false
}
```

**Example**:
```bash
POST /fa/inventory/api/serial/123/update-secondary/
Content-Type: application/json

{
  "secondary_serial_code": "CUSTOM-001"
}
```

---

### 5.5 Receipt APIs

#### 5.5.1 Get Temporary Receipt Data

**Endpoint**: `GET /fa/inventory/api/temporary-receipt-data/`

**Description**: Returns temporary receipt data for auto-filling permanent receipt lines.

**Query Parameters**:
- `temporary_receipt_id` (required): Temporary receipt ID

**Response**:
```json
{
  "item_id": 123,
  "item_code": "001-002-003-0001",
  "item_name": "Item Name",
  "warehouse_id": 1,
  "warehouse_code": "00001",
  "warehouse_name": "Main Warehouse",
  "quantity": "10.000000",
  "entered_quantity": "10.000000",
  "unit": "EA",
  "entered_unit": "EA",
  "supplier_id": 1,
  "supplier_code": "500001",
  "supplier_name": "Supplier Name"
}
```

**Example**:
```bash
GET /fa/inventory/api/temporary-receipt-data/?temporary_receipt_id=456
```

---

### 5.6 Inventory Balance APIs

#### 5.6.1 Get Inventory Balance

**Endpoint**: `GET /fa/inventory/inventory-balance/api/`

**Description**: Calculates and returns inventory balance for an item in a warehouse.

**Query Parameters**:
- `warehouse_id` (required): Warehouse ID
- `item_id` (required): Item ID
- `as_of_date` (optional): Calculate balance as of this date (ISO format: YYYY-MM-DD)

**Response**:
```json
{
  "item_id": 123,
  "warehouse_id": 1,
  "quantity": "150.000000",
  "unit": "EA",
  "as_of_date": "2025-11-21",
  "baseline_date": "2025-11-01",
  "baseline_quantity": "100.000000",
  "transactions": [
    {
      "date": "2025-11-05",
      "type": "receipt",
      "quantity": "50.000000",
      "document_code": "PRM-202511-000001"
    }
  ],
  "total_receipts": "50.000000",
  "total_issues": "0.000000",
  "current_balance": "150.000000"
}
```

**Example**:
```bash
GET /fa/inventory/inventory-balance/api/?warehouse_id=1&item_id=123&as_of_date=2025-11-21
```

---

## 6. Usage Examples

### 6.1 JavaScript Example - Cascading Dropdowns

```javascript
// Get categories when type is selected
function loadCategories(typeId) {
  fetch(`/fa/inventory/api/filtered-categories/?type_id=${typeId}`)
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('category');
      select.innerHTML = '<option value="">--- انتخاب کنید ---</option>';
      data.categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.value;
        option.textContent = cat.label;
        select.appendChild(option);
      });
    });
}

// Get subcategories when category is selected
function loadSubcategories(categoryId) {
  fetch(`/fa/inventory/api/filtered-subcategories/?category_id=${categoryId}`)
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('subcategory');
      select.innerHTML = '<option value="">--- انتخاب کنید ---</option>';
      data.subcategories.forEach(subcat => {
        const option = document.createElement('option');
        option.value = subcat.value;
        option.textContent = subcat.label;
        select.appendChild(option);
      });
    });
}
```

### 6.2 JavaScript Example - Get Item Units

```javascript
function loadItemUnits(itemId) {
  fetch(`/fa/inventory/api/item-units/?item_id=${itemId}`)
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('unit');
      select.innerHTML = '';
      data.units.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.unit_name; // Use unit_name for form submission
        option.textContent = unit.label;
        if (unit.is_base) {
          option.selected = true; // Select base unit by default
        }
        select.appendChild(option);
      });
      
      // Auto-fill material type if in BOM form
      if (data.item_type_id) {
        document.getElementById('id_material_type').value = data.item_type_id;
      }
    });
}
```

### 6.3 JavaScript Example - Update Serial Secondary Code

```javascript
function updateSerialSecondaryCode(serialId, secondaryCode) {
  fetch(`/fa/inventory/api/serial/${serialId}/update-secondary/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      secondary_serial_code: secondaryCode
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('کد سریال ثانویه با موفقیت ذخیره شد.');
      } else {
        alert('خطا: ' + data.error);
      }
    });
}
```

---

## 7. Rate Limiting

Currently, there are no rate limits on API endpoints. However, for production deployment, consider implementing:
- Rate limiting per user/IP
- Request throttling
- Caching for frequently accessed data

---

## 8. Versioning

Currently, all APIs are unversioned. For future API changes, consider:
- URL versioning: `/api/v1/...`
- Header versioning: `X-API-Version: 1`
- Query parameter versioning: `?version=1`

---

## 9. Testing

### 9.1 Using cURL

```bash
# Get item units
curl -X GET "http://localhost:8000/fa/inventory/api/item-units/?item_id=123" \
  -H "Cookie: sessionid=your_session_id"

# Update serial secondary code
curl -X POST "http://localhost:8000/fa/inventory/api/serial/123/update-secondary/" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_id" \
  -H "X-CSRFToken: your_csrf_token" \
  -d '{"secondary_serial_code": "CUSTOM-001"}'
```

### 9.2 Using Python Requests

```python
import requests

session = requests.Session()
# Login first
session.post('http://localhost:8000/login/', data={
    'username': 'user',
    'password': 'pass'
})

# Get item units
response = session.get('http://localhost:8000/fa/inventory/api/item-units/', params={
    'item_id': 123
})
data = response.json()
print(data['units'])
```

---

## 10. Error Codes

| HTTP Code | Description | Example |
|----------|-------------|---------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Missing required parameter |
| 401 | Unauthorized | User not logged in |
| 404 | Not Found | Item not found |
| 500 | Internal Server Error | Database error, exception |

---

**Last Updated**: 2025-11-21

