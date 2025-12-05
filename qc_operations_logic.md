# QC Operations Logic

## Description
This document describes the logic and workflow for the "QC Operations" feature in the Production module, as well as the "Rework Document" process in the same module, based on discussed requirements.

---

## 1. QC Requirement Flag
- Each operation can have a flag called "Needs QC".
- This flag indicates whether the operation requires quality control approval before the workflow can continue.

## 2. Menu Addition: QC Operations (In Production Module)
- A new menu item titled **"QC Operations"** will be added to the production module.
- This menu displays **only operations** that:
    - Have the "Needs QC" flag set,
    - **AND** have a performance document (performance record) already registered for them.

## 3. QC Approval/Reject Process
- For every operation listed in the "QC Operations" menu, the user is able to:
    - Approve (confirm) the operation
    - Reject the operation
- The result of this QC action will directly impact further workflow.

## 4. Restriction on Creating General Performance Document
- When a performance document is registered for an operation with the "Needs QC" flag:
    - The system must prevent the user from creating a "general performance document" for that order **until QC approval has been granted**.
    - Only after QC approval, the user can proceed with the related general document.

## 5. Summary of QC Operations Workflow
1. Define/process an operation, set the "Needs QC" flag if appropriate.
2. After registering a performance document for this operation, it appears in the "QC Operations" menu (only if both conditions met).
3. User (acting as QC) reviews each operation and can approve or reject.
4. Unless approved by QC, the user cannot submit the general performance document for the related order.

---

## 6. Rework Document Logic in Production Module
### Description
A new menu titled **"Rework"** will be added to the production module for managing and registering rework documents for orders.

### Workflow
1. **Order Selection:**
    - User first selects a specific production order.
2. **Display of Two Lists:**
    - After order selection, two lists are shown:
        - **First List:** Operations of the selected order that do **not** have any performance document registered (operations completely missing a performance document).
        - **Second List:** Operations of the selected order that **have a performance document** but their performance has been **rejected by QC**.
3. **Rework Document Registration:**
    - From each list, the user can select operations and proceed to register a rework document for the chosen operations.

### Summary
- The "Rework" menu in the production module is dedicated to managing and registering rework documents. This helps users:
    - Identify operations with no performance record at all,
    - And those with rejected performance by QC,
  for handling rework cases appropriately.

---

**Note:**
- This document only describes the business logic and user flow. No code or configuration changes are performed as per user request.
