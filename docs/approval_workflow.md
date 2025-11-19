# Approval Workflow Guide

Approval steps across the platform (purchase requests, warehouse requests, and stocktaking records) are now fully **user-based**. Django's `User` model owns every approval, while the Production module's `Person` records remain focused on work-center staffing and man-hour analytics.

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
| Requester | Still linked to `production.Person` for compatibility with line-level workforce KPIs. |
| Approver | ForeignKey to Django `User` (`approver_id`). |
| Form | `PurchaseRequestForm` pulls approvers via `get_feature_approvers("inventory.requests.purchase", company_id)` and requires a selection. |
| View | `PurchaseRequestApproveView` checks that the active user matches `approver_id` **and** belongs to the allowed approver list. Non-matching users receive a localized error. |
| Locking | Approval flips `status` to `APPROVED`, records `approved_at`, sets `is_locked = 1`, and captures `locked_by` when available. Locked documents are the only ones surfaced inside receipt forms. |

### Visibility Rules

- The approval panel is rendered only if `request.user.id == purchase_request.approver_id`.
- Users without approval permission never see approve/reject actions thanks to a combination of template checks (`approver_user_ids`) and server-side validation.

## Warehouse Requests

| Aspect | Details |
| --- | --- |
| Requester | Remains a `Person` to align with staffing and departmental reporting. |
| Approver | ForeignKey to Django `User`, surfaced through `get_feature_approvers("inventory.requests.warehouse", company_id)`. |
| Form | `WarehouseRequestForm` enforces approver selection and filters items/warehouses/units based on company scope. |
| View | `WarehouseRequestApproveView` mirrors the purchase flow: only the designated approver (and users with the permission) can approve. |
| Locking | Sets `request_status = "approved"`, stamps `approved_at`, optionally stores `approved_by` (person) for work-line metrics, and locks the document for downstream issue generation. |

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

## When to Touch `Person`

`production.Person` is still the authoritative source for:

- Staffing rosters inside production work lines.
- Department/unit membership and man-hour calculations.
- Linking requesters to physical employees for analytics.

Do **not** reintroduce `Person` into approval fields; all approval controls must stay user-based.

