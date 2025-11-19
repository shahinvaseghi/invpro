# Approval Workflow Guide

Approval steps across the platform (purchase requests, warehouse requests, and stocktaking records) are now fully **user-based**. Django's `User` model owns every approval and request creation. The Production module's `Person` records remain focused solely on work-center staffing, work line assignments, and man-hour analytics.

Use this guide whenever you need to troubleshoot approver visibility, wire new approval-enabled features, or explain the experience to stakeholders.

## Permission Model

- `shared/permissions.py` defines `FEATURE_PERMISSION_MAP`. Features with the `APPROVE` action (e.g., `inventory.requests.purchase`) are the only ones eligible for approving.
- `inventory.forms.get_feature_approvers(feature_code, company_id)` composes the approver queryset:
  - Includes Django superusers automatically.
  - Adds users who have an active `UserCompanyAccess` for the company **and** an access level whose permissions allow `APPROVE` for the feature.
  - Adds users who inherit the permission via group profiles.
- Forms reuse that helper to populate approver dropdowns, ensuring a single source of truth.

## Purchase Requests

| Aspect | Details |
| --- | --- |
| Requester | ForeignKey to Django `User` (`requested_by`). Directly tracks which user created the request. |
| Approver | ForeignKey to Django `User` (`approver_id`). |
| Form | `PurchaseRequestForm` pulls approvers via `get_feature_approvers("inventory.requests.purchase", company_id)` and requires a selection. |
| View | `PurchaseRequestApproveView` checks that the active user matches `approver_id` **and** belongs to the allowed approver list. Non-matching users receive a localized error. |
| Locking | Approval flips `status` to `APPROVED`, records `approved_at`, sets `is_locked = 1`, and captures `locked_by` when available. Locked documents are the only ones surfaced inside receipt forms. |

### Visibility Rules

- The approval panel is rendered only if `request.user.id == purchase_request.approver_id`.
- Users without approval permission never see approve/reject actions thanks to a combination of template checks (`approver_user_ids`) and server-side validation.
- Users can only edit their own draft requests (`requested_by == request.user`).

## Warehouse Requests

| Aspect | Details |
| --- | --- |
| Requester | ForeignKey to Django `User` (`requester`). Directly tracks which user created the request. |
| Approver | Django `User` filtered by warehouse-request approval permission (`approver`). |
| Form | `WarehouseRequestForm` invokes `get_feature_approvers("inventory.requests.warehouse", company_id)` and displays only users with approval authority. |
| View | `WarehouseRequestApproveView` ensures the current user is the designated approver before allowing the POST. |
| Locking | On approval, `request_status` changes to `approved`, `approved_at` and `is_locked=1` are recorded. |

### Visibility Rules

- The approval panel is rendered only if `request.user.id == warehouse_request.approver_id`.
- Users without approval permission never see approve/reject actions.
- Users can only edit their own draft requests (`requester == request.user`).

## Stocktaking Records

| Aspect | Details |
| --- | --- |
| Approver | ForeignKey to `shared.User`. |
| Form | `StocktakingRecordForm` loads approvers through `get_feature_approvers("inventory.stocktaking.records", company_id)`. The dropdown includes superusers and any user whose role grants stocktaking approval. |
| Behavior | `approval_status` is disabled unless the current user is the approver; server-side validation blocks unauthorized mutations. |
| Locking | Approved records set `is_locked = 1` and feed inventory balance calculations. |

## Notifications & Dashboard

- `shared.context_processors.active_company` injects `notifications` and `notification_count` into every template.
  - Pending approvals (where the current user is the approver) generate `approval_pending` notifications per module.
  - Recently approved user-submitted requests (within seven days) generate `approved` notifications.
- `templates/base.html` renders a notification bell with a dropdown summary.
- `templates/ui/dashboard.html` displays:
  - A user-info tile (name/company/current Jalali date-time).
  - Permission-aware stat cards (only show tiles if the user has the related feature permission).
  - A "Pending Approvals" tile with quick links that only appear when the user has access and the count is > 0.

## Testing Checklist

1. **Seed Permissions**: Assign `APPROVE` action to a role via `UserCompanyAccess`.
2. **Approver Dropdown**: Verify forms only list authorized Django users.
3. **Visibility**: Ensure non-approvers cannot see approval widgets in templates.
4. **Server Enforcement**: Attempt to approve as an unauthorized user; expect an error and no state change.
5. **Locking**: After approval, confirm `is_locked`/status fields change and the record becomes selectable in downstream forms.
6. **Notifications**: With pending approvals, confirm the bell badge count and dropdown entries. After approval, ensure requesters receive the "approved" notification.

## When to Use `Person` vs `User`

### Use `User` for:

- **All inventory requests**: Purchase requests, warehouse requests
- **All approval workflows**: Approvers, approval tracking
- **Document creation tracking**: Who created/edited documents
- **Notifications**: Who should receive approval notifications
- **Access control**: Permission checks, authentication

### Use `Person` ONLY for:

- **Production module operations**:
  - Staffing rosters inside production work lines
  - Work line assignments and capacity planning
  - Man-hour calculations and labor cost tracking
  - Department/unit membership for production analytics
  - Shift scheduling and attendance tracking

**Important**: Do **not** reintroduce `Person` into inventory module. All inventory operations must use Django `User` directly.

## Model Changes (Breaking)

### PurchaseRequest
- ✅ `requested_by`: Changed from `Person` to `User`
- ❌ `requested_by_code`: **REMOVED**
- ✅ `approver`: Remains `User` (already was `User`)

### WarehouseRequest
- ✅ `requester`: Changed from `Person` to `User`
- ❌ `requester_code`: **REMOVED**
- ✅ `approver`: Remains `User` (already was `User`)
- ❌ `approved_by`: **REMOVED**
- ❌ `approved_by_code`: **REMOVED**
- ❌ `rejected_by`: **REMOVED**
- ❌ `cancelled_by`: **REMOVED**

### Migration
- Migration `0023_remove_person_from_inventory` handles all these changes
- Existing data in removed fields will be lost
- Ensure you have backups before applying this migration

## Code References

### Forms
- `inventory/forms.py`: `get_feature_approvers()` function
- `inventory/forms.py`: `PurchaseRequestForm`, `WarehouseRequestForm`

### Views
- `inventory/views.py`: `PurchaseRequestCreateView`, `PurchaseRequestApproveView`
- `inventory/views.py`: `WarehouseRequestCreateView`, `WarehouseRequestApproveView`

### Context Processors
- `shared/context_processors.py`: `active_company()` - handles notifications

### Templates
- `templates/base.html`: Notification bell UI
- `templates/ui/dashboard.html`: Dashboard with approval stats
