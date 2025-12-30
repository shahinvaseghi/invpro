# Accounting Module Design Plan

## Overview

We are designing `invproj`, a modular warehouse, production, and quality control platform built with Python and Django. The application targets PostgreSQL as the primary database engine and must run seamlessly on both Linux/Nginx and Windows Server/IIS deployments. Django handles server-side rendering and API endpoints, while the architecture leaves room for eventual SPA or mobile front ends. Initially all modules share a single physical database, but careful schema boundaries and naming conventions (`inventory_`, `production_`, `qc_`, `accounting_`, shared `invproj_`) ensure we can migrate modules into their own services or databases as the system scales. Shared/global entities—companies, users, personnel, company units—reside in the `invproj_` namespace and provide consistent tenancy, security, and configuration anchors throughout the platform.

This document presents the comprehensive accounting and financial management module design for the `invproj` platform. The accounting module is designed to support full-featured financial operations including general ledger, subsidiary and detail ledgers, accounting documents (manual and automatic), treasury management (receipts, payments, checks, bank reconciliation), income and expense tracking, payroll management (salary payments, insurance and tax settings, document upload, bank transfer files), VAT (Value Added Tax) management, party account management, financial reports (balance sheet, income statement, account movements), tax compliance (TTMS integration, seasonal transaction reports), and fiscal year closing procedures.

The module integrates with other platform modules (inventory, sales, procurement) to automatically generate accounting entries when business transactions occur, while also supporting manual journal entries for adjustments and corrections. The design follows Iranian accounting standards and tax regulations, including support for VAT calculations, TTMS (Tax Transaction Management System) integration, and seasonal transaction reporting requirements.

Key design principles:

- **Multi-company tenancy**: Every accounting table stores `company_id` and cached `company_code`, referencing `invproj_company`, to isolate tenant data and enable future sharding.
- **Consistent auditing**: Tables include `is_enabled`, activation timestamps, creation/update metadata, and optional `metadata` (`jsonb`) for extensibility. Boolean semantics use `smallint` (0/1) to align with existing conventions.
- **Double-entry bookkeeping**: All accounting documents enforce balanced debits and credits, ensuring accounting equation integrity.
- **Document workflow**: Accounting documents support draft, posted, locked, and reversed states with full audit trails.
- **Integration points**: Automatic document generation from inventory receipts/issues, sales invoices, and procurement transactions.
- **Tax compliance**: Built-in support for VAT calculations, TTMS integration, and seasonal transaction reporting per Iranian tax regulations.
- **Chart of accounts**: Hierarchical account structure (General Ledger → Subsidiary Ledger → Detail Ledger) with flexible depth.
- **Fiscal year management**: Support for fiscal year opening/closing, carry-forward balances, and comparative reporting.

The sections below document each functional area with detailed table designs, relationships, constraints, and implementation notes to guide Django model creation, validation rules, and migration planning.

---

## Table of Contents

1. [Chart of Accounts](#1-chart-of-accounts)
2. [Accounting Documents](#2-accounting-documents)
3. [Treasury Management](#3-treasury-management)
4. [Income and Expense Management](#4-income-and-expense-management)
5. [Payroll Management](#5-payroll-management)
6. [Party Account Management](#6-party-account-management)
7. [Financial Reports](#7-financial-reports)
8. [Tax Compliance Modules](#8-tax-compliance-modules)
9. [Fiscal Year Management](#9-fiscal-year-management)
10. [Settings and Configuration](#10-settings-and-configuration)
11. [Integration Points](#11-integration-points)
12. [Implementation Notes](#12-implementation-notes)
13. [Future Enhancements](#13-future-enhancements)
14. [Conclusion](#14-conclusion)

**Note**: Financial reports are managed by the centralized [Reporting Module](../docs/reporting_module_design_plan.md). See section 7 for overview and link to detailed documentation.

---

## 1. Chart of Accounts

### 1.1 Overview

The Chart of Accounts (COA) is the foundation of the accounting system. It defines the hierarchical structure of accounts used to classify and record all financial transactions. The system supports three levels:

- **General Ledger (کل)**: Top-level accounts representing major account categories (Assets, Liabilities, Equity, Revenue, Expenses)
- **Subsidiary Ledger (معین)**: Intermediate accounts that provide more detail under general ledger accounts
- **Detail Ledger (تفصیلی)**: Most granular level, often representing specific parties, projects, or cost centers

### 1.2 Account Structure

#### Table: `accounting_account`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company owning the account. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code for reporting. |
| `account_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` within company | Hierarchical account code (e.g., "1.01.001"). |
| `account_name` | `varchar(200)` | `NOT NULL` | Persian/local account name. |
| `account_name_en` | `varchar(200)` | nullable | English account name. |
| `account_type` | `varchar(30)` | `NOT NULL`, check in ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE') | Account classification. |
| `account_level` | `smallint` | `NOT NULL`, check in (1,2,3) | 1=General, 2=Subsidiary, 3=Detail. |
| `parent_account_id` | `bigint` | nullable, FK to `accounting_account(id)` | Parent account for hierarchical structure. |
| `normal_balance` | `varchar(10)` | `NOT NULL`, check in ('DEBIT', 'CREDIT') | Expected balance side (Assets/Expenses=DEBIT, Liabilities/Equity/Revenue=CREDIT). |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active account flag. |
| `is_system_account` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | System-generated accounts cannot be deleted. |
| `opening_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Opening balance for current fiscal year. |
| `current_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Current period balance (calculated). |
| `description` | `text` | nullable | Account description and usage notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible attributes (VAT settings, cost center mapping). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Unique constraint on `(company_id, account_code)` ensures account code uniqueness per company.
- Self-referential foreign key `parent_account_id` creates hierarchical structure.
- Account codes should follow hierarchical pattern (e.g., "1" for assets, "1.01" for cash, "1.01.001" for specific bank account).
- `current_balance` is calculated from document lines; consider materialized views for performance.
- System accounts (e.g., retained earnings, current year profit) are protected from deletion.

#### Table: `accounting_account_balance`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `account_id` | `bigint` | `NOT NULL`, FK to `accounting_account(id)` | Account reference. |
| `fiscal_year_id` | `bigint` | `NOT NULL`, FK to `accounting_fiscal_year(id)` | Fiscal year for balance tracking. |
| `period_start` | `date` | `NOT NULL` | Start date of balance period. |
| `period_end` | `date` | `NOT NULL` | End date of balance period. |
| `debit_total` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Total debits in period. |
| `credit_total` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Total credits in period. |
| `opening_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Balance at period start. |
| `closing_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Balance at period end. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible period data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `updated_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Last update timestamp. |

**Additional considerations:**
- Used for period-based reporting and balance calculations.
- Unique constraint on `(company_id, account_id, fiscal_year_id, period_start, period_end)`.
- Consider partitioning by fiscal year for large datasets.

---

## 2. Accounting Documents

### 2.1 Overview

Accounting documents are the core transactional records in the system. Every financial transaction must be recorded through an accounting document that follows double-entry bookkeeping principles (total debits = total credits). Documents can be created manually or automatically generated from business transactions in other modules.

### 2.2 Document Types

- **Manual Entry**: User-created journal entries for adjustments, corrections, or manual transactions
- **Automatic Entry**: System-generated entries from inventory receipts/issues, sales invoices, purchase orders, etc.
- **Opening Entry**: Initial balances when starting the system or opening a new fiscal year
- **Closing Entry**: Year-end closing entries to transfer temporary account balances

### 2.3 Document Structure

#### Table: `accounting_document`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `document_number` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated document number (e.g., "DOC-1403-000001"). |
| `document_date` | `date` | `NOT NULL` | Transaction date (Jalali format in UI). |
| `document_type` | `varchar(30)` | `NOT NULL`, check in ('MANUAL', 'AUTOMATIC', 'OPENING', 'CLOSING', 'ADJUSTMENT') | Document classification. |
| `fiscal_year_id` | `bigint` | `NOT NULL`, FK to `accounting_fiscal_year(id)` | Fiscal year for document. |
| `period_id` | `bigint` | nullable, FK to `accounting_period(id)` | Optional period reference. |
| `description` | `text` | `NOT NULL` | Document description/explanation. |
| `reference_number` | `varchar(100)` | nullable | External reference (invoice number, receipt number, etc.). |
| `reference_type` | `varchar(50)` | nullable | Type of reference (e.g., 'INVENTORY_RECEIPT', 'SALES_INVOICE'). |
| `reference_id` | `bigint` | nullable | Foreign key to referenced document (polymorphic). |
| `total_debit` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Sum of all debit lines. |
| `total_credit` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Sum of all credit lines (must equal total_debit). |
| `status` | `varchar(20)` | `NOT NULL`, default `'DRAFT'`, check in ('DRAFT', 'POSTED', 'LOCKED', 'REVERSED', 'CANCELLED') | Document workflow status. |
| `posted_at` | `timestamp with time zone` | nullable | When document was posted. |
| `posted_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who posted the document. |
| `locked_at` | `timestamp with time zone` | nullable | When document was locked. |
| `locked_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who locked the document. |
| `reversed_document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Reference to reversal document if reversed. |
| `attachment_count` | `smallint` | `NOT NULL`, default `0` | Number of attached files. |
| `notes` | `text` | nullable | Internal notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible document data (approval chain, custom fields). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Document number format: `DOC-YYYY-XXXXXX` where YYYY is fiscal year and XXXXXX is sequential number.
- Constraint: `total_debit = total_credit` must be enforced at database level.
- Status workflow: DRAFT → POSTED → LOCKED (or CANCELLED/REVERSED).
- Locked documents cannot be edited or deleted.
- Reversed documents create a new document with opposite entries.

#### Table: `accounting_document_line`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `document_id` | `bigint` | `NOT NULL`, FK to `accounting_document(id)`, ON DELETE CASCADE | Parent document. |
| `line_number` | `smallint` | `NOT NULL` | Sequential line number within document. |
| `account_id` | `bigint` | `NOT NULL`, FK to `accounting_account(id)` | Account being debited or credited. |
| `debit_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Debit amount (must be 0 if credit_amount > 0). |
| `credit_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Credit amount (must be 0 if debit_amount > 0). |
| `description` | `text` | nullable | Line item description. |
| `party_id` | `bigint` | nullable, FK to `accounting_party(id)` | Optional party reference for detail accounts. |
| `cost_center_id` | `bigint` | nullable, FK to `accounting_cost_center(id)` | Optional cost center allocation. |
| `project_id` | `bigint` | nullable | Optional project reference (if project tracking enabled). |
| `vat_rate` | `decimal(5,2)` | nullable | VAT rate percentage if applicable. |
| `vat_amount` | `decimal(18,2)` | nullable | VAT amount if applicable. |
| `reference` | `varchar(100)` | nullable | Additional reference for line item. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible line data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- Constraint: `(debit_amount > 0 AND credit_amount = 0) OR (debit_amount = 0 AND credit_amount > 0)` - each line must be either debit or credit, not both.
- Line numbers should be sequential and unique within document.
- Party reference is required for detail accounts (account_level = 3).

#### Table: `accounting_document_attachment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `document_id` | `bigint` | `NOT NULL`, FK to `accounting_document(id)`, ON DELETE CASCADE | Parent document. |
| `file_name` | `varchar(255)` | `NOT NULL` | Original file name. |
| `file_path` | `varchar(500)` | `NOT NULL` | Storage path (relative to media root). |
| `file_size` | `bigint` | `NOT NULL` | File size in bytes. |
| `mime_type` | `varchar(100)` | nullable | MIME type of file. |
| `description` | `varchar(255)` | nullable | Attachment description. |
| `uploaded_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Upload timestamp. |
| `uploaded_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Uploader reference. |

**Additional considerations:**
- Store files in `media/accounting/documents/{company_id}/{fiscal_year}/{document_number}/`.
- Support common formats: PDF, images, Excel, Word documents.
- Consider file size limits and virus scanning.

---

## 3. Treasury Management

### 3.1 Overview

Treasury management handles all cash and bank transactions including receipts, payments, transfers between accounts, check management, and bank reconciliation. This module ensures accurate tracking of cash flow and bank balances.

### 3.2 Cash and Bank Accounts

#### Table: `accounting_cash_account`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `account_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` within company | Cash account code (e.g., "1.01.001"). |
| `account_name` | `varchar(200)` | `NOT NULL` | Account name (e.g., "صندوق اصلی"). |
| `account_type` | `varchar(20)` | `NOT NULL`, check in ('CASH', 'BANK') | Cash register or bank account. |
| `bank_name` | `varchar(200)` | nullable | Bank name (if account_type = 'BANK'). |
| `branch_name` | `varchar(200)` | nullable | Branch name. |
| `account_number` | `varchar(50)` | nullable | Bank account number. |
| `iban` | `varchar(34)` | nullable | IBAN code (if applicable). |
| `swift_code` | `varchar(11)` | nullable | SWIFT/BIC code. |
| `currency_code` | `varchar(3)` | `NOT NULL`, default `'IRR'` | ISO currency code. |
| `opening_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Opening balance. |
| `current_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Current balance (calculated). |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active account flag. |
| `linked_account_id` | `bigint` | nullable, FK to `accounting_account(id)` | Linked general ledger account. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible account data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Each cash/bank account should have a corresponding account in the chart of accounts.
- Current balance is calculated from treasury transactions.

#### Table: `accounting_treasury_transaction`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `transaction_number` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated number (e.g., "TR-1403-000001"). |
| `transaction_date` | `date` | `NOT NULL` | Transaction date. |
| `transaction_type` | `varchar(20)` | `NOT NULL`, check in ('RECEIPT', 'PAYMENT', 'TRANSFER') | Transaction classification. |
| `cash_account_id` | `bigint` | `NOT NULL`, FK to `accounting_cash_account(id)` | Source or destination account. |
| `to_cash_account_id` | `bigint` | nullable, FK to `accounting_cash_account(id)` | Destination account (for transfers). |
| `amount` | `decimal(18,2)` | `NOT NULL` | Transaction amount. |
| `currency_code` | `varchar(3)` | `NOT NULL`, default `'IRR'` | Transaction currency. |
| `exchange_rate` | `decimal(10,4)` | nullable | Exchange rate if foreign currency. |
| `description` | `text` | `NOT NULL` | Transaction description. |
| `party_id` | `bigint` | nullable, FK to `accounting_party(id)` | Related party (customer, supplier, etc.). |
| `payment_method` | `varchar(30)` | nullable, check in ('CASH', 'CHECK', 'CARD', 'TRANSFER', 'OTHER') | Payment method. |
| `check_id` | `bigint` | nullable, FK to `accounting_check(id)` | Related check (if payment_method = 'CHECK'). |
| `document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Related accounting document. |
| `reference_number` | `varchar(100)` | nullable | External reference. |
| `is_reconciled` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Bank reconciliation status. |
| `reconciled_at` | `timestamp with time zone` | nullable | Reconciliation timestamp. |
| `reconciled_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who reconciled. |
| `status` | `varchar(20)` | `NOT NULL`, default `'DRAFT'`, check in ('DRAFT', 'POSTED', 'CANCELLED') | Transaction status. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible transaction data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Transaction number format: `TR-YYYY-XXXXXX`.
- Receipts increase account balance, payments decrease it.
- Transfers require both `cash_account_id` and `to_cash_account_id`.
- Posted transactions automatically create accounting document entries.

#### Table: `accounting_check`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `check_number` | `varchar(50)` | `NOT NULL` | Check number. |
| `check_type` | `varchar(20)` | `NOT NULL`, check in ('RECEIVABLE', 'PAYABLE') | Received or issued check. |
| `bank_name` | `varchar(200)` | `NOT NULL` | Issuing bank. |
| `branch_name` | `varchar(200)` | nullable | Branch name. |
| `account_number` | `varchar(50)` | nullable | Account number. |
| `amount` | `decimal(18,2)` | `NOT NULL` | Check amount. |
| `currency_code` | `varchar(3)` | `NOT NULL`, default `'IRR'` | Check currency. |
| `issue_date` | `date` | `NOT NULL` | Check issue date. |
| `due_date` | `date` | `NOT NULL` | Check due date. |
| `drawer_party_id` | `bigint` | nullable, FK to `accounting_party(id)` | Drawer (issuer) party. |
| `beneficiary_party_id` | `bigint` | nullable, FK to `accounting_party(id)` | Beneficiary party. |
| `status` | `varchar(30)` | `NOT NULL`, default `'PENDING'`, check in ('PENDING', 'DEPOSITED', 'CLEARED', 'BOUNCED', 'CANCELLED') | Check status. |
| `deposit_date` | `date` | nullable | Deposit date. |
| `clearance_date` | `date` | nullable | Clearance date. |
| `bounce_reason` | `text` | nullable | Reason if bounced. |
| `treasury_transaction_id` | `bigint` | nullable, FK to `accounting_treasury_transaction(id)` | Related treasury transaction. |
| `document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Related accounting document. |
| `notes` | `text` | nullable | Additional notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible check data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Receivable checks: company receives check from customer.
- Payable checks: company issues check to supplier/creditor.
- Status workflow: PENDING → DEPOSITED → CLEARED (or BOUNCED).
- Track check lifecycle for cash flow management.

#### Table: `accounting_bank_reconciliation`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `cash_account_id` | `bigint` | `NOT NULL`, FK to `accounting_cash_account(id)` | Bank account being reconciled. |
| `reconciliation_date` | `date` | `NOT NULL` | Reconciliation date. |
| `statement_balance` | `decimal(18,2)` | `NOT NULL` | Bank statement ending balance. |
| `book_balance` | `decimal(18,2)` | `NOT NULL` | System book balance. |
| `adjusted_balance` | `decimal(18,2)` | `NOT NULL` | Adjusted balance after reconciliation. |
| `outstanding_deposits` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Deposits not yet on statement. |
| `outstanding_checks` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Checks not yet cleared. |
| `bank_charges` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Bank fees/charges. |
| `interest_earned` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Interest income. |
| `reconciled_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who performed reconciliation. |
| `notes` | `text` | nullable | Reconciliation notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible reconciliation data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- Reconciliation formula: `adjusted_balance = book_balance + outstanding_deposits - outstanding_checks - bank_charges + interest_earned`.
- Should match `statement_balance` after adjustments.
- Mark transactions as reconciled during this process.

---

## 4. Income and Expense Management

### 4.1 Overview

Income and expense management tracks all revenue and cost transactions, with support for VAT calculations, cost center allocation, and project tracking. This module integrates with sales and inventory modules to automatically record income and expenses.

### 4.2 Income and Expense Records

#### Table: `accounting_income_expense`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `transaction_number` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated number (e.g., "IE-1403-000001"). |
| `transaction_date` | `date` | `NOT NULL` | Transaction date. |
| `transaction_type` | `varchar(20)` | `NOT NULL`, check in ('INCOME', 'EXPENSE') | Income or expense. |
| `category_id` | `bigint` | nullable, FK to `accounting_income_expense_category(id)` | Income/expense category. |
| `account_id` | `bigint` | `NOT NULL`, FK to `accounting_account(id)` | Related account. |
| `amount` | `decimal(18,2)` | `NOT NULL` | Base amount (before VAT). |
| `vat_rate` | `decimal(5,2)` | nullable | VAT rate percentage. |
| `vat_amount` | `decimal(18,2)` | nullable | Calculated VAT amount. |
| `total_amount` | `decimal(18,2)` | `NOT NULL` | Total amount (base + VAT). |
| `currency_code` | `varchar(3)` | `NOT NULL`, default `'IRR'` | Transaction currency. |
| `exchange_rate` | `decimal(10,4)` | nullable | Exchange rate if foreign currency. |
| `description` | `text` | `NOT NULL` | Transaction description. |
| `party_id` | `bigint` | nullable, FK to `accounting_party(id)` | Related party (customer, supplier). |
| `cost_center_id` | `bigint` | nullable, FK to `accounting_cost_center(id)` | Cost center allocation. |
| `project_id` | `bigint` | nullable | Project reference (if applicable). |
| `payment_method` | `varchar(30)` | nullable | Payment method. |
| `treasury_transaction_id` | `bigint` | nullable, FK to `accounting_treasury_transaction(id)` | Related treasury transaction. |
| `document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Related accounting document. |
| `reference_type` | `varchar(50)` | nullable | Source reference type (e.g., 'SALES_INVOICE'). |
| `reference_id` | `bigint` | nullable | Source reference ID. |
| `is_vat_applicable` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | VAT applicability flag. |
| `vat_exemption_reason` | `varchar(200)` | nullable | Reason for VAT exemption. |
| `status` | `varchar(20)` | `NOT NULL`, default `'DRAFT'`, check in ('DRAFT', 'POSTED', 'CANCELLED') | Transaction status. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible transaction data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- VAT calculation: `vat_amount = amount * (vat_rate / 100)`, `total_amount = amount + vat_amount`.
- Integration with sales module: sales invoices automatically create income records.
- Integration with inventory module: purchase receipts automatically create expense records.

#### Table: `accounting_income_expense_category`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `category_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` within company | Category code. |
| `category_name` | `varchar(200)` | `NOT NULL` | Category name. |
| `category_type` | `varchar(20)` | `NOT NULL`, check in ('INCOME', 'EXPENSE') | Income or expense category. |
| `parent_category_id` | `bigint` | nullable, FK to `accounting_income_expense_category(id)` | Parent category for hierarchy. |
| `default_account_id` | `bigint` | nullable, FK to `accounting_account(id)` | Default account for category. |
| `default_vat_rate` | `decimal(5,2)` | nullable | Default VAT rate. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active category flag. |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Display order. |
| `description` | `text` | nullable | Category description. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible category data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Hierarchical category structure for better organization.
- Default account and VAT rate can be overridden per transaction.

#### Table: `accounting_cost_center`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `cost_center_code` | `varchar(20)` | `NOT NULL`, `UNIQUE` within company | Cost center code. |
| `cost_center_name` | `varchar(200)` | `NOT NULL` | Cost center name. |
| `parent_cost_center_id` | `bigint` | nullable, FK to `accounting_cost_center(id)` | Parent cost center. |
| `department_id` | `bigint` | nullable, FK to `invproj_company_unit(id)` | Related company unit/department. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active cost center flag. |
| `budget_amount` | `decimal(18,2)` | nullable | Budget allocation. |
| `description` | `text` | nullable | Cost center description. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible cost center data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Cost centers enable expense allocation and reporting by department/project.
- Hierarchical structure supports roll-up reporting.

---

## 5. Payroll Management

### 5.1 Overview

Payroll management handles salary and wage payments to employees. This module processes payments, calculates deductions (insurance, taxes), generates accounting entries, and produces bank transfer files.

**Important Note**: Employee master data (personnel information) and payroll decrees (حکم) are managed in the HR module. The accounting module only handles payment processing, accounting entries, and bank file generation aspects of payroll.

### 5.2 Key Features

- **Salary Payment Processing**: Process monthly salary payments based on HR payroll decrees
- **Insurance and Tax Settings**: Configure insurance rates, tax brackets, and deduction rules
- **Payroll Document Upload**: Import payroll documents from external systems or manual entry
- **Bank Transfer File Generation**: Generate bank transfer files in standard formats (CSV, Excel, XML) for bulk salary payments

### 5.3 Payroll Payment Structure

#### Table: `accounting_payroll_payment`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `payment_number` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated payment number (e.g., "PAY-1403-01-000001"). |
| `payment_date` | `date` | `NOT NULL` | Payment date. |
| `payment_period` | `varchar(10)` | `NOT NULL` | Payment period (e.g., "1403-01" for year-month). |
| `person_id` | `bigint` | `NOT NULL`, FK to `production_person(id)` | Employee reference (from HR/Production module). |
| `personnel_code` | `varchar(30)` | nullable | Cached personnel code for reporting. |
| `decree_id` | `bigint` | nullable, FK to `hr_payroll_decree(id)` | Reference to HR payroll decree (حکم). |
| `base_salary` | `decimal(18,2)` | `NOT NULL` | Base salary amount. |
| `allowances` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Total allowances (overtime, bonuses, etc.). |
| `gross_salary` | `decimal(18,2)` | `NOT NULL` | Gross salary (base + allowances). |
| `insurance_employee` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Employee insurance deduction. |
| `insurance_employer` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Employer insurance contribution. |
| `tax_deduction` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Income tax deduction. |
| `other_deductions` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Other deductions (loans, advances, etc.). |
| `total_deductions` | `decimal(18,2)` | `NOT NULL` | Total deductions (insurance + tax + other). |
| `net_salary` | `decimal(18,2)` | `NOT NULL` | Net salary (gross - deductions). |
| `payment_method` | `varchar(30)` | `NOT NULL`, check in ('BANK_TRANSFER', 'CASH', 'CHECK') | Payment method. |
| `bank_account_id` | `bigint` | nullable, FK to `accounting_cash_account(id)` | Bank account for transfer. |
| `employee_bank_account` | `varchar(50)` | nullable | Employee bank account number. |
| `employee_bank_name` | `varchar(200)` | nullable | Employee bank name. |
| `status` | `varchar(20)` | `NOT NULL`, default `'DRAFT'`, check in ('DRAFT', 'CALCULATED', 'APPROVED', 'PAID', 'CANCELLED') | Payment status. |
| `calculated_at` | `timestamp with time zone` | nullable | Calculation timestamp. |
| `calculated_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who calculated payment. |
| `approved_at` | `timestamp with time zone` | nullable | Approval timestamp. |
| `approved_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who approved payment. |
| `paid_at` | `timestamp with time zone` | nullable | Payment timestamp. |
| `paid_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who processed payment. |
| `treasury_transaction_id` | `bigint` | nullable, FK to `accounting_treasury_transaction(id)` | Related treasury transaction. |
| `document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Related accounting document. |
| `bank_file_id` | `bigint` | nullable, FK to `accounting_payroll_bank_file(id)` | Related bank transfer file. |
| `notes` | `text` | nullable | Payment notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible payment data (deduction details, adjustments). |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Payment number format: `PAY-YYYY-MM-XXXXXX` where YYYY-MM is period and XXXXXX is sequence.
- Net salary calculation: `net_salary = gross_salary - total_deductions`.
- Integration with HR/Production module: retrieve employee data via `production_person` table.
- Reference payroll decrees (حکم) defined in HR module.
- Status workflow: DRAFT → CALCULATED → APPROVED → PAID.
- When paid, automatically create treasury transaction and accounting document.

#### Table: `accounting_payroll_payment_detail`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `payment_id` | `bigint` | `NOT NULL`, FK to `accounting_payroll_payment(id)`, ON DELETE CASCADE | Parent payment. |
| `detail_type` | `varchar(30)` | `NOT NULL`, check in ('ALLOWANCE', 'DEDUCTION', 'ADJUSTMENT') | Detail type. |
| `detail_code` | `varchar(50)` | nullable | Detail code (e.g., "OVERTIME", "TAX", "INSURANCE"). |
| `detail_name` | `varchar(200)` | `NOT NULL` | Detail name/description. |
| `amount` | `decimal(18,2)` | `NOT NULL` | Amount (positive for additions, negative for deductions). |
| `calculation_base` | `decimal(18,2)` | nullable | Base amount used for calculation (if percentage-based). |
| `rate` | `decimal(5,2)` | nullable | Rate percentage (if applicable). |
| `is_taxable` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Taxable item flag. |
| `is_insurance_base` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Included in insurance base calculation. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible detail data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |

**Additional considerations:**
- Break down salary components for detailed reporting.
- Track which items are taxable and included in insurance base.
- Support custom allowances and deductions per company policy.

### 5.4 Insurance and Tax Settings

#### Table: `accounting_payroll_insurance_tax_settings`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)`, UNIQUE | Tenant company (one settings record per company). |
| `insurance_employee_rate` | `decimal(5,2)` | `NOT NULL`, default `7.00` | Employee insurance rate percentage. |
| `insurance_employer_rate` | `decimal(5,2)` | `NOT NULL`, default `23.00` | Employer insurance rate percentage. |
| `insurance_base_min` | `decimal(18,2)` | nullable | Minimum insurance base amount. |
| `insurance_base_max` | `decimal(18,2)` | nullable | Maximum insurance base amount (ceiling). |
| `tax_exemption_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Tax exemption threshold. |
| `tax_brackets` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Tax brackets configuration (array of {min, max, rate}). |
| `unemployment_insurance_rate` | `decimal(5,2)` | nullable | Unemployment insurance rate (if applicable). |
| `retirement_contribution_rate` | `decimal(5,2)` | nullable | Retirement contribution rate (if applicable). |
| `effective_date` | `date` | `NOT NULL` | Settings effective date. |
| `expiry_date` | `date` | nullable | Settings expiry date (null if current). |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active settings flag. |
| `notes` | `text` | nullable | Settings notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible settings data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Tax brackets stored as JSON array: `[{"min": 0, "max": 10000000, "rate": 0}, {"min": 10000000, "max": 50000000, "rate": 10}, ...]`.
- Support historical settings for audit trail (keep old settings with expiry_date).
- Insurance base calculation: `insurance_base = min(max(gross_salary, insurance_base_min), insurance_base_max)`.
- Tax calculation: apply progressive tax brackets to taxable income.

#### Table: `accounting_payroll_tax_bracket`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `settings_id` | `bigint` | `NOT NULL`, FK to `accounting_payroll_insurance_tax_settings(id)` | Parent settings. |
| `bracket_order` | `smallint` | `NOT NULL` | Bracket order (1, 2, 3, ...). |
| `min_amount` | `decimal(18,2)` | `NOT NULL` | Minimum taxable amount for bracket. |
| `max_amount` | `decimal(18,2)` | nullable | Maximum taxable amount (null for highest bracket). |
| `tax_rate` | `decimal(5,2)` | `NOT NULL` | Tax rate percentage for this bracket. |
| `description` | `varchar(255)` | nullable | Bracket description. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |

**Additional considerations:**
- Alternative to storing brackets in JSON: dedicated table for easier querying and management.
- Bracket order ensures correct tax calculation (apply brackets sequentially).

### 5.5 Payroll Document Upload

#### Table: `accounting_payroll_document`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `document_number` | `varchar(50)` | `NOT NULL` | Document number/reference. |
| `document_type` | `varchar(30)` | `NOT NULL`, check in ('HR_DECREE', 'EXTERNAL_FILE', 'MANUAL_ENTRY') | Document source type. |
| `upload_date` | `date` | `NOT NULL` | Upload date. |
| `period` | `varchar(10)` | `NOT NULL` | Payroll period (e.g., "1403-01"). |
| `file_name` | `varchar(255)` | nullable | Original file name. |
| `file_path` | `varchar(500)` | nullable | Storage path (if file uploaded). |
| `file_format` | `varchar(20)` | nullable | File format (e.g., "EXCEL", "CSV", "XML"). |
| `record_count` | `integer` | `NOT NULL`, default `0` | Number of records in document. |
| `processed_count` | `integer` | `NOT NULL`, default `0` | Number of records processed. |
| `status` | `varchar(20)` | `NOT NULL`, default `'UPLOADED'`, check in ('UPLOADED', 'PROCESSING', 'PROCESSED', 'ERROR', 'CANCELLED') | Processing status. |
| `error_log` | `text` | nullable | Error log if processing failed. |
| `uploaded_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who uploaded document. |
| `processed_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who processed document. |
| `processed_at` | `timestamp with time zone` | nullable | Processing timestamp. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible document data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- Support import from HR module decrees (via API or database link).
- Support import from external systems or manual entry.
- Support external file uploads (Excel, CSV) with validation.
- Parse uploaded files and create payroll payment records.
- Track processing status and errors for troubleshooting.

#### Table: `accounting_payroll_document_record`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `document_id` | `bigint` | `NOT NULL`, FK to `accounting_payroll_document(id)`, ON DELETE CASCADE | Parent document. |
| `row_number` | `integer` | `NOT NULL` | Row number in source file. |
| `person_id` | `bigint` | nullable, FK to `production_person(id)` | Matched employee. |
| `personnel_code` | `varchar(30)` | nullable | Personnel code from file. |
| `national_id` | `varchar(20)` | nullable | National ID from file. |
| `raw_data` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Raw data from file row. |
| `processed_data` | `jsonb` | nullable | Processed/validated data. |
| `payment_id` | `bigint` | nullable, FK to `accounting_payroll_payment(id)` | Created payment record. |
| `status` | `varchar(20)` | `NOT NULL`, default `'PENDING'`, check in ('PENDING', 'PROCESSED', 'ERROR', 'SKIPPED') | Processing status. |
| `error_message` | `text` | nullable | Error message if processing failed. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |

**Additional considerations:**
- Store raw file data for audit and reprocessing.
- Match employees by personnel code or national ID.
- Track processing status per record for partial processing support.

### 5.6 Bank Transfer File Generation

#### Table: `accounting_payroll_bank_file`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `file_number` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Auto-generated file number (e.g., "BANK-1403-01-000001"). |
| `file_date` | `date` | `NOT NULL` | File generation date. |
| `period` | `varchar(10)` | `NOT NULL` | Payroll period. |
| `bank_id` | `bigint` | `NOT NULL`, FK to `accounting_cash_account(id)` | Bank account for transfers. |
| `file_format` | `varchar(20)` | `NOT NULL`, check in ('CSV', 'EXCEL', 'XML', 'TXT') | File format. |
| `bank_format` | `varchar(50)` | nullable | Bank-specific format (e.g., "MELLI_CSV", "PARSIAN_XML"). |
| `total_records` | `integer` | `NOT NULL`, default `0` | Number of payment records. |
| `total_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Total transfer amount. |
| `file_path` | `varchar(500)` | nullable | Generated file storage path. |
| `file_size` | `bigint` | nullable | File size in bytes. |
| `status` | `varchar(20)` | `NOT NULL`, default `'DRAFT'`, check in ('DRAFT', 'GENERATED', 'SENT', 'PROCESSED', 'CANCELLED') | File status. |
| `generated_at` | `timestamp with time zone` | nullable | Generation timestamp. |
| `generated_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who generated file. |
| `sent_at` | `timestamp with time zone` | nullable | Sent to bank timestamp. |
| `sent_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who sent file. |
| `bank_reference` | `varchar(100)` | nullable | Bank reference number (after processing). |
| `notes` | `text` | nullable | File notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible file data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- File number format: `BANK-YYYY-MM-XXXXXX`.
- Support multiple bank formats (each bank may have different file structure).
- Generate file with payment records marked for bank transfer.
- Track file status through bank processing workflow.

#### Table: `accounting_payroll_bank_file_record`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `bank_file_id` | `bigint` | `NOT NULL`, FK to `accounting_payroll_bank_file(id)`, ON DELETE CASCADE | Parent bank file. |
| `payment_id` | `bigint` | `NOT NULL`, FK to `accounting_payroll_payment(id)` | Related payment. |
| `record_number` | `integer` | `NOT NULL` | Record number in file. |
| `employee_name` | `varchar(200)` | nullable | Employee name (for file). |
| `employee_account` | `varchar(50)` | `NOT NULL` | Employee bank account number. |
| `amount` | `decimal(18,2)` | `NOT NULL` | Transfer amount. |
| `description` | `varchar(255)` | nullable | Transfer description/reference. |
| `status` | `varchar(20)` | nullable, check in ('PENDING', 'PROCESSED', 'FAILED', 'REJECTED') | Bank processing status. |
| `bank_reference` | `varchar(100)` | nullable | Bank transaction reference. |
| `processed_date` | `date` | nullable | Bank processing date. |
| `error_message` | `text` | nullable | Error message if processing failed. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible record data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |

**Additional considerations:**
- Link bank file records to payment records for reconciliation.
- Track bank processing status per record.
- Support reconciliation when bank provides processing results.

### 5.7 Payroll Accounting Integration

#### Automatic Accounting Entry Generation

When payroll payments are processed, the system automatically generates accounting documents:

**Debit Entries:**
- Salary Expense Account (gross salary amount)
- Insurance Expense Account (employer insurance contribution)
- Tax Payable Account (tax deduction amount)

**Credit Entries:**
- Cash/Bank Account (net salary payment)
- Insurance Payable Account (employee + employer insurance)
- Tax Payable Account (tax deduction)
- Other Payable Accounts (other deductions)

**Integration Points:**
- Link `accounting_document.reference_type = 'PAYROLL_PAYMENT'` and `reference_id` to payroll payment ID
- Map salary components to appropriate expense accounts
- Update employee party account balances (if employees are tracked as parties)

### 5.8 Payroll Reports

Payroll reports are now managed by the centralized **Reporting Module**. All payroll-related reports including payroll summary, payroll detail, insurance and tax reports, and bank transfer reports are available through the reporting module.

**Note**: For detailed documentation on payroll reports, see [Reporting Module Design Plan](../docs/reporting_module_design_plan.md#2-accounting-reports) (section 2.2.7 Payroll Summary Report).

**Key Payroll Reports:**
- Payroll Summary Report (گزارش خلاصه حقوق و دستمزد)
- Payroll Detail Report (گزارش تفصیلی حقوق و دستمزد)
- Insurance and Tax Report (گزارش بیمه و مالیات)
- Bank Transfer Report (گزارش انتقال بانکی)

All reports support multiple export formats and can be scheduled for automatic generation.

---

## 6. Party Account Management

### 6.1 Overview

Party accounts represent external entities that the company transacts with: customers, suppliers, banks, employees, and other parties. Each party can have multiple accounts (receivables, payables) and detailed transaction history.

### 6.2 Party Structure

#### Table: `accounting_party`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `party_code` | `varchar(30)` | `NOT NULL`, `UNIQUE` within company | Party code (auto-generated or manual). |
| `party_type` | `varchar(30)` | `NOT NULL`, check in ('CUSTOMER', 'SUPPLIER', 'BANK', 'EMPLOYEE', 'GOVERNMENT', 'OTHER') | Party classification. |
| `party_name` | `varchar(200)` | `NOT NULL` | Party name. |
| `legal_name` | `varchar(200)` | nullable | Legal/registered name. |
| `national_id` | `varchar(20)` | nullable, `UNIQUE` | National ID (for individuals). |
| `economic_code` | `varchar(20)` | nullable, `UNIQUE` | Economic code (for companies). |
| `registration_number` | `varchar(50)` | nullable | Registration number. |
| `tax_id` | `varchar(50)` | nullable | Tax ID. |
| `phone_number` | `varchar(30)` | nullable | Primary phone. |
| `mobile_number` | `varchar(30)` | nullable | Mobile phone. |
| `email` | `varchar(254)` | nullable | Email address. |
| `website` | `varchar(255)` | nullable | Website URL. |
| `address` | `text` | nullable | Physical address. |
| `city` | `varchar(100)` | nullable | City. |
| `state` | `varchar(100)` | nullable | State/Province. |
| `postal_code` | `varchar(20)` | nullable | Postal code. |
| `country` | `varchar(3)` | nullable | ISO country code. |
| `credit_limit` | `decimal(18,2)` | nullable | Credit limit (for customers). |
| `payment_terms` | `varchar(100)` | nullable | Payment terms (e.g., "Net 30"). |
| `default_receivable_account_id` | `bigint` | nullable, FK to `accounting_account(id)` | Default receivable account. |
| `default_payable_account_id` | `bigint` | nullable, FK to `accounting_account(id)` | Default payable account. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active party flag. |
| `notes` | `text` | nullable | Additional notes. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible party data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Party code format: `{PARTY_TYPE_PREFIX}-{SEQUENCE}` (e.g., "CUST-000001" for customer).
- Integration with inventory module: suppliers from `inventory_supplier` can be linked.
- Integration with sales module: customers can be linked.
- National ID and economic code validation per Iranian regulations.

#### Table: `accounting_party_account`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `party_id` | `bigint` | `NOT NULL`, FK to `accounting_party(id)` | Party reference. |
| `account_id` | `bigint` | `NOT NULL`, FK to `accounting_account(id)` | Detail account for party. |
| `account_type` | `varchar(20)` | `NOT NULL`, check in ('RECEIVABLE', 'PAYABLE') | Receivable or payable account. |
| `opening_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Opening balance. |
| `current_balance` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Current balance (calculated). |
| `currency_code` | `varchar(3)` | `NOT NULL`, default `'IRR'` | Account currency. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active account flag. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible account data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- Each party can have multiple accounts (receivable, payable, different currencies).
- Current balance calculated from document lines referencing this party account.
- Unique constraint on `(company_id, party_id, account_id, account_type)`.

#### Table: `accounting_party_transaction`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `party_id` | `bigint` | `NOT NULL`, FK to `accounting_party(id)` | Party reference. |
| `party_account_id` | `bigint` | `NOT NULL`, FK to `accounting_party_account(id)` | Party account reference. |
| `transaction_date` | `date` | `NOT NULL` | Transaction date. |
| `transaction_type` | `varchar(30)` | `NOT NULL` | Transaction type (e.g., 'INVOICE', 'PAYMENT', 'ADJUSTMENT'). |
| `debit_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Debit amount. |
| `credit_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Credit amount. |
| `balance_after` | `decimal(18,2)` | `NOT NULL` | Balance after this transaction. |
| `document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Related accounting document. |
| `document_line_id` | `bigint` | nullable, FK to `accounting_document_line(id)` | Related document line. |
| `reference_number` | `varchar(100)` | nullable | External reference. |
| `description` | `text` | nullable | Transaction description. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible transaction data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |

**Additional considerations:**
- Maintains detailed transaction history for each party account.
- Used for party account statements and aging reports.
- Balance calculation: `balance_after = previous_balance + debit_amount - credit_amount`.

---

## 7. Financial Reports

### 7.1 Overview

Financial reports are now managed by the centralized **Reporting Module**. All accounting reports including balance sheet, income statement, account movements, trial balance, party account statements, VAT reports, and payroll reports are available through the reporting module.

**Note**: For detailed documentation on accounting reports, see [Reporting Module Design Plan](../docs/reporting_module_design_plan.md#2-accounting-reports).

**Key Accounting Reports:**
- Balance Sheet (ترازنامه)
- Income Statement (صورت سود و زیان)
- Account Movements (گردش حساب)
- Trial Balance (تراز آزمایشی)
- Party Account Statement (گزارش تفصیلی طرف حساب)
- VAT Report (گزارش مالیات بر ارزش افزوده)
- Payroll Summary Report (گزارش خلاصه حقوق و دستمزد)

All reports support multiple export formats (PDF, Excel, CSV, HTML) and can be scheduled for automatic generation and delivery.

---

## 8. Tax Compliance Modules

### 8.1 Overview

Tax compliance modules ensure the system meets Iranian tax regulations including VAT (Value Added Tax), TTMS (Tax Transaction Management System) integration, and seasonal transaction reporting.

### 8.2 VAT Management

#### Table: `accounting_vat_transaction`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `transaction_date` | `date` | `NOT NULL` | Transaction date. |
| `transaction_type` | `varchar(30)` | `NOT NULL`, check in ('SALE', 'PURCHASE', 'ADJUSTMENT') | Sale or purchase transaction. |
| `party_id` | `bigint` | nullable, FK to `accounting_party(id)` | Related party. |
| `base_amount` | `decimal(18,2)` | `NOT NULL` | Base amount (before VAT). |
| `vat_rate` | `decimal(5,2)` | `NOT NULL` | VAT rate percentage. |
| `vat_amount` | `decimal(18,2)` | `NOT NULL` | Calculated VAT amount. |
| `total_amount` | `decimal(18,2)` | `NOT NULL` | Total amount (base + VAT). |
| `invoice_number` | `varchar(100)` | nullable | Invoice number. |
| `invoice_date` | `date` | nullable | Invoice date. |
| `is_exempt` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | VAT exemption flag. |
| `exemption_reason` | `varchar(200)` | nullable | Exemption reason. |
| `document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Related accounting document. |
| `reference_type` | `varchar(50)` | nullable | Source reference type. |
| `reference_id` | `bigint` | nullable | Source reference ID. |
| `ttms_status` | `varchar(20)` | nullable, check in ('PENDING', 'SENT', 'CONFIRMED', 'REJECTED') | TTMS submission status. |
| `ttms_reference` | `varchar(100)` | nullable | TTMS reference number. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible VAT data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- VAT calculation: `vat_amount = base_amount * (vat_rate / 100)`.
- Integration with sales and purchase modules for automatic VAT recording.
- TTMS integration for electronic submission to tax authority.

#### Table: `accounting_vat_report`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `report_period` | `varchar(10)` | `NOT NULL` | Period (e.g., "1403-01" for year-month). |
| `report_type` | `varchar(30)` | `NOT NULL`, check in ('SALES', 'PURCHASES', 'SUMMARY') | Report type. |
| `total_base_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Total base amount. |
| `total_vat_amount` | `decimal(18,2)` | `NOT NULL`, default `0.00` | Total VAT amount. |
| `transaction_count` | `integer` | `NOT NULL`, default `0` | Number of transactions. |
| `generated_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Report generation timestamp. |
| `generated_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who generated report. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible report data. |

**Additional considerations:**
- Monthly VAT reports for tax filing.
- Summary reports show net VAT payable/receivable.

### 8.3 TTMS Integration

#### Table: `accounting_ttms_submission`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `submission_date` | `date` | `NOT NULL` | Submission date. |
| `submission_type` | `varchar(30)` | `NOT NULL` | Submission type (e.g., 'INVOICE', 'PAYMENT'). |
| `transaction_count` | `integer` | `NOT NULL` | Number of transactions submitted. |
| `status` | `varchar(20)` | `NOT NULL`, default `'PENDING'`, check in ('PENDING', 'SUBMITTED', 'CONFIRMED', 'REJECTED') | Submission status. |
| `ttms_reference` | `varchar(100)` | nullable | TTMS reference number. |
| `response_data` | `jsonb` | nullable | TTMS response data. |
| `error_message` | `text` | nullable | Error message if rejected. |
| `submitted_at` | `timestamp with time zone` | nullable | Submission timestamp. |
| `submitted_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who submitted. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible submission data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- TTMS API integration for electronic submission.
- Retry mechanism for failed submissions.
- Log all API requests and responses.

### 8.4 Seasonal Transaction Reporting

#### Table: `accounting_seasonal_transaction`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `season` | `varchar(10)` | `NOT NULL` | Season identifier (e.g., "1403-01" for first season of year 1403). |
| `transaction_date` | `date` | `NOT NULL` | Transaction date. |
| `transaction_type` | `varchar(30)` | `NOT NULL`, check in ('SALE', 'PURCHASE') | Sale or purchase. |
| `party_id` | `bigint` | nullable, FK to `accounting_party(id)` | Related party. |
| `party_national_id` | `varchar(20)` | nullable | Party national ID. |
| `party_economic_code` | `varchar(20)` | nullable | Party economic code. |
| `amount` | `decimal(18,2)` | `NOT NULL` | Transaction amount. |
| `vat_amount` | `decimal(18,2)` | nullable | VAT amount. |
| `invoice_number` | `varchar(100)` | nullable | Invoice number. |
| `invoice_date` | `date` | nullable | Invoice date. |
| `description` | `text` | nullable | Transaction description. |
| `document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Related accounting document. |
| `is_exported` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Export flag for seasonal report. |
| `exported_at` | `timestamp with time zone` | nullable | Export timestamp. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible transaction data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |

**Additional considerations:**
- Seasonal reports required by Iranian tax authority (quarterly).
- Export format: XML/CSV per tax authority specifications.
- Include all sales and purchases above threshold.

---

## 9. Fiscal Year Management

### 9.1 Overview

Fiscal year management handles opening and closing of fiscal years, carry-forward of balances, and comparative reporting across fiscal years.

### 9.2 Fiscal Year Structure

#### Table: `accounting_fiscal_year`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `fiscal_year_code` | `varchar(10)` | `NOT NULL`, `UNIQUE` within company | Fiscal year code (e.g., "1403"). |
| `fiscal_year_name` | `varchar(100)` | `NOT NULL` | Fiscal year name. |
| `start_date` | `date` | `NOT NULL` | Fiscal year start date. |
| `end_date` | `date` | `NOT NULL` | Fiscal year end date. |
| `is_current` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Current fiscal year flag. |
| `is_closed` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Closed fiscal year flag. |
| `closed_at` | `timestamp with time zone` | nullable | Closing timestamp. |
| `closed_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who closed the year. |
| `opening_document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Opening entry document. |
| `closing_document_id` | `bigint` | nullable, FK to `accounting_document(id)` | Closing entry document. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible fiscal year data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Only one current fiscal year per company.
- Closing process: close temporary accounts, transfer to retained earnings, create opening entries for next year.
- Unique constraint on `(company_id, fiscal_year_code)`.

#### Table: `accounting_period`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `fiscal_year_id` | `bigint` | `NOT NULL`, FK to `accounting_fiscal_year(id)` | Parent fiscal year. |
| `period_code` | `varchar(10)` | `NOT NULL` | Period code (e.g., "1403-01" for first month). |
| `period_name` | `varchar(100)` | `NOT NULL` | Period name. |
| `start_date` | `date` | `NOT NULL` | Period start date. |
| `end_date` | `date` | `NOT NULL` | Period end date. |
| `is_closed` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Closed period flag. |
| `closed_at` | `timestamp with time zone` | nullable | Closing timestamp. |
| `closed_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who closed the period. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible period data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |

**Additional considerations:**
- Typically monthly periods within a fiscal year.
- Closed periods prevent new transactions (configurable).
- Unique constraint on `(company_id, fiscal_year_id, period_code)`.

### 9.3 Opening and Closing Entries

#### Opening Entry Process

1. **Create Opening Document**: System generates opening document for new fiscal year.
2. **Carry Forward Balances**: Permanent accounts (assets, liabilities, equity) carry forward their closing balances.
3. **Reset Temporary Accounts**: Revenue and expense accounts start with zero balance.
4. **Post Opening Document**: Opening document is posted to establish initial balances.

#### Closing Entry Process

1. **Close Revenue Accounts**: Transfer all revenue account balances to income summary.
2. **Close Expense Accounts**: Transfer all expense account balances to income summary.
3. **Calculate Net Income**: Income summary balance = net profit/loss.
4. **Transfer to Retained Earnings**: Transfer net income to retained earnings account.
5. **Create Closing Document**: System generates closing document with all transfers.
6. **Lock Fiscal Year**: Mark fiscal year as closed, prevent new transactions.

---

## 10. Settings and Configuration

### 10.1 Overview

Settings and configuration module manages system-wide accounting parameters, document numbering, VAT settings, and integration configurations.

### 10.2 Configuration Tables

#### Table: `accounting_company_settings`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)`, UNIQUE | Tenant company (one settings record per company). |
| `default_currency` | `varchar(3)` | `NOT NULL`, default `'IRR'` | Default currency code. |
| `fiscal_year_start_month` | `smallint` | `NOT NULL`, default `1`, check in (1..12) | Fiscal year start month. |
| `fiscal_year_start_day` | `smallint` | `NOT NULL`, default `1`, check in (1..31) | Fiscal year start day. |
| `vat_enabled` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | VAT module enabled flag. |
| `default_vat_rate` | `decimal(5,2)` | nullable | Default VAT rate percentage. |
| `ttms_enabled` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | TTMS integration enabled flag. |
| `ttms_api_url` | `varchar(500)` | nullable | TTMS API endpoint URL. |
| `ttms_api_key` | `varchar(255)` | nullable | TTMS API authentication key (encrypted). |
| `document_number_format` | `varchar(100)` | nullable | Document number format template. |
| `auto_post_documents` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Auto-post documents on creation. |
| `require_document_approval` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Require approval before posting. |
| `decimal_places` | `smallint` | `NOT NULL`, default `2`, check in (0..6) | Decimal places for amounts. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible settings data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- One settings record per company.
- Encrypt sensitive data (API keys, credentials).
- Document number format examples: "DOC-{YYYY}-{NNNNNN}", "DOC-{YYMM}-{NNNN}".

#### Table: `accounting_document_number_sequence`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `document_type` | `varchar(30)` | `NOT NULL` | Document type (e.g., 'MANUAL', 'AUTOMATIC'). |
| `fiscal_year_id` | `bigint` | `NOT NULL`, FK to `accounting_fiscal_year(id)` | Fiscal year for sequence. |
| `sequence_number` | `bigint` | `NOT NULL`, default `0` | Current sequence number. |
| `prefix` | `varchar(10)` | nullable | Document number prefix. |
| `suffix` | `varchar(10)` | nullable | Document number suffix. |
| `format_template` | `varchar(100)` | nullable | Number format template. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible sequence data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `updated_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Last update timestamp. |

**Additional considerations:**
- Unique constraint on `(company_id, document_type, fiscal_year_id)`.
- Use database sequences or atomic increment for thread-safe number generation.
- Reset sequence at start of each fiscal year.

---

## 11. Integration Points

### 11.1 Inventory Module Integration

**Automatic Document Generation:**
- **Permanent Receipts**: Create expense document and inventory asset entries
- **Permanent Issues**: Create cost of goods sold (COGS) entries
- **Consumption Issues**: Create production cost entries
- **Stocktaking Adjustments**: Create inventory adjustment entries

**Integration Points:**
- Link `accounting_document.reference_type = 'INVENTORY_RECEIPT'` and `reference_id` to inventory receipt ID
- Map inventory items to expense/asset accounts based on item type
- Calculate VAT from purchase receipts if supplier is VAT-registered

### 11.2 Sales Module Integration

**Automatic Document Generation:**
- **Sales Invoices**: Create income document and receivable entries
- **Sales Returns**: Create return entries and reverse original income
- **Payment Receipts**: Create cash/bank receipt and reduce receivables

**Integration Points:**
- Link `accounting_document.reference_type = 'SALES_INVOICE'` and `reference_id` to sales invoice ID
- Map sales items to income accounts
- Calculate VAT on sales invoices
- Update party receivable balances

### 11.3 Procurement Module Integration

**Automatic Document Generation:**
- **Purchase Orders**: Create commitment entries (optional)
- **Purchase Receipts**: Create expense/payable entries
- **Purchase Returns**: Create return entries and reverse original expense

**Integration Points:**
- Link accounting documents to procurement documents
- Map procurement items to expense accounts
- Calculate VAT on purchases
- Update party payable balances

### 11.4 Production Module Integration

**Automatic Document Generation:**
- **Production Orders**: Create work-in-progress (WIP) entries
- **Material Consumption**: Transfer from inventory to WIP
- **Finished Goods**: Transfer from WIP to finished goods inventory
- **Production Costs**: Allocate labor, overhead, and material costs

**Integration Points:**
- Link accounting documents to production orders
- Track production costs by cost center
- Calculate cost per unit for finished goods

### 11.5 HR/Production Module Integration

**Employee Data Retrieval:**
- **Employee Information**: Retrieve employee data from `production_person` table
- **Personnel Codes**: Use personnel codes for matching and reporting
- **Company Units**: Link employees to company units for organizational reporting

**Integration Points:**
- Link `accounting_payroll_payment.person_id` to `production_person.id`
- Reference payroll decrees (حکم) defined in HR module via `decree_id` field
- Import employee bank account information from HR/Production records (if available)
- Use personnel codes for matching employees in payroll documents

**Note**: Employee master data (personnel information, company unit assignments) and payroll decrees (حکم), decree groups, decree sub-groups are managed in the HR module. Payment processing and accounting entries are managed in the accounting module.

---

## 12. Implementation Notes

### 12.1 Database Constraints

**Critical Constraints:**
- `accounting_document`: `total_debit = total_credit` (enforced at database level)
- `accounting_document_line`: `(debit_amount > 0 AND credit_amount = 0) OR (debit_amount = 0 AND credit_amount > 0)`
- `accounting_account`: `account_code` unique within company
- `accounting_fiscal_year`: Only one `is_current = 1` per company

**Indexes:**
- `(company_id, document_date)` on `accounting_document` for date range queries
- `(company_id, account_id, transaction_date)` on `accounting_document_line` for account movements
- `(company_id, party_id, transaction_date)` on `accounting_party_transaction` for party statements
- `(company_id, fiscal_year_id, period_code)` on `accounting_period` for period lookups

### 12.2 Business Rules

**Document Workflow:**
1. **DRAFT**: Document created, can be edited/deleted
2. **POSTED**: Document posted to accounts, cannot be edited (can be reversed)
3. **LOCKED**: Document locked for audit, cannot be modified
4. **REVERSED**: Document reversed by creating opposite entries
5. **CANCELLED**: Document cancelled before posting

**Account Balance Calculation:**
- Opening balance + sum of debits - sum of credits = current balance
- Recalculate on document post/reverse
- Consider materialized views for performance

**VAT Calculation:**
- VAT amount = base amount × (VAT rate / 100)
- Round to 2 decimal places (or per company settings)
- Track VAT separately for input (purchases) and output (sales)

### 12.3 Performance Considerations

**Large Dataset Handling:**
- Partition `accounting_document_line` by fiscal year
- Use materialized views for account balances
- Index foreign keys and date columns
- Consider archiving old fiscal years

**Report Generation:**
- Cache frequently accessed reports
- Generate reports asynchronously for large datasets
- Use database views for complex report queries
- Export to Excel/PDF using background tasks

### 12.4 Security Considerations

**Access Control:**
- Use `FeaturePermissionRequiredMixin` for all views
- Define permissions in `shared/permissions.py`:
  - `accounting.documents.create`
  - `accounting.documents.edit`
  - `accounting.documents.post`
  - `accounting.documents.lock`
  - `accounting.reports.view`
  - `accounting.settings.edit`

**Data Protection:**
- Encrypt sensitive data (API keys, bank account numbers)
- Audit trail for all document modifications
- Restrict document deletion to authorized users
- Lock documents after posting to prevent tampering

### 12.5 Localization

**Date Handling:**
- Store dates in Gregorian format in database
- Display dates in Jalali (Persian) format in UI
- Use `JalaliDateField` and `JalaliDateInput` widget
- Support date range filters in reports

**Currency Handling:**
- Default currency: IRR (Iranian Rial)
- Support multiple currencies with exchange rates
- Display amounts with proper formatting (thousand separators)
- Round to appropriate decimal places per currency

---

## 13. Future Enhancements

### 13.1 Planned Features

- **Multi-currency Support**: Full multi-currency accounting with exchange rate management
- **Budget Management**: Budget planning and variance analysis
- **Project Accounting**: Project cost tracking and profitability analysis
- **Fixed Assets Management**: Depreciation calculation and asset register
- **Bank Reconciliation Automation**: Import bank statements and auto-match transactions
- **Advanced Reporting**: Custom report builder, dashboard widgets
- **API Integration**: RESTful API for third-party integrations
- **Mobile App**: Mobile access for approvals and basic operations

### 13.2 Integration Enhancements

- **ERP Integration**: Export/import with external ERP systems
- **Banking Integration**: Direct bank API integration for transaction import
- **E-invoicing**: Electronic invoice generation and submission
- **Payment Gateway**: Integration with payment gateways for online payments

---

## 14. Conclusion

This design document provides a comprehensive blueprint for implementing a full-featured accounting and financial management module within the `invproj` platform. The design follows Iranian accounting standards and tax regulations while maintaining flexibility for future enhancements and integrations.

The modular architecture ensures clean separation of concerns, enabling independent development and testing of each functional area. Integration points with other platform modules (inventory, sales, procurement, production) are clearly defined to support automated accounting entry generation.

Implementation should proceed in phases:
1. **Phase 1**: Chart of accounts, basic document entry, and account balances
2. **Phase 2**: Treasury management, party accounts, and basic reports
3. **Phase 3**: VAT management, income/expense tracking, and advanced reports
4. **Phase 4**: Payroll management (payment processing, insurance/tax settings, bank files)
5. **Phase 5**: Tax compliance (TTMS, seasonal reports) and fiscal year management
6. **Phase 6**: Advanced features and integrations

Each phase should include comprehensive testing, documentation, and user training before proceeding to the next phase.

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: invproj Development Team  
**Status**: Design Phase

