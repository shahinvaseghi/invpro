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
| `edit` | `id=<user_id>` | Edit user |
| `disable` | `id=<user_id>` | Disable user |
| `enable` | `id=<user_id>` | Enable user |

### Purchase Requests (020400 / purchase_requests)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show purchase requests |
| `add` | - | Create new purchase request |
| `edit` | `id=<request_id>` | Edit purchase request |
| `approve` | `id=<request_id>`, `code=<request_code>` | Approve purchase request |
| `create_receipt_from` | `id=<request_id>`, `type=<temporary\|permanent\|consignment>` | Create receipt from approved purchase request |

**Special Actions:**
- **`create_receipt_from`**: This action allows creating receipt documents (temporary, permanent, or consignment) directly from an approved purchase request. The system will open an intermediate selection page where users can adjust quantities and add notes before creating the final receipt document.

### Warehouse Requests (020500 / warehouse_requests)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show warehouse requests |
| `add` | - | Create new warehouse request |
| `edit` | `id=<request_id>` | Edit warehouse request |
| `approve` | `id=<request_id>`, `code=<request_code>` | Approve warehouse request |
| `create_issue_from` | `id=<request_id>`, `type=<permanent\|consumption\|consignment>` | Create issue from approved warehouse request |

**Special Actions:**
- **`create_issue_from`**: This action allows creating issue documents (permanent, consumption, or consignment) directly from an approved warehouse request. Similar to receipt creation, the system provides an intermediate selection page for quantity adjustment and notes before creating the final issue document.

### Receipts

#### Temporary Receipts (020601 / receipt_temporary)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show temporary receipts |
| `add` | - | Create new temporary receipt |
| `edit` | `id=<receipt_id>` | Edit temporary receipt |
| `delete` | `id=<receipt_id>` | Delete temporary receipt |
| `lock` | `id=<receipt_id>` | Lock temporary receipt |
| `send_to_qc` | `id=<receipt_id>` | Send temporary receipt to QC for inspection |

#### Permanent Receipts (020602 / receipt_permanent)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show permanent receipts |
| `add` | - | Create new permanent receipt |
| `edit` | `id=<receipt_id>` | Edit permanent receipt |
| `delete` | `id=<receipt_id>` | Delete permanent receipt |
| `lock` | `id=<receipt_id>` | Lock permanent receipt |

#### Consignment Receipts (020603 / receipt_consignment)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show consignment receipts |
| `add` | - | Create new consignment receipt |
| `edit` | `id=<receipt_id>` | Edit consignment receipt |
| `delete` | `id=<receipt_id>` | Delete consignment receipt |
| `lock` | `id=<receipt_id>` | Lock consignment receipt |

### Issues

#### Permanent Issues (020701 / issue_permanent)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show permanent issues |
| `add` | - | Create new permanent issue |
| `edit` | `id=<issue_id>` | Edit permanent issue |
| `delete` | `id=<issue_id>` | Delete permanent issue |
| `lock` | `id=<issue_id>` | Lock permanent issue |

#### Consumption Issues (020702 / issue_consumption)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show consumption issues |
| `add` | - | Create new consumption issue |
| `edit` | `id=<issue_id>` | Edit consumption issue |
| `delete` | `id=<issue_id>` | Delete consumption issue |
| `lock` | `id=<issue_id>` | Lock consumption issue |

#### Consignment Issues (020703 / issue_consignment)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show consignment issues |
| `add` | - | Create new consignment issue |
| `edit` | `id=<issue_id>` | Edit consignment issue |
| `delete` | `id=<issue_id>` | Delete consignment issue |
| `lock` | `id=<issue_id>` | Lock consignment issue |

### Inspections (041000 / inspections)

| Action | Parameters | Description |
|--------|------------|-------------|
| `show` | - | Show inspections |
| `showown` | - | Show own inspections |
| `accept` | `code=<inspection_code>` | Accept inspection |
| `reject` | `code=<inspection_code>` | Reject inspection |

---

## Parameter Types

Parameters can be:

1. **Literal values**: `gp=superuser`
2. **From ticket context**: `code={ticket.reference_code}`
3. **From current context**: `user={current_user.id}`

---

## Implementation Status

- **Status**: ✅ **Implemented and Active**
- **Database Tables**: 
  - `invproj_section_registry`: Stores all section definitions (37 sections registered)
  - `invproj_action_registry`: Stores all action definitions (50 actions registered)
- **Migration**: Data migration `0012_populate_section_and_action_registry.py` populates initial data
- **Permission Checking**: Integrated with feature permission system
- **Parameter Validation**: JSON schema validation in `parameter_schema` field
- **Error Handling**: Graceful error handling via handler functions and URL routing

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
