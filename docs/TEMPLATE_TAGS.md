# Template Tags Documentation

This document provides comprehensive documentation for all custom template tags and filters used in the invproj platform.

## Table of Contents

1. [Overview](#1-overview)
2. [Jalali Date Tags](#2-jalali-date-tags)
3. [Access Control Tags](#3-access-control-tags)
4. [JSON Filters](#4-json-filters)
5. [Usage Examples](#5-usage-examples)

---

## 1. Overview

Template tags are custom Django template filters and tags that extend the template language with custom functionality. All template tags are organized by module:

- **Inventory Module**: Jalali date conversion tags (`inventory/templatetags/jalali_tags.py`)
- **Shared Module**: Access control and JSON filters (`shared/templatetags/`)

---

## 2. Jalali Date Tags

**Module**: `inventory/templatetags/jalali_tags.py`

**Purpose**: Convert Gregorian dates to Jalali (Persian) dates for display in templates.

### 2.1 `jalali_date` Filter

**Description**: Converts a Gregorian date to Jalali date string.

**Usage**:
```django
{{ receipt.document_date|jalali_date }}
{{ receipt.document_date|jalali_date:"%Y/%m/%d" }}
{{ receipt.document_date|jalali_date:"%d %B %Y" }}
```

**Parameters**:
- `value`: Gregorian date (date, datetime, or ISO string)
- `format_str` (optional): Output format string (default: `'%Y/%m/%d'`)

**Returns**: Jalali date string (e.g., `'1403/09/15'`) or empty string if input is None/invalid

**Format Codes**:
- `%Y`: 4-digit year (e.g., `1403`)
- `%m`: 2-digit month (e.g., `09`)
- `%d`: 2-digit day (e.g., `15`)
- `%B`: Full month name (e.g., `آذر`)

**Examples**:
```django
{# Default format: YYYY/MM/DD #}
{{ receipt.document_date|jalali_date }}
{# Output: 1403/09/15 #}

{# Custom format #}
{{ receipt.document_date|jalali_date:"%Y-%m-%d" }}
{# Output: 1403-09-15 #}

{# Long format with month name #}
{{ receipt.document_date|jalali_date:"%d %B %Y" }}
{# Output: 15 آذر 1403 #}
```

**Notes**:
- Automatically handles `datetime` objects by extracting the date part
- Returns empty string for `None` or invalid dates
- Uses `jdatetime` library for conversion

---

### 2.2 `jalali_date_short` Filter

**Description**: Short format Jalali date (equivalent to `jalali_date` with default format).

**Usage**:
```django
{{ receipt.document_date|jalali_date_short }}
```

**Returns**: Jalali date in `YYYY/MM/DD` format (e.g., `'1403/09/15'`)

**Example**:
```django
{{ receipt.document_date|jalali_date_short }}
{# Output: 1403/09/15 #}
```

---

### 2.3 `jalali_date_long` Filter

**Description**: Long format Jalali date with Persian month name.

**Usage**:
```django
{{ receipt.document_date|jalali_date_long }}
```

**Returns**: Jalali date with month name (e.g., `'15 آذر 1403'`)

**Example**:
```django
{{ receipt.document_date|jalali_date_long }}
{# Output: 15 آذر 1403 #}
```

**Month Names**:
- فروردین, اردیبهشت, خرداد, تیر, مرداد, شهریور
- مهر, آبان, آذر, دی, بهمن, اسفند

---

### 2.4 `jalali_datetime` Filter

**Description**: Converts Gregorian datetime to Jalali datetime string (includes time).

**Usage**:
```django
{{ serial.created_at|jalali_datetime }}
{{ serial.created_at|jalali_datetime:"%Y/%m/%d %H:%M:%S" }}
```

**Parameters**:
- `value`: Gregorian datetime object
- `format_str` (optional): Output format (default: `'%Y/%m/%d %H:%M'`)

**Returns**: Jalali date + time string (e.g., `'1403/09/15 14:30'`)

**Example**:
```django
{{ serial.created_at|jalali_datetime }}
{# Output: 1403/09/15 14:30 #}

{{ serial.created_at|jalali_datetime:"%Y/%m/%d %H:%M:%S" }}
{# Output: 1403/09/15 14:30:45 #}
```

**Notes**:
- Extracts both date and time from datetime objects
- Time part remains in 24-hour format
- If value is a date (not datetime), only date part is converted

---

## 3. Access Control Tags

**Module**: `shared/templatetags/access_tags.py`

**Purpose**: Check user permissions for features and actions in templates.

### 3.1 `feature_allowed` Filter

**Description**: Checks if user has permission for a specific feature and action.

**Usage**:
```django
{% load access_tags %}

{{ user_feature_permissions|feature_allowed:"inventory.receipts.permanent" }}
{{ user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" }}
{{ user_feature_permissions|feature_allowed:"inventory.receipts.permanent:approve" }}
```

**Parameters**:
- `user_permissions`: Dictionary of user feature permissions (from context processor)
- `args`: Feature code with optional action (format: `"feature_code[:action]"`)

**Returns**: `True` if user has permission, `False` otherwise

**Action Values**:
- `view` (default): Check view permission
- `view_all`: Check view all permission
- `view_own`: Check view own permission
- `create`: Check create permission
- `edit_own`: Check edit own permission
- `delete_own`: Check delete own permission
- `approve`: Check approve permission
- `lock_own`: Check lock own permission
- etc.

**Examples**:
```django
{% load access_tags %}

{# Check if user can view permanent receipts #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent" %}
  <a href="{% url 'inventory:receipt_permanent_list' %}">رسیدهای دائم</a>
{% endif %}

{# Check if user can create permanent receipts #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
  <a href="{% url 'inventory:receipt_permanent_create' %}" class="btn btn-primary">
    ایجاد رسید دائم
  </a>
{% endif %}

{# Check if user can approve permanent receipts #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:approve" %}
  <button type="submit" class="btn btn-success">تایید</button>
{% endif %}
```

**Notes**:
- Feature codes use dot notation (e.g., `inventory.receipts.permanent`)
- If action is omitted, defaults to `view`
- Superusers automatically have all permissions
- Returns `False` if `user_permissions` is empty or `None`

---

## 4. JSON Filters

**Module**: `shared/templatetags/json_filters.py`

**Purpose**: Convert Python objects to JSON strings for use in templates (especially JavaScript).

### 4.1 `to_json` Filter

**Description**: Converts a Python object (dict, list, etc.) to JSON string.

**Usage**:
```django
{% load json_filters %}

{{ field_config|to_json }}
{{ form_data|to_json }}
```

**Parameters**:
- `value`: Python object (dict, list, string, or None)

**Returns**: JSON string representation of the object

**Examples**:
```django
{% load json_filters %}

{# Convert dict to JSON #}
<script>
  const fieldConfig = {{ field_config|to_json }};
  console.log(fieldConfig);
</script>

{# Convert list to JSON #}
<script>
  const items = {{ items_list|to_json }};
  items.forEach(item => {
    console.log(item.name);
  });
</script>

{# Already a JSON string (validated and returned as-is) #}
{{ json_string|to_json }}
```

**Behavior**:
- If `value` is `None`, returns `'{}'`
- If `value` is already a valid JSON string, returns it as-is
- If `value` is a dict/list, converts to JSON with `ensure_ascii=False` (supports Persian characters)
- If conversion fails, returns `'{}'`

**Error Handling**:
- Catches `TypeError` and `ValueError` exceptions
- Returns empty JSON object `'{}'` on error

**Example in Template**:
```django
{% load json_filters %}

<script>
  // Pass Python dict to JavaScript
  const config = {{ ticket_template.field_config|to_json }};
  
  // Use in JavaScript
  if (config.show_date_picker) {
    initializeDatePicker();
  }
</script>
```

---

## 5. Usage Examples

### 5.1 Complete Template Example - Receipt List

```django
{% extends "inventory/base.html" %}
{% load i18n %}
{% load jalali_tags %}
{% load access_tags %}

{% block inventory_content %}
  <h1>{% trans "Permanent Receipts" %}</h1>
  
  {# Show create button only if user has permission #}
  {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
    <a href="{% url 'inventory:receipt_permanent_create' %}" class="btn btn-primary">
      {% trans "Create Receipt" %}
    </a>
  {% endif %}
  
  <table class="data-table">
    <thead>
      <tr>
        <th>{% trans "Code" %}</th>
        <th>{% trans "Date" %}</th>
        <th>{% trans "Status" %}</th>
        <th>{% trans "Actions" %}</th>
      </tr>
    </thead>
    <tbody>
      {% for receipt in receipts %}
        <tr>
          <td>{{ receipt.document_code }}</td>
          <td>{{ receipt.document_date|jalali_date_long }}</td>
          <td>
            {% if receipt.is_locked %}
              <span class="badge badge-locked">{% trans "Locked" %}</span>
            {% else %}
              <span class="badge badge-draft">{% trans "Draft" %}</span>
            {% endif %}
          </td>
          <td>
            {# Show edit button only if user can edit own receipts #}
            {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:edit_own" %}
              <a href="{% url 'inventory:receipt_permanent_edit' receipt.pk %}">
                {% trans "Edit" %}
              </a>
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock %}
```

### 5.2 JavaScript Integration Example

```django
{% load json_filters %}

<script>
  // Pass Python data to JavaScript
  const receiptData = {{ receipt_data|to_json }};
  
  // Use in JavaScript
  document.addEventListener('DOMContentLoaded', function() {
    console.log('Receipt Code:', receiptData.document_code);
    console.log('Date:', receiptData.document_date);
  });
</script>
```

### 5.3 Conditional Rendering Based on Permissions

```django
{% load access_tags %}

<div class="action-buttons">
  {# Always show view button if user can view #}
  {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent" %}
    <a href="{% url 'inventory:receipt_permanent_list' %}" class="btn btn-secondary">
      {% trans "View All" %}
    </a>
  {% endif %}
  
  {# Show create button only if user can create #}
  {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
    <a href="{% url 'inventory:receipt_permanent_create' %}" class="btn btn-primary">
      {% trans "Create" %}
    </a>
  {% endif %}
  
  {# Show approve button only if user can approve #}
  {% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:approve" %}
    <button type="submit" class="btn btn-success">
      {% trans "Approve" %}
    </button>
  {% endif %}
</div>
```

---

## 6. Loading Template Tags

To use template tags in your templates, you must load them first:

```django
{% load jalali_tags %}      {# For Jalali date filters #}
{% load access_tags %}      {# For permission checks #}
{% load json_filters %}     {# For JSON conversion #}
```

You can load multiple tags in one line:

```django
{% load jalali_tags access_tags json_filters %}
```

---

## 7. Related Files

- `inventory/templatetags/jalali_tags.py`: Jalali date conversion filters
- `inventory/utils/jalali.py`: Core Jalali date utility functions
- `shared/templatetags/access_tags.py`: Permission checking filter
- `shared/templatetags/json_filters.py`: JSON conversion filter
- `shared/utils/permissions.py`: Permission resolution logic
- `shared/context_processors.py`: Provides `user_feature_permissions` to templates

---

## 8. Troubleshooting

### Jalali Date Not Displaying

**Problem**: Date shows as empty or Gregorian format

**Solutions**:
1. Ensure `{% load jalali_tags %}` is at the top of template
2. Check that date value is not `None`
3. Verify `jdatetime` library is installed: `pip install jdatetime`
4. Check date format is valid

### Permission Check Always Returns False

**Problem**: `feature_allowed` always returns `False`

**Solutions**:
1. Ensure `user_feature_permissions` is in context (from `shared.context_processors.active_company`)
2. Check feature code spelling (must match `FEATURE_PERMISSION_MAP` in `shared/permissions.py`)
3. Verify user has `AccessLevelPermission` records in database
4. Check that `active_company_id` is set in session

### JSON Filter Returns Empty Object

**Problem**: `to_json` returns `'{}'` instead of expected data

**Solutions**:
1. Check that value is not `None`
2. Verify value is serializable (dict, list, string, number, bool)
3. Check for circular references in complex objects
4. Ensure value is passed correctly from view context

---

## 9. Best Practices

1. **Always load tags at the top**: Load template tags before using them
2. **Use appropriate date format**: Use `jalali_date_long` for user-facing dates, `jalali_date_short` for compact displays
3. **Check permissions before rendering**: Use `feature_allowed` to conditionally show/hide UI elements
4. **Validate JSON data**: Test `to_json` output in browser console before using in JavaScript
5. **Cache permission checks**: Permission checks are fast, but avoid excessive nested checks in loops

---

**Last Updated**: 2025-11-21

