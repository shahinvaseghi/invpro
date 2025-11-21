## UI Architecture & Page Blueprint

### 1. Platform Context

`invproj` is a modular warehouse, production, and quality-control platform implemented with Python, Django, and PostgreSQL. The system must operate in both Linux/Nginx and Windows Server/IIS environments. Django currently renders server-side HTML, but we plan the UI so that modules can progressively adopt SPA components (React/Vue) where real-time interactivity is needed. A shared layout, component library, and permission-aware navigation keep the user experience consistent across modules while allowing each module to evolve independently.

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Global Shell (layout, navigation, notifications, company picker, user menu)│
├───────────────────────────────────────────────────────────────────────────┤
│ Inventory Module   │ Production Module   │ QC Module       │ Shared Settings │
│ (inventory_*)      │ (production_*)      │ (qc_*)          │ (invproj_*)     │
└───────────────────────────────────────────────────────────────────────────┘
```

All UI components map directly to the database tables defined in the module design documents. Each view should be built so that switching from one company to another simply re-queries the relevant tables via the active company context stored in the session. Access control derives from `invproj_access_level_permission` and governs both routing and component visibility.

### 2. Global UX Principles

1. **Unified shell:**
   - Header: company selector, quick search, notification bell, user menu, help center.
   - Left navigation drawer: module switcher with collapsible groups.
   - Breadcrumb bar below header showing module → section → record.
   - Responsive layout using CSS grid/flex to support desktops (primary target) and tablets.

2. **Role-aware UI:**
   - Every navigation item has a permission key (module, resource_code). Unauthorized entries are hidden.
   - Action buttons (Create/Approve/Delete) wrap reusable permission checks. Templates should call `{% if has_perm 'inventory', 'inventory_receipt_permanent', 'can_create' %}`.

3. **Company context:**
   - Company picker lists companies available via `invproj_user_company_access`.
   - When company changes, trigger a client-side event to reload all lists and clear cached filters.
   - Show selected company code in header and include it in page titles (e.g., `INV-001 · Inventory Dashboard`).

4. **Reusable components:**
   - Data grids: server-side pagination, column sort, column visibility toggles, export (CSV/XLSX).
   - Filter panels: collapsible on desktop, full-screen overlay on tablet. Persist filters via URL query parameters.
   - Detail tabs: Summary, Activity Log, Attachments, Related Records.
   - Modal and side-panel forms for quick edits, full-page forms for multi-step workflows.

5. **Audit visibility:**
   - Each detail view shows Created/Updated by, timestamps, `is_enabled`, workflow state.
   - Activity logs (timeline component) show approvals, status changes, associated users.

6. **Error, empty, success states:**
   - Use consistent patterns for empty states with contextual actions (e.g., “No purchase requests yet · Create first request”).
   - Display inline validation errors beneath inputs; global error banner for server errors.

7. **Performance and scalability:**
   - Large lists default to filters applied (e.g., “Open only”). Provide asynchronous exports for full dataset.
   - Use caching for reference data (item types, suppliers) to reduce DB round trips.

### 3. Inventory Module UI (Tables prefixed `inventory_`)

#### 3.1 Dashboards & Home
- **Inventory Overview Page**
  - KPIs: total stock value (`inventory_item` × valuation), low-stock alerts, pending receipts count (`inventory_receipt_temporary`), QC pending approvals (`qc_receipt_inspection`).
  - Graphs: Stock over time, fast-moving SKUs, supplier OTIF performance.
  - Quick links: “Create Purchase Request”, “Record Temporary Receipt”, “Run Stocktaking”.

#### 3.2 Master Data Management
1. **Item Type/Category/Subcategory Management**
   - Data grid with hierarchical view (type → category → subcategory).
   - Inline toggles for `is_enabled`, `sort_order` reorder dialog.
   - Modal form for create/edit (fields from `inventory_item_type`, `inventory_item_category`, `inventory_item_subcategory`).
   - Validations: unique constraints, numeric codes, metadata JSON editor with schema hints.

2. **Item Catalog (`inventory_item`)**
   - Master-detail layout:
     - Left: filter list by type/category, search by name/code.
     - Right: tabs (`Summary`, `Specifications` via `inventory_item_spec`, `Units` via `inventory_item_unit`, `Warehouses` via `inventory_item_warehouse`, `Suppliers` via `inventory_supplier_item`, `Substitutes` via `inventory_item_substitute`, `Audit`).
   - Actions: Activate/Deactivate, Duplicate item, Generate QR/barcode.
   - Show computed code structure highlight (type/cat/subcat segments).

3. **Warehouse & Work Line Management**
   - Map view (if location data available) + table for `inventory_warehouse`.
   - Work lines nested under warehouse detail page (`inventory_work_line`).
   - Provide visualization for operational status (enabled/disabled toggles).

4. **Supplier Management**
   - Supplier list with contact information, ratings (from future analytics).
   - Tabs for categories (`inventory_supplier_category`), subcategories (`inventory_supplier_subcategory`), items (`inventory_supplier_item`).
   - Price metadata viewer (JSON pretty print) with currency formatting.

#### 3.3 Procurement
1. **Purchase Request Board**
   - Kanban lanes for statuses (Draft, Approved, Ordered, Fulfilled, Cancelled).
   - Card details: request code, item, quantity, needed by date, requester.
   - Drill-down detail page with history timeline, linked receipts, approvals.
   - Mass actions: approve multiple, assign to buyer.

2. **Approval Workbench**
   - Filtered list of requests awaiting current user approval.
   - Approve/reject modals capturing approval notes.

#### 3.4 Inbound Receipts
1. **Temporary Receipt Queue**
   - Grid of `inventory_receipt_temporary` with QC status badge (`Awaiting QC`, `QC Passed`, `QC Rejected`).
   - Actions: Record inspection (links to QC module), convert to permanent, cancel.
   - Detail view: supplier info, linked transfer, attachments, inspection results from `qc_receipt_inspection`.

2. **Permanent Receipt Management**
   - List view of `inventory_receipt_permanent` with filters for supplier, date range, purchase request.
   - Detail view shows line items (future extension), financial fields, posting status.
   - “Create from Temporary” wizard autopopulates from selected temporary receipt.
   - For items with `has_lot_tracking=1`, include a step that generates lot codes using the pattern `LOT-MMYY-XXXXXX-UUU`. The UI should display how many units must be labeled, allow printing of labels (PDF/thermal), and show a preview of codes before posting.

3. **Consignment Receipts**
   - Separate list due to ownership differences.
   - Track expected return date, conversion status, linked contract.

#### 3.5 Outbound Issues
1. **Issue Overview**
   - Tabs for Permanent Issue, Consumption Issue, Consignment Issue.
   - Each tab has table, filters, quick create buttons.

2. **Consumption Issue Form**
   - Form referencing `production_transfer_to_line` (if linked) to prefill materials.
   - Validation ensures `quantity` does not exceed transferred quantity unless permitted.
   - When item requires lot tracking, modal selector lists available lot codes (with search/filter) and enforces 1:1 mapping per unit; UI shows remaining balance for each lot and highlights codes generated earlier (`LOT-MMYY-XXXXXX-UUU`).

3. **Approval Flow**
   - Optional approval step for issues depending on role; display required approvals and current stage.

#### 3.6 Stocktaking & Adjustments
1. **Stocktaking Sessions (Future)**
   - Session header table (to be added later) controlling deficits/surplus/record docs.

2. **Deficit/Surplus Documents**
   - Side-by-side view showing expected vs counted data (bar chart/table combination).
   - Comment fields for reason codes; quick link to incident report.

3. **Stock Record Confirmation**
   - `inventory_stocktaking_record` detail page summarizing variance documents.
   - Print-ready PDF for audit sign-off.

### 4. Production Module UI (Tables prefixed `production_`)

#### 4.1 Dashboard
- KPIs: Orders released vs completed, yield %, average cycle time, machine utilization.
- Visuals: Gantt chart of active orders, Pareto of scrap reasons, labor vs machine time trend.

#### 4.2 Engineering Data
1. **BOM Material Mapping (`production_bom_material`)**
   - Item-centric view showing required materials per finished product.
   - Editor with inline validations for quantity, scrap allowance.
   - Compare revisions side-by-side.

2. **Process Definitions (`production_process`, `production_process_step`)**
   - Process list grouped by finished item; status chips for Active/Archived.
   - Detail view timeline for steps: sequence order, assigned work center, labor/machine minutes, required personnel roles.
   - Copy process structure to new revision; highlight differences.

#### 4.3 Production Orders (`production_product_order`)
- Order board (cards for each status) + tabular view.
- Order detail tabs:
  - Summary: quantity, BOM, process, due date, status.
  - Materials: required vs transferred vs consumed (join with inventory transfer/issue data).
  - Operations: planned vs actual times per process step.
  - QC: linked inspections (incoming & in-process; future).
  - Activity: approvals, releases, completions.
- Actions: Release order, start/stop, close, scrap report.

#### 4.4 Performance Tracking (`production_order_performance`)
- Recording UI: form with entry for quantity produced, received, scrapped; labor usage (multi-row), machine usage, material scrap JSON.
- Visual comparison: gauge showing actual vs planned cycle time, run time.
- Exports for OEE reporting.

#### 4.5 Material Transfers (`production_transfer_to_line`)
- Status board: Draft, Issued, Delivered, Discrepancy.
- Detail page: Items, source/destination warehouses, work center, variances, attachments (pick tickets).
- Actions: Issue stock, mark delivered, record variance; sync with inventory issue documents.
- Shared visibility with inventory to coordinate material movements; highlight pending transfers that block production start.
- Integrate with barcode scanning for confirmation.

### 5. QC Module UI (Tables prefixed `qc_`)

#### 5.1 Inspection Workbench
- Landing page lists temporary receipts with QC status (Awaiting, In Progress, Passed, Failed).
- Filters: supplier, item, inspection code, date range.
- Batch actions: Assign inspector, schedule inspection.

#### 5.2 Inspection Detail (`qc_receipt_inspection`)
- Header: temporary receipt info (quantity, supplier, item), current decision.
- Sections:
  - **Checklist**: dynamic form generated from `inspection_results` JSON schema (future extension).
  - **Measurements**: table for recorded values, tolerance indicators (color-coded).
  - **Attachments**: image/doc upload preview.
  - **Approvals**: inspector signature, approver signature.
  - **Nonconformities**: panel with link to CAPA once implemented.
- Action buttons: Approve, Approve with Deviation, Reject (requires reason), Request Re-inspection.

#### 5.3 Inspection History & Reporting
- Timeline view for each supplier or item showing pass/fail trend.
- Exportable reports for compliance (CSV/PDF).
- Quick link to related permanent receipts and purchase orders.

### 6. Shared Module UI (Tables prefixed `invproj_`)

#### 6.1 Company Management
- `invproj_company` list with search, status toggles, brand metadata form (logo upload, color palette).
- Detail view for contact info, metadata (JSON editor with schema hints), related units.

#### 6.2 Company Units (`invproj_company_unit`)
- Hierarchical tree component showing parent-child relationships.
- Table with filters by unit type (department, plant, etc.).
- Forms to assign unit-level metadata (cost centers, managers, addresses).

#### 6.3 User & Access Management
- User list (`invproj_user`) with status filters (active, invited, suspended).
- Invite workflow: capture email, assign provisional access levels, send email link.
- Access assignment wizard: select company, choose access level (`invproj_access_level`), preview permissions.
- Role management UI: create/edit access levels, select permissions via checkboxes grouped by module and resource.
- Audit log: table showing who changed which access (detailed metadata).

#### 6.4 Personnel Management (Production Module) (`production_person`, `production_person_assignment`)
- Personnel list with search by code/name, filters by company unit, status.
- **Location**: Production module (`/production/personnel/`)

#### 6.5 Machine Management (Production Module) (`production_machine`)
- Machine list with search by code/name, filters by work center, status, machine type.
- Machine detail view showing specifications, maintenance schedule, work center assignment.
- **Location**: Production module (`/production/machines/`)
- Detail view: personal info, metadata, certifications (stored in metadata or future table), associated user account if applicable.
- Assignment manager: grid showing work center assignments by module. Use row for person, columns for work centers. Provide timeline or history view for assignment periods.

### 7. UX Patterns & Technical Implementation

#### 7.1 Template Hierarchy
- `templates/base.html`: global layout (header, nav, footer).
- `templates/components/`: reusable pieces (alerts, pagination, filters, data grid, timeline, status badge, metadata viewer).
- Module-specific bases: `templates/inventory/base.html`, etc., that extend `base.html` and load module nav.
- Each module organizes pages under `templates/<module>/<section>/` (e.g., `inventory/items/list.html`).

#### 7.2 URL & View Conventions
- Use Django URL namespaces per module (`inventory:items:list`).
- Class-based views:
  - ListView + Filter mixin using `django-filter` for server-side filtering.
  - DetailView with top-level context (record, related objects).
  - FormView/UpdateView for CRUD; use `FormHelper` or custom component for consistent layout.
- Decorator/mixin `CompanyPermissionRequired` ensures user has proper `invproj_access_level_permission` entry.
- Provide DRF viewsets paralleling key UI views for potential SPA use.

#### 7.3 Forms & Workflows
- Use Django ModelForms with `ModelFormSet` for nested relationships (e.g., BOM materials).
- Add custom clean methods validating cross-table dependencies (e.g., `temporary_receipt` must have `QC approved`).
- Stepper components for multi-step forms (e.g., creating production order: select item → choose BOM → choose process → set quantity → review confirmation).
- Provide autosave for long forms (saving draft states). Use AJAX endpoints for saving partial data, storing in metadata if needed.

#### 7.4 Navigation & Breadcrumbs
- Build breadcrumb component receiving list of tuples (label, URL). Example: `[('Inventory', 'inventory:dashboard'), ('Receipts', 'inventory:receipts:list'), ('TR-00045', None)]`.
- Highlight active nav item based on current route; use icons for top-level sections.

#### 7.5 State Indicators & Workflow Visualization
- Status chips (color-coded): Draft (gray), In Progress (blue), Approved (green), Rejected (red), Archived (black).
- Timelines for approvals: vertical timeline showing steps with user avatars and timestamps.
- Progress bars for production order completion (quantity produced vs planned).
- Alerts for approaching due dates (within 3 days) or overdue items (red banner).

#### 7.6 Handling Large Data Sets
- Grid virtualization (optional) if using SPA components; for server-side, paginate and lazily load details via AJAX modals.
- Provide “Analyze in Excel/BI” exports for key lists; asynchronous job to generate file and notify user via toast when ready.
- Use caching for reference dropdowns (e.g., item list) with typeahead search.

#### 7.7 Integrations & APIs
- REST APIs (DRF) for core entities: Items, Purchase Requests, Receipts, Production Orders, QC Inspections.
- Webhook endpoints for external systems (ERP, MES) to push updates.
- WebSocket channels (future) for dashboards requiring live updates (production line status, QC queue).

#### 7.8 Accessibility & Localization
- Support right-to-left languages (e.g., Persian) by using logical ordering and CSS direction switching.
- Use accessible color contrasts, ARIA labels for interactive elements, keyboard navigation for forms and tables.
- Strings must be translatable via Django i18n; dynamic data uses localized formats (dates, numbers, currency).

#### 7.9 Testing & Quality
- Automated UI tests (Selenium/Playwright) for critical flows: login, company switch, create purchase request, approve QC inspection.
- Snapshot tests for templates to ensure layout stability.
- Performance budgets (page load under 3s for key views on typical datasets).

### 8. Data ↔ UI Mapping Examples

| UI Page                                   | Primary Tables Used                                        | Notes |
|-------------------------------------------|-------------------------------------------------------------|-------|
| Inventory Item Detail                     | `inventory_item`, `inventory_item_spec`, `inventory_item_unit`, `inventory_item_warehouse`, `inventory_supplier_item`, `inventory_item_substitute` | Show aggregated metadata; allow inline edits via AJAX. |
| Purchase Request Detail                   | `inventory_purchase_request`, `inventory_receipt_permanent`, `production_product_order` (links) | Display fulfillment progress bar. |
| Temporary Receipt QC Panel                | `inventory_receipt_temporary`, `qc_receipt_inspection`, `inventory_receipt_permanent` | QC approval toggles conversion button. |
| Production Order Detail                   | `production_product_order`, `production_bom_material`, `production_process_step`, `production_order_performance`, `production_transfer_to_line_item`, `inventory_issue_consumption` | Multi-tab view linking materials and performance. |
| QC Inspection History Report              | `qc_receipt_inspection`, `inventory_receipt_temporary`, `inventory_receipt_permanent` | Provide CSV export. |
| User Access Management                    | `invproj_user`, `invproj_user_company_access`, `invproj_access_level`, `invproj_access_level_permission` | UI for assigning roles per company. |

### 9. Development Roadmap

1. **Foundations**
   - Implement base template, navigation shell, company picker, permission-check mixins.
   - Build shared component library (data grid, forms, modals, status chips, timeline).

2. **Shared Module UI**
   - Company & unit management pages.
   - User and access level management.
   - Personnel and machine management (Production module).

3. **Inventory Module**
   - Master data (items, warehouses, suppliers).
   - Procurement requests and purchase workflows.
   - Temporary receipt queue and QC integration.
   - Permanent receipts, issues, stocktaking.

4. **Production Module**
   - BOM and process editors.
   - Production order management and performance reporting.
   - Transfer coordination with inventory.

5. **QC Module**
   - Inspection workbench for temporary receipts.
   - Inspection detail capture forms and history reporting.
   - Integration with nonconformity/CAPA once defined.

6. **Enhancements**
   - Real-time dashboards, analytics widgets.
   - SPA integration for high-interaction screens (e.g., production line monitoring).
   - Mobile-responsive views for warehouse scanning tasks.

### 10. Deliverables for the UI Team

- High-fidelity wireframes per screen described above (Figma or equivalent).
- Component library documentation (props, states, usage guidelines).
- CSS guidelines (spacing, typography, color themes, dark mode plans).
- Interaction specs (hover states, animations, validation behavior).
- Routing map with URLs and expected permissions for each view.
- API contracts (input/output JSON, error codes) for SPA or integrations.

By following these guidelines, the UI team can implement a modular, scalable interface that mirrors the domain structure of the database while remaining flexible for future growth and technology upgrades. EOF
