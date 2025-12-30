# Reporting Module Design Plan

## Overview

We are designing `invproj`, a modular warehouse, production, and quality control platform built with Python and Django. The application targets PostgreSQL as the primary database engine and must run seamlessly on both Linux/Nginx and Windows Server/IIS deployments. Django handles server-side rendering and API endpoints, while the architecture leaves room for eventual SPA or mobile front ends. Initially all modules share a single physical database, but careful schema boundaries and naming conventions (`inventory_`, `production_`, `qc_`, `accounting_`, `reporting_`, shared `invproj_`) ensure we can migrate modules into their own services or databases as the system scales. Shared/global entities—companies, users, personnel, company units—reside in the `invproj_` namespace and provide consistent tenancy, security, and configuration anchors throughout the platform.

This document presents the comprehensive reporting module design for the `invproj` platform. The reporting module serves as a centralized reporting system that aggregates and presents reports from all platform modules including inventory, production, accounting, quality control, sales, procurement, HR, and other modules. This centralized approach ensures consistent reporting interfaces, unified export formats, scheduled report generation, and shared report templates across all modules.

The module provides a unified reporting framework that allows users to:
- Access reports from all modules through a single interface
- Generate reports in multiple formats (PDF, Excel, CSV, HTML)
- Schedule automatic report generation and delivery
- Create custom report templates and configurations
- Share and export reports with appropriate access controls
- View historical reports and compare periods

Key design principles:

- **Multi-company tenancy**: Every report configuration stores `company_id` and cached `company_code`, referencing `invproj_company`, to isolate tenant data and enable future sharding.
- **Consistent auditing**: Report configurations include timestamps, creation/update metadata, and optional `metadata` (`jsonb`) for extensibility.
- **Module-agnostic architecture**: Reports are organized by source module but share common infrastructure (templates, export formats, scheduling).
- **Flexible data sources**: Reports can query from single or multiple modules, supporting cross-module analytics.
- **Export capabilities**: All reports support multiple export formats with consistent formatting.
- **Scheduled execution**: Reports can be scheduled for automatic generation and delivery via email or file storage.

The sections below document each functional area with detailed table designs, relationships, constraints, and implementation notes to guide Django model creation, validation rules, and migration planning.

---

## Table of Contents

1. [Module Overview](#1-module-overview)
2. [Accounting Reports](#2-accounting-reports)
3. [Inventory Reports](#3-inventory-reports)
4. [Production Reports](#4-production-reports)
5. [Sales Reports](#5-sales-reports)
6. [Procurement Reports](#6-procurement-reports)
7. [HR Reports](#7-hr-reports)
8. [Quality Control Reports](#8-quality-control-reports)
9. [Ticketing Reports](#9-ticketing-reports)
10. [Cross-Module Reports](#10-cross-module-reports)
11. [Report Infrastructure](#11-report-infrastructure)
12. [Report Scheduling](#12-report-scheduling)
13. [Report Templates and Configuration](#13-report-templates-and-configuration)
14. [Implementation Notes](#14-implementation-notes)
15. [Future Enhancements](#15-future-enhancements)
16. [Conclusion](#16-conclusion)

---

## 1. Module Overview

### 1.1 Purpose

The reporting module provides a centralized reporting infrastructure that:
- Consolidates reports from all platform modules
- Provides consistent user interface and export capabilities
- Enables scheduled report generation and delivery
- Supports custom report templates and configurations
- Maintains report history and audit trails

### 1.2 Architecture

The reporting module acts as a service layer that:
- **Queries data** from various module tables based on report definitions
- **Processes and aggregates** data according to report logic
- **Formats output** using templates and export engines
- **Delivers reports** via web interface, email, or file storage
- **Schedules execution** for automatic report generation

### 1.3 Report Categories

Reports are organized by source module:
- **Accounting Reports**: Financial statements, account movements, tax reports
- **Inventory Reports**: Stock levels, movements, valuation, turnover
- **Production Reports**: BOM usage, production orders, efficiency
- **Sales Reports**: Sales performance, customer analysis, revenue
- **Procurement Reports**: Purchase analysis, supplier performance
- **HR Reports**: Payroll summaries, attendance, personnel
- **Quality Control Reports**: Inspection results, defect analysis
- **Cross-Module Reports**: Integrated analytics across modules

---

## 2. Accounting Reports

### 2.1 Overview

Accounting reports provide financial insights including balance sheets, income statements, account movements, and tax compliance reports. These reports are generated from accounting module data and support financial analysis, auditing, and regulatory compliance.

### 2.2 Report Types

#### 2.2.1 Balance Sheet (ترازنامه)

The balance sheet shows the company's financial position at a specific point in time, displaying assets, liabilities, and equity.

**Report Structure:**
- **Assets**: Current assets (cash, receivables, inventory) and fixed assets (property, equipment)
- **Liabilities**: Current liabilities (payables, short-term debt) and long-term liabilities
- **Equity**: Capital, retained earnings, current year profit/loss

**Key Features:**
- Comparative reporting (current period vs. previous period)
- Multi-level account grouping and roll-up
- Export to PDF/Excel
- Print-friendly format

**Data Source:**
- `accounting_account` table for account structure
- `accounting_account_balance` for period balances
- `accounting_document` and `accounting_document_line` for transaction details

#### 2.2.2 Income Statement (صورت سود و زیان)

The income statement shows company performance over a period, displaying revenues, expenses, and net profit/loss.

**Report Structure:**
- **Revenue**: Operating revenue, other income
- **Cost of Goods Sold (COGS)**: Direct costs
- **Operating Expenses**: Administrative, selling, general expenses
- **Other Income/Expenses**: Non-operating items
- **Net Income**: Final profit/loss

**Key Features:**
- Period comparison (current vs. previous period, current vs. same period last year)
- Percentage of revenue analysis
- Department/cost center breakdown
- Export capabilities

**Data Source:**
- `accounting_account` for revenue and expense accounts
- `accounting_document_line` for transaction details
- `accounting_income_expense` for income/expense records

#### 2.2.3 Account Movements (گردش حساب)

Shows detailed movement of a specific account or account group over a period.

**Report Structure:**
- Opening balance
- Debit transactions (with dates, references, descriptions)
- Credit transactions (with dates, references, descriptions)
- Closing balance

**Key Features:**
- Filter by date range
- Filter by party (for detail accounts)
- Include/exclude sub-accounts
- Export to Excel for further analysis

**Data Source:**
- `accounting_account` for account information
- `accounting_document_line` for transaction lines
- `accounting_document` for document references

#### 2.2.4 Trial Balance (تراز آزمایشی)

Shows all accounts with their debit and credit balances at a specific date.

**Report Structure:**
- Account code and name
- Debit balance
- Credit balance
- Net balance

**Key Features:**
- Verify double-entry bookkeeping (total debits = total credits)
- Include/exclude zero-balance accounts
- Group by account level
- Export capabilities

**Data Source:**
- `accounting_account` for account list
- `accounting_account_balance` for account balances
- Calculated from `accounting_document_line` if balance table not available

#### 2.2.5 Party Account Statement (گزارش تفصیلی طرف حساب)

Detailed statement for a specific party showing all transactions and current balance.

**Report Structure:**
- Party information
- Opening balance
- Transaction list (date, type, debit, credit, balance)
- Closing balance
- Aging analysis (if applicable)

**Key Features:**
- Filter by date range
- Aging buckets (current, 30 days, 60 days, 90+ days)
- Export to PDF/Excel
- Email to party

**Data Source:**
- `accounting_party` for party information
- `accounting_party_account` for account details
- `accounting_party_transaction` for transaction history

#### 2.2.6 VAT Report (گزارش مالیات بر ارزش افزوده)

Summary of VAT transactions for tax filing.

**Report Structure:**
- Sales VAT (output VAT)
- Purchase VAT (input VAT)
- Net VAT payable/receivable
- Transaction details

**Key Features:**
- Filter by period
- Breakdown by transaction type
- Export for tax authority submission
- Integration with TTMS

**Data Source:**
- `accounting_vat_transaction` for VAT transactions
- `accounting_vat_report` for aggregated data

#### 2.2.7 Payroll Summary Report (گزارش خلاصه حقوق و دستمزد)

Summary of payroll payments for a period.

**Report Structure:**
- Total employees paid
- Total gross salary
- Total deductions (insurance, tax, other)
- Total net salary
- Breakdown by department/cost center

**Key Features:**
- Filter by period, department, cost center
- Period comparison
- Export capabilities

**Data Source:**
- `accounting_payroll_payment` for payment records
- `accounting_payroll_payment_detail` for detailed breakdown
- HR module for employee and department data

#### 2.2.8 Payroll Detail Report (گزارش تفصیلی حقوق و دستمزد)

Detailed report per employee showing salary breakdown.

**Report Structure:**
- Employee information
- Salary components (base, allowances)
- Deductions breakdown (insurance, tax, other)
- Net salary
- Payment method and date

**Key Features:**
- Filter by employee, period
- Detailed component breakdown
- Export to PDF/Excel

**Data Source:**
- `accounting_payroll_payment` for payment records
- `accounting_payroll_payment_detail` for detailed breakdown
- `production_person` for employee information

#### 2.2.9 Insurance and Tax Report (گزارش بیمه و مالیات)

Summary of insurance and tax calculations.

**Report Structure:**
- Total insurance base
- Employee insurance contributions
- Employer insurance contributions
- Total tax deductions
- Breakdown by tax brackets

**Key Features:**
- Filter by period
- Tax bracket analysis
- Export capabilities

**Data Source:**
- `accounting_payroll_payment` for payment records
- `accounting_payroll_insurance_tax_settings` for rates
- `accounting_payroll_tax_bracket` for tax brackets

#### 2.2.10 Bank Transfer Report (گزارش انتقال بانکی)

Report of bank transfer file for payroll payments.

**Report Structure:**
- File information
- List of transfers
- Total amount
- Processing status

**Key Features:**
- Filter by file, period, bank
- Transfer status tracking
- Export capabilities

**Data Source:**
- `accounting_payroll_bank_file` for file information
- `accounting_payroll_bank_file_record` for transfer records
- `accounting_payroll_payment` for payment details

---

## 3. Inventory Reports

### 3.1 Overview

Inventory reports provide insights into stock levels, movements, valuation, and turnover. These reports help optimize inventory management and support decision-making.

### 3.2 Report Types

#### 3.2.1 Inventory Balance Report (گزارش موجودی)

Shows current inventory levels by item and warehouse.

**Report Structure:**
- Item information (code, name, category)
- Warehouse location
- Current quantity
- Unit of measure
- Valuation (if applicable)

**Key Features:**
- Filter by warehouse, item category, item type
- Include/exclude zero-balance items
- Export to Excel
- Valuation options (FIFO, LIFO, Average)

**Data Source:**
- `inventory_item` for item information
- `inventory_warehouse` for warehouse information
- Calculated from `inventory_balance` module functions

#### 3.2.2 Inventory Movement Report (گزارش گردش موجودی)

Shows inventory movements (receipts, issues, adjustments) over a period.

**Report Structure:**
- Transaction date and type
- Item and warehouse
- Quantity (in/out)
- Reference document
- Running balance

**Key Features:**
- Filter by date range, item, warehouse
- Group by transaction type
- Export to Excel
- Include lot/batch tracking if applicable

**Data Source:**
- `inventory_receipt_permanent`, `inventory_receipt_temporary`, `inventory_receipt_consignment`
- `inventory_issue_permanent`, `inventory_issue_consumption`, `inventory_issue_consignment`
- `inventory_stocktaking_deficit`, `inventory_stocktaking_surplus`

#### 3.2.3 Inventory Valuation Report (گزارش ارزش موجودی)

Shows inventory value by item, category, or warehouse.

**Report Structure:**
- Item/category/warehouse grouping
- Quantity on hand
- Unit cost
- Total value
- Valuation method

**Key Features:**
- Multiple valuation methods (FIFO, LIFO, Average, Standard)
- Filter by date
- Comparison with previous period
- Export capabilities

**Data Source:**
- `inventory_item` for item information
- Inventory balance calculations
- Cost data from receipts or standard costs

#### 3.2.4 Stock Turnover Report (گزارش گردش کالا)

Shows inventory turnover rates and days on hand.

**Report Structure:**
- Item information
- Average inventory
- Cost of goods sold
- Turnover ratio
- Days on hand

**Key Features:**
- Identify slow-moving items
- Filter by category or warehouse
- Period comparison
- Export to Excel

**Data Source:**
- Inventory movements
- Cost of goods sold from accounting or inventory issues

#### 3.2.5 Supplier Performance Report (گزارش عملکرد تأمین‌کنندگان)

Shows supplier performance metrics.

**Report Structure:**
- Supplier information
- Number of receipts
- Total value
- Average delivery time
- Quality metrics

**Key Features:**
- Filter by date range
- Ranking by performance
- Export capabilities

**Data Source:**
- `inventory_supplier` for supplier information
- `inventory_receipt_permanent` for receipt data
- QC inspection results if available

#### 3.2.6 Purchase Request Report (گزارش درخواست‌های خرید)

Shows purchase requests and their status.

**Report Structure:**
- Request number and date
- Requester information
- Items requested
- Status (draft, pending, approved, rejected)
- Approval information

**Key Features:**
- Filter by status, date range, requester
- Track approval workflow
- Export capabilities

**Data Source:**
- `inventory_purchase_request` for request headers
- `inventory_purchase_request_line` for line items

#### 3.2.7 Warehouse Request Report (گزارش درخواست‌های انبار)

Shows internal warehouse requests for material issuance.

**Report Structure:**
- Request number and date
- Requester information
- Items requested
- Warehouse and destination
- Status and approval information

**Key Features:**
- Filter by status, date range, requester, warehouse
- Track approval workflow
- Export capabilities

**Data Source:**
- `inventory_warehouse_request` for request records
- `inventory_warehouse_request_line` for line items

#### 3.2.8 Stocktaking Report (گزارش شمارش موجودی)

Shows stocktaking records and adjustments.

**Report Structure:**
- Stocktaking record information
- Items counted
- Deficits and surpluses
- Approval status
- Variance analysis

**Key Features:**
- Filter by date range, warehouse, approval status
- Compare physical vs. system counts
- Export capabilities

**Data Source:**
- `inventory_stocktaking_record` for stocktaking records
- `inventory_stocktaking_deficit` for deficit adjustments
- `inventory_stocktaking_surplus` for surplus adjustments

#### 3.2.9 Item Lot Tracking Report (گزارش ردیابی لات)

Shows lot tracking information for traceable items.

**Report Structure:**
- Lot code and information
- Item details
- Receipt date and source
- Consumption/issue history
- Current location

**Key Features:**
- Filter by lot code, item, date range
- Full lot traceability
- Export capabilities

**Data Source:**
- `inventory_item_lot` for lot records
- Receipt and issue documents linked to lots

#### 3.2.10 Item Serial Tracking Report (گزارش ردیابی سریال)

Shows serial number tracking for serialized items.

**Report Structure:**
- Serial number
- Item information
- Current status and location
- Transaction history
- Linked documents

**Key Features:**
- Filter by serial number, item, status
- Complete serial history
- Export capabilities

**Data Source:**
- `inventory_item_serial` for serial records
- `inventory_item_serial_history` for transaction history

---

## 4. Production Reports

### 4.1 Overview

Production reports provide insights into manufacturing operations, BOM usage, production orders, and efficiency metrics.

### 4.2 Report Types

#### 4.2.1 Production Order Status Report (گزارش وضعیت سفارشات تولید)

Shows status of all production orders.

**Report Structure:**
- Order number and date
- Finished item
- Quantity ordered vs. completed
- Status
- Timeline

**Key Features:**
- Filter by status, date range, work center
- Export capabilities
- Visual status indicators

**Data Source:**
- `production_product_order` for order information
- `production_order_performance` for performance data

#### 4.2.2 BOM Usage Report (گزارش مصرف BOM)

Shows material consumption from BOMs.

**Report Structure:**
- Finished item
- Material items consumed
- Quantity used vs. planned
- Variance analysis

**Key Features:**
- Filter by order, date range
- Variance analysis
- Export to Excel

**Data Source:**
- `production_bom` and `production_bom_material` for BOM structure
- `production_product_order` for order data
- Material consumption from inventory issues

#### 4.2.3 Production Efficiency Report (گزارش کارایی تولید)

Shows production efficiency metrics.

**Report Structure:**
- Work center/line
- Planned vs. actual production
- Efficiency percentage
- Downtime analysis

**Key Features:**
- Filter by period, work center
- Trend analysis
- Export capabilities

**Data Source:**
- `production_product_order` for planned production
- `production_order_performance` for actual performance
- `production_work_center` and `production_work_line` for work center data

#### 4.2.4 BOM Usage Analysis Report (گزارش تحلیل مصرف BOM)

Shows detailed BOM consumption analysis.

**Report Structure:**
- Finished item
- BOM version
- Material items and quantities
- Actual vs. planned consumption
- Variance analysis

**Key Features:**
- Filter by finished item, order, date range
- Variance percentage calculation
- Export capabilities

**Data Source:**
- `production_bom` and `production_bom_material` for BOM structure
- `production_product_order` for orders
- Material consumption from inventory issues

#### 4.2.5 Work Center Utilization Report (گزارش بهره‌برداری از مراکز کار)

Shows work center utilization and capacity.

**Report Structure:**
- Work center/line information
- Available capacity
- Utilized capacity
- Utilization percentage
- Pending orders

**Key Features:**
- Filter by work center, period
- Capacity planning insights
- Export capabilities

**Data Source:**
- `production_work_center` and `production_work_line` for work center data
- `production_product_order` for order load
- `production_order_performance` for actual utilization

#### 4.2.6 Machine Status Report (گزارش وضعیت ماشین‌آلات)

Shows machine status and maintenance information.

**Report Structure:**
- Machine information
- Current status (operational, maintenance, idle, broken)
- Last maintenance date
- Next maintenance due
- Work center assignment

**Key Features:**
- Filter by status, work center
- Maintenance scheduling
- Export capabilities

**Data Source:**
- `production_machine` for machine records
- Maintenance schedule and history

#### 4.2.7 Personnel Assignment Report (گزارش تخصیص پرسنل)

Shows personnel assignments to work centers.

**Report Structure:**
- Personnel information
- Work center assignments
- Assignment period
- Primary assignment flag
- Assignment status

**Key Features:**
- Filter by person, work center, date
- Active assignments only option
- Export capabilities

**Data Source:**
- `production_person` for personnel data
- `production_person_assignment` for assignments

#### 4.2.8 Process Performance Report (گزارش عملکرد فرآیند)

Shows process step performance and timing.

**Report Structure:**
- Process definition
- Process steps
- Planned vs. actual time
- Labor and machine time
- Efficiency metrics

**Key Features:**
- Filter by process, order, date range
- Bottleneck identification
- Export capabilities

**Data Source:**
- `production_process` and `production_process_step` for process definitions
- `production_order_performance` for actual performance data

---

## 5. Sales Reports

### 5.1 Overview

Sales reports provide insights into sales performance, customer analysis, and revenue trends.

### 5.2 Report Types

#### 5.2.1 Sales Performance Report (گزارش عملکرد فروش)

Shows sales performance by period, product, customer, or region.

**Report Structure:**
- Sales period
- Revenue by product/customer/region
- Quantity sold
- Growth trends

**Key Features:**
- Multiple grouping options
- Period comparison
- Export capabilities

**Data Source:**
- Sales module tables (to be defined)
- Integration with accounting income records

#### 5.2.2 Customer Analysis Report (گزارش تحلیل مشتری)

Shows customer purchase patterns and value.

**Report Structure:**
- Customer information
- Total purchases
- Purchase frequency
- Average order value
- Customer ranking

**Key Features:**
- Filter by date range
- Customer segmentation
- Export capabilities

**Data Source:**
- Sales module customer data
- Sales transaction data

---

## 6. Procurement Reports

### 6.1 Overview

Procurement reports provide insights into purchase activities, supplier performance, and procurement costs.

### 6.2 Report Types

#### 6.2.1 Purchase Analysis Report (گزارش تحلیل خرید)

Shows purchase activities and trends.

**Report Structure:**
- Purchase period
- Items purchased
- Supplier information
- Total value
- Purchase trends

**Key Features:**
- Filter by supplier, item, date range
- Period comparison
- Export capabilities

**Data Source:**
- Procurement module tables (to be defined)
- Integration with inventory receipts and accounting expenses

---

## 7. HR Reports

### 7.1 Overview

HR reports provide insights into payroll, attendance, and personnel metrics. Note: Payroll reports are also available in the Accounting reports section.

### 7.2 Report Types

#### 7.2.1 Payroll Summary Report (گزارش خلاصه حقوق و دستمزد)

Summary of payroll payments (also available in Accounting reports section).

**Report Structure:**
- Payroll period
- Total employees
- Total gross salary
- Total deductions
- Total net salary
- Department breakdown

**Key Features:**
- Filter by period, department
- Period comparison
- Export capabilities

**Data Source:**
- `accounting_payroll_payment` for payment records
- HR module for employee and department data

#### 7.2.2 Attendance Report (گزارش حضور و غیاب)

Shows employee attendance records.

**Report Structure:**
- Employee information
- Attendance dates
- Hours worked
- Absences
- Overtime

**Key Features:**
- Filter by employee, date range, department
- Attendance patterns
- Export capabilities

**Data Source:**
- HR module attendance tables (to be defined)

#### 7.2.3 Personnel Directory Report (گزارش فهرست پرسنل)

Shows personnel directory information.

**Report Structure:**
- Personnel code and name
- Department/unit assignments
- Contact information
- Employment status
- Assignment details

**Key Features:**
- Filter by department, status, work center
- Export capabilities

**Data Source:**
- `production_person` for personnel data
- `production_person_assignment` for assignments
- `invproj_company_unit` for department information

---

## 9. Ticketing Reports

### 9.1 Overview

Ticketing reports provide insights into ticket management, resolution times, category performance, and support metrics.

### 9.2 Report Types

#### 9.2.1 Ticket Status Report (گزارش وضعیت تیکت‌ها)

Shows status of all tickets.

**Report Structure:**
- Ticket number and creation date
- Category and template
- Priority
- Status (open, in_progress, resolved, closed)
- Assignee information
- Resolution time

**Key Features:**
- Filter by status, category, priority, assignee, date range
- Status distribution charts
- Export capabilities

**Data Source:**
- `ticketing_ticket` for ticket records
- `ticketing_category` for category information
- `ticketing_template` for template information
- `ticketing_priority` for priority information

#### 9.2.2 Ticket Resolution Time Report (گزارش زمان حل تیکت‌ها)

Shows ticket resolution times and SLA compliance.

**Report Structure:**
- Ticket information
- Creation date
- Resolution date
- Resolution time (hours/days)
- SLA target
- SLA compliance status

**Key Features:**
- Filter by category, priority, date range
- Average resolution time calculation
- SLA compliance percentage
- Export capabilities

**Data Source:**
- `ticketing_ticket` for ticket records
- `ticketing_priority` for SLA hours
- Calculated resolution times

#### 9.2.3 Category Performance Report (گزارش عملکرد دسته‌بندی‌ها)

Shows ticket volume and performance by category.

**Report Structure:**
- Category information
- Total tickets
- Open tickets
- Resolved tickets
- Average resolution time
- Resolution rate

**Key Features:**
- Filter by date range
- Category ranking
- Trend analysis
- Export capabilities

**Data Source:**
- `ticketing_category` for category data
- `ticketing_ticket` for ticket statistics

#### 9.2.4 Priority Distribution Report (گزارش توزیع اولویت‌ها)

Shows ticket distribution by priority.

**Report Structure:**
- Priority information
- Number of tickets
- Percentage of total
- Average resolution time
- SLA compliance

**Key Features:**
- Filter by date range, category
- Visual charts
- Export capabilities

**Data Source:**
- `ticketing_priority` for priority data
- `ticketing_ticket` for ticket counts

#### 9.2.5 Assignee Performance Report (گزارش عملکرد مسئولان)

Shows ticket handling performance by assignee.

**Report Structure:**
- Assignee information
- Total tickets assigned
- Resolved tickets
- Average resolution time
- Resolution rate
- Pending tickets

**Key Features:**
- Filter by date range, category
- Performance ranking
- Export capabilities

**Data Source:**
- `ticketing_ticket` for ticket assignments
- `invproj_user` for assignee information

#### 9.2.6 Template Usage Report (گزارش استفاده از قالب‌ها)

Shows usage statistics for ticket templates.

**Report Structure:**
- Template information
- Number of tickets created
- Category association
- Usage frequency
- Average resolution time

**Key Features:**
- Filter by date range, category
- Template popularity ranking
- Export capabilities

**Data Source:**
- `ticketing_template` for template data
- `ticketing_ticket` for usage statistics

#### 9.2.7 Ticket Comments Report (گزارش نظرات تیکت‌ها)

Shows comment activity on tickets.

**Report Structure:**
- Ticket information
- Comment count
- Comment authors
- Comment dates
- Response time

**Key Features:**
- Filter by date range, ticket status
- Activity analysis
- Export capabilities

**Data Source:**
- `ticketing_ticket_comment` for comment records
- `ticketing_ticket` for ticket information

---

## 8. Quality Control Reports

### 8.1 Overview

Quality control reports provide insights into inspection results, defect rates, and quality metrics.

### 8.2 Report Types

#### 8.2.1 Inspection Results Report (گزارش نتایج بازرسی)

Shows quality inspection results.

**Report Structure:**
- Inspection date
- Item/supplier information
- Inspection status
- Defect details
- Inspector information

**Key Features:**
- Filter by date, supplier, item
- Defect analysis
- Export capabilities

**Data Source:**
- `qc_receipt_inspection` for inspection records

#### 8.2.2 Defect Analysis Report (گزارش تحلیل عیوب)

Shows defect patterns and trends.

**Report Structure:**
- Defect type
- Frequency
- Affected items/suppliers
- Trend analysis

**Key Features:**
- Filter by date range, supplier, item
- Defect categorization
- Trend charts
- Export capabilities

**Data Source:**
- QC inspection data
- Defect classification from QC module

#### 8.2.3 Inspection Status Report (گزارش وضعیت بازرسی‌ها)

Shows status of all inspections.

**Report Structure:**
- Inspection code and date
- Temporary receipt information
- Inspector information
- Inspection status
- Approval decision

**Key Features:**
- Filter by status, date range, inspector
- Pending inspections tracking
- Export capabilities

**Data Source:**
- `qc_receipt_inspection` for inspection records
- `inventory_receipt_temporary` for receipt information

#### 8.2.4 Supplier Quality Report (گزارش کیفیت تأمین‌کنندگان)

Shows quality metrics by supplier.

**Report Structure:**
- Supplier information
- Number of inspections
- Pass/fail rates
- Average quality score
- Defect trends

**Key Features:**
- Filter by date range, supplier
- Quality ranking
- Export capabilities

**Data Source:**
- `qc_receipt_inspection` for inspection data
- `inventory_supplier` for supplier information
- `inventory_receipt_temporary` for receipt links

#### 8.2.5 Inspector Performance Report (گزارش عملکرد بازرسان)

Shows inspector activity and performance.

**Report Structure:**
- Inspector information
- Number of inspections
- Inspection completion time
- Approval rate
- Quality metrics

**Key Features:**
- Filter by date range, inspector
- Performance ranking
- Export capabilities

**Data Source:**
- `qc_receipt_inspection` for inspection records
- `production_person` for inspector information

---

## 10. Cross-Module Reports

### 10.1 Overview

Cross-module reports combine data from multiple modules to provide integrated analytics and insights across the entire platform.

### 10.2 Report Types

#### 10.2.1 Profitability Analysis (تحلیل سودآوری)

Combines sales, production, and inventory data to analyze product profitability.

**Report Structure:**
- Product/item information
- Sales revenue
- Production costs
- Inventory costs
- Net profit margin

**Key Features:**
- Filter by product, date range
- Cost breakdown analysis
- Profit margin trends
- Export capabilities

**Data Source:**
- Sales module for revenue
- Production module for costs
- Inventory module for inventory valuation
- Accounting module for financial data

#### 10.2.2 Supply Chain Performance (عملکرد زنجیره تأمین)

Combines procurement, inventory, and production data.

**Report Structure:**
- Supplier performance
- Inventory levels
- Production efficiency
- Overall supply chain metrics

**Key Features:**
- Filter by date range, supplier, product
- End-to-end visibility
- Export capabilities

**Data Source:**
- Procurement module for purchase data
- Inventory module for stock levels
- Production module for production efficiency
- QC module for quality metrics

#### 10.2.3 Material Flow Analysis (تحلیل جریان مواد)

Shows material flow from procurement through production to sales.

**Report Structure:**
- Material items
- Procurement receipts
- Production consumption
- Sales issues
- Inventory levels

**Key Features:**
- Filter by item, date range
- Flow visualization
- Export capabilities

**Data Source:**
- Inventory receipts and issues
- Production BOM consumption
- Sales transactions

#### 10.2.4 Quality Cost Analysis (تحلیل هزینه کیفیت)

Combines QC inspection data with cost information.

**Report Structure:**
- Quality inspection results
- Defect costs
- Rework costs
- Supplier quality costs
- Total quality cost

**Key Features:**
- Filter by date range, supplier, item
- Cost breakdown
- Export capabilities

**Data Source:**
- QC module for inspection data
- Accounting module for cost data
- Inventory module for rework tracking

#### 10.2.5 Production Material Variance (واریانس مواد تولید)

Shows variance between planned and actual material consumption.

**Report Structure:**
- Production order
- BOM materials
- Planned quantities
- Actual consumption
- Variance amount and percentage

**Key Features:**
- Filter by order, date range, item
- Variance analysis
- Export capabilities

**Data Source:**
- Production BOM for planned quantities
- Inventory consumption issues for actual usage
- Production orders for order information

---

## 11. Report Infrastructure

### 11.1 Overview

The report infrastructure provides common services for report generation, formatting, and delivery across all modules.

### 11.2 Core Tables

#### Table: `reporting_report_definition`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `company_code` | `varchar(8)` | `NOT NULL`, check numeric | Cached company code. |
| `report_code` | `varchar(50)` | `NOT NULL`, `UNIQUE` within company | Report identifier code. |
| `report_name` | `varchar(200)` | `NOT NULL` | Report display name. |
| `report_name_en` | `varchar(200)` | nullable | English report name. |
| `module_code` | `varchar(30)` | `NOT NULL` | Source module (e.g., 'accounting', 'inventory', 'production'). |
| `report_category` | `varchar(50)` | `NOT NULL` | Report category within module. |
| `report_type` | `varchar(50)` | `NOT NULL` | Report type identifier. |
| `description` | `text` | nullable | Report description. |
| `query_sql` | `text` | nullable | SQL query for report data (if SQL-based). |
| `query_function` | `varchar(200)` | nullable | Python function name for report data (if function-based). |
| `template_path` | `varchar(500)` | nullable | Template file path for report formatting. |
| `default_filters` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Default filter values. |
| `required_filters` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Required filter fields. |
| `output_formats` | `jsonb` | `NOT NULL`, default `'["PDF", "EXCEL", "CSV", "HTML"]'::jsonb` | Supported output formats. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active report flag. |
| `is_system_report` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | System report (cannot be deleted). |
| `sort_order` | `smallint` | `NOT NULL`, default `0` | Display order. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible report configuration. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |
| `edited_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Last editor reference. |

**Additional considerations:**
- Unique constraint on `(company_id, report_code)`.
- Reports can be SQL-based or function-based (Python).
- Template path points to report template file.
- Default and required filters define report parameters.

#### Table: `reporting_report_execution`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `report_definition_id` | `bigint` | `NOT NULL`, FK to `reporting_report_definition(id)` | Report definition. |
| `execution_date` | `timestamp with time zone` | `NOT NULL`, default `now()` | Execution timestamp. |
| `executed_by_id` | `bigint` | nullable, FK to `invproj_user(id)` | User who executed report. |
| `filters_applied` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Filters used for this execution. |
| `output_format` | `varchar(20)` | `NOT NULL` | Output format (PDF, EXCEL, CSV, HTML). |
| `status` | `varchar(20)` | `NOT NULL`, default `'PENDING'`, check in ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED') | Execution status. |
| `file_path` | `varchar(500)` | nullable | Generated file storage path. |
| `file_size` | `bigint` | nullable | File size in bytes. |
| `execution_time_ms` | `integer` | nullable | Execution time in milliseconds. |
| `error_message` | `text` | nullable | Error message if failed. |
| `row_count` | `integer` | nullable | Number of rows in report. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible execution data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |

**Additional considerations:**
- Track all report executions for audit and history.
- Store generated files for later retrieval.
- Monitor execution time and performance.

#### Table: `reporting_report_config`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `report_definition_id` | `bigint` | `NOT NULL`, FK to `reporting_report_definition(id)` | Report definition. |
| `config_name` | `varchar(200)` | `NOT NULL` | Configuration name. |
| `config_json` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Report configuration (filters, grouping, formatting). |
| `is_default` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Default configuration flag. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active configuration flag. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |

**Additional considerations:**
- Store report templates and configurations for reuse.
- Support custom report definitions per company.
- Multiple configurations per report definition.

---

## 12. Report Scheduling

### 12.1 Overview

Report scheduling allows automatic generation and delivery of reports at specified intervals.

### 12.2 Scheduling Tables

#### Table: `reporting_report_schedule`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `report_definition_id` | `bigint` | `NOT NULL`, FK to `reporting_report_definition(id)` | Report to schedule. |
| `schedule_name` | `varchar(200)` | `NOT NULL` | Schedule name. |
| `schedule_type` | `varchar(20)` | `NOT NULL`, check in ('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY', 'CUSTOM') | Schedule frequency. |
| `schedule_config` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Schedule configuration (days, times, etc.). |
| `filters` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Default filters for scheduled execution. |
| `output_format` | `varchar(20)` | `NOT NULL`, default `'PDF'` | Output format. |
| `delivery_method` | `varchar(30)` | `NOT NULL`, check in ('EMAIL', 'FILE_STORAGE', 'BOTH') | Delivery method. |
| `email_recipients` | `jsonb` | `NOT NULL`, default `'[]'::jsonb` | Email recipient list. |
| `storage_path` | `varchar(500)` | nullable | File storage path. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active schedule flag. |
| `last_executed_at` | `timestamp with time zone` | nullable | Last execution timestamp. |
| `next_execution_at` | `timestamp with time zone` | nullable | Next scheduled execution. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible schedule data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |

**Additional considerations:**
- Schedule configuration stored as JSON (e.g., `{"day_of_week": 1, "time": "09:00"}` for weekly).
- Integration with task queue (Celery) for scheduled execution.
- Track execution history via `reporting_report_execution` table.

---

## 13. Report Templates and Configuration

### 13.1 Overview

Report templates define the visual layout and formatting of reports. Templates can be customized per company or report type.

### 13.2 Template Structure

#### Table: `reporting_report_template`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `bigserial` | PK | Auto-increment surrogate key. |
| `company_id` | `bigint` | `NOT NULL`, FK to `invproj_company(id)` | Tenant company. |
| `template_code` | `varchar(50)` | `NOT NULL`, `UNIQUE` within company | Template identifier. |
| `template_name` | `varchar(200)` | `NOT NULL` | Template name. |
| `report_type` | `varchar(50)` | nullable | Associated report type (if specific). |
| `template_file_path` | `varchar(500)` | `NOT NULL` | Template file path. |
| `template_format` | `varchar(20)` | `NOT NULL`, check in ('HTML', 'PDF', 'EXCEL') | Template format. |
| `is_default` | `smallint` | `NOT NULL`, default `0`, check in (0,1) | Default template flag. |
| `is_active` | `smallint` | `NOT NULL`, default `1`, check in (0,1) | Active template flag. |
| `metadata` | `jsonb` | `NOT NULL`, default `'{}'::jsonb` | Extensible template data. |
| `created_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Auto-populated on insert. |
| `edited_at` | `timestamp with time zone` | `NOT NULL`, default `now()` | Update audit. |
| `created_by_id` | `bigint` | FK to `invproj_user(id)`, nullable | Creator reference. |

**Additional considerations:**
- Templates stored as files (HTML, PDF templates, Excel templates).
- Support for company branding (logos, colors, headers).
- Multiple templates per report type for different formats.

---

## 14. Implementation Notes

### 14.1 Report Generation Process

1. **User Request**: User selects report, applies filters, chooses format
2. **Validation**: Validate filters and permissions
3. **Data Retrieval**: Execute query/function to retrieve data
4. **Data Processing**: Aggregate, calculate, format data
5. **Template Rendering**: Apply template to format output
6. **Export Generation**: Generate file in requested format
7. **Delivery**: Return file to user or send via email/storage

### 14.2 Performance Considerations

- **Caching**: Cache frequently accessed reports
- **Async Generation**: Generate large reports asynchronously
- **Database Optimization**: Optimize queries with proper indexes
- **Materialized Views**: Use materialized views for complex aggregations
- **Pagination**: Support pagination for large datasets

### 14.3 Security Considerations

- **Access Control**: Enforce module-level permissions for reports
- **Data Filtering**: Automatically filter by company and user permissions
- **Sensitive Data**: Mask sensitive information in reports
- **Audit Trail**: Log all report executions

### 14.4 Integration Points

- **Module Integration**: Each module provides report definitions and data access functions
- **Export Engines**: Integration with PDF (WeasyPrint, ReportLab), Excel (openpyxl, xlsxwriter), CSV libraries
- **Task Queue**: Integration with Celery for scheduled reports
- **Email Service**: Integration with email service for report delivery

---

## 15. Future Enhancements

### 15.1 Planned Features

- **Interactive Dashboards**: Visual dashboards with charts and graphs
- **Report Builder**: Drag-and-drop report builder for custom reports
- **Data Export API**: RESTful API for programmatic report generation
- **Advanced Analytics**: Statistical analysis and forecasting
- **Mobile Reports**: Optimized reports for mobile devices

### 15.2 Integration Enhancements

- **BI Tools Integration**: Export to business intelligence tools
- **Real-time Reports**: Real-time data updates in reports
- **Collaborative Reports**: Share and comment on reports
- **Report Versioning**: Track report definition changes

---

## 16. Conclusion

This design document provides a comprehensive blueprint for implementing a centralized reporting module within the `invproj` platform. The module consolidates reports from all platform modules while providing consistent interfaces, export capabilities, and scheduling features.

The modular architecture ensures that each module can define its own reports while sharing common infrastructure for generation, formatting, and delivery. This approach enables scalability and maintainability while providing users with a unified reporting experience.

Implementation should proceed in phases:
1. **Phase 1**: Core infrastructure (report definitions, execution tracking)
2. **Phase 2**: Accounting reports (migrated from accounting module)
3. **Phase 3**: Inventory and production reports
4. **Phase 4**: Sales, procurement, and HR reports
5. **Phase 5**: Cross-module reports and advanced features
6. **Phase 6**: Scheduling and automation

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: invproj Development Team  
**Status**: Design Phase

