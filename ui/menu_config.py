"""
Menu configuration for the application.

This file defines the structure of all menus (top menu and sidebar menu)
in a centralized way to ensure consistency and maintainability.
"""

from typing import List, Dict, Optional, Any


class MenuItem:
    """Represents a single menu item."""
    
    def __init__(
        self,
        name: str,
        url_name: str,
        icon: str = "",
        permission: Optional[str] = None,
        requires_superuser: bool = False,
        requires_staff: bool = False,
        target: str = "_self",
        children: Optional[List['MenuItem']] = None
    ):
        self.name = name
        self.url_name = url_name
        self.icon = icon
        self.permission = permission
        self.requires_superuser = requires_superuser
        self.requires_staff = requires_staff
        self.target = target
        self.children = children or []


class MenuSection:
    """Represents a menu section (module)."""
    
    def __init__(
        self,
        name: str,
        icon: str = "",
        items: Optional[List[MenuItem]] = None,
        permission: Optional[str] = None,
        requires_superuser: bool = False,
        requires_staff: bool = False
    ):
        self.name = name
        self.icon = icon
        self.items = items or []
        self.permission = permission
        self.requires_superuser = requires_superuser
        self.requires_staff = requires_staff


def get_menu_structure() -> List[MenuSection]:
    """
    Returns the complete menu structure for the application.
    
    This structure is used by both top menu and sidebar menu.
    """
    
    menu_sections = [
        # Shared Section
        MenuSection(
            name="Shared",
            icon="icon-settings",
            items=[
                MenuItem(
                    name="Dashboard",
                    url_name="ui:dashboard",
                    icon="icon-dashboard"
                ),
                MenuItem(
                    name="Companies",
                    url_name="shared:companies",
                    icon="icon-building",
                    permission="shared.companies"
                ),
                MenuItem(
                    name="Company Units",
                    url_name="shared:company_units",
                    icon="icon-factory",
                    permission="shared.company_units"
                ),
                MenuItem(
                    name="SMTP Servers",
                    url_name="shared:smtp_servers",
                    icon="icon-email",
                    permission="shared.smtp_servers",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Users",
                    url_name="shared:users",
                    icon="icon-users",
                    permission="shared.users",
                    children=[
                        MenuItem(
                            name="Users",
                            url_name="shared:users",
                            icon="icon-users",
                            permission="shared.users"
                        ),
                        MenuItem(
                            name="Groups",
                            url_name="shared:groups",
                            icon="icon-user",
                            permission="shared.groups"
                        ),
                        MenuItem(
                            name="Access Levels",
                            url_name="shared:access_levels",
                            icon="icon-lock",
                            permission="shared.access_levels"
                        ),
                    ]
                ),
                MenuItem(
                    name="Django Admin",
                    url_name="admin_panel",
                    icon="icon-settings",
                    requires_staff=True,
                    target="_blank"
                ),
            ]
        ),
        
        # Inventory Section
        MenuSection(
            name="Inventory",
            icon="icon-package",
            permission="inventory.dashboard",
            items=[
                MenuItem(
                    name="Items",
                    url_name="inventory:items",
                    icon="icon-clipboard",
                    permission="inventory.master.items",
                    children=[
                        MenuItem(
                            name="Edit Items",
                            url_name="inventory:items",
                            icon="icon-clipboard",
                            permission="inventory.master.items"
                        ),
                        MenuItem(
                            name="Item Serials",
                            url_name="inventory:item_serials",
                            icon="icon-numbers",
                            permission="inventory.master.item_serials"
                        ),
                        MenuItem(
                            name="Inventory Balance",
                            url_name="inventory:inventory_balance",
                            icon="icon-chart",
                            permission="inventory.balance"
                        ),
                    ]
                ),
                MenuItem(
                    name="Warehouses",
                    url_name="inventory:warehouses",
                    icon="icon-store",
                    permission="inventory.master.warehouses"
                ),
                MenuItem(
                    name="Suppliers",
                    url_name="inventory:suppliers",
                    icon="icon-truck",
                    permission="inventory.suppliers.list",
                    children=[
                        MenuItem(
                            name="Supplier Categories",
                            url_name="inventory:supplier_categories",
                            icon="icon-folder",
                            permission="inventory.suppliers.categories"
                        ),
                        MenuItem(
                            name="Supplier List",
                            url_name="inventory:suppliers",
                            icon="icon-truck",
                            permission="inventory.suppliers.list"
                        ),
                    ]
                ),
                MenuItem(
                    name="Receipts",
                    url_name="inventory:receipt_temporary",
                    icon="icon-download",
                    permission="inventory.receipts.temporary",
                    children=[
                        MenuItem(
                            name="Temporary Receipts",
                            url_name="inventory:receipt_temporary",
                            icon="icon-download",
                            permission="inventory.receipts.temporary"
                        ),
                        MenuItem(
                            name="Permanent Receipts",
                            url_name="inventory:receipt_permanent",
                            icon="icon-check",
                            permission="inventory.receipts.permanent"
                        ),
                        MenuItem(
                            name="Consignment Receipts",
                            url_name="inventory:receipt_consignment",
                            icon="icon-package",
                            permission="inventory.receipts.consignment"
                        ),
                    ]
                ),
                MenuItem(
                    name="Issues",
                    url_name="inventory:issue_permanent",
                    icon="icon-upload",
                    permission="inventory.issues.permanent",
                    children=[
                        MenuItem(
                            name="Permanent Issues",
                            url_name="inventory:issue_permanent",
                            icon="icon-upload",
                            permission="inventory.issues.permanent"
                        ),
                        MenuItem(
                            name="Consumption Issues",
                            url_name="inventory:issue_consumption",
                            icon="icon-fire",
                            permission="inventory.issues.consumption"
                        ),
                        MenuItem(
                            name="Consignment Issues",
                            url_name="inventory:issue_consignment",
                            icon="icon-package",
                            permission="inventory.issues.consignment"
                        ),
                        MenuItem(
                            name="حواله انتقال بین انبارها",
                            url_name="inventory:issue_warehouse_transfer",
                            icon="icon-refresh",
                            permission="inventory.issues.warehouse_transfer",
                            requires_superuser=True
                        ),
                    ]
                ),
                MenuItem(
                    name="Stocktaking",
                    url_name="inventory:stocktaking_deficit",
                    icon="icon-chart",
                    permission="inventory.stocktaking.deficit",
                    children=[
                        MenuItem(
                            name="Deficit Records",
                            url_name="inventory:stocktaking_deficit",
                            icon="icon-trend-down",
                            permission="inventory.stocktaking.deficit"
                        ),
                        MenuItem(
                            name="Surplus Records",
                            url_name="inventory:stocktaking_surplus",
                            icon="icon-trend-up",
                            permission="inventory.stocktaking.surplus"
                        ),
                        MenuItem(
                            name="Stocktaking Records",
                            url_name="inventory:stocktaking_records",
                            icon="icon-chart",
                            permission="inventory.stocktaking.records"
                        ),
                    ]
                ),
                MenuItem(
                    name="Purchase Requests",
                    url_name="inventory:purchase_requests",
                    icon="icon-cart",
                    permission="inventory.requests.purchase"
                ),
                MenuItem(
                    name="Warehouse Requests",
                    url_name="inventory:warehouse_requests",
                    icon="icon-clipboard",
                    permission="inventory.requests.warehouse"
                ),
            ]
        ),
        
        # Production Section
        MenuSection(
            name="Production",
            icon="icon-gear",
            permission="production.dashboard",
            items=[
                MenuItem(
                    name="Personnel",
                    url_name="production:personnel",
                    icon="icon-worker",
                    permission="production.personnel"
                ),
                MenuItem(
                    name="Machines",
                    url_name="production:machines",
                    icon="icon-gear",
                    permission="production.machines"
                ),
                MenuItem(
                    name="Work Lines",
                    url_name="production:work_lines",
                    icon="icon-ruler",
                    permission="production.work_lines"
                ),
                MenuItem(
                    name="BOM",
                    url_name="production:bom_list",
                    icon="icon-clipboard",
                    permission="production.bom",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Processes",
                    url_name="production:processes",
                    icon="icon-refresh",
                    permission="production.processes",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Product Orders",
                    url_name="production:product_orders",
                    icon="icon-package",
                    permission="production.product_orders",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Transfer to Line Requests",
                    url_name="production:transfer_requests",
                    icon="icon-truck",
                    permission="production.transfer_requests",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Performance Records",
                    url_name="production:performance_records",
                    icon="icon-chart",
                    permission="production.performance_records",
                    requires_superuser=True
                ),
                MenuItem(
                    name="QC Operations",
                    url_name="production:qc_operations",
                    icon="icon-lab",
                    permission="production.qc_operations",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Rework",
                    url_name="production:rework_document_list",
                    icon="icon-refresh",
                    permission="production.rework",
                    requires_superuser=True
                ),
                MenuItem(
                    name="شناسایی و ردیابی",
                    url_name="production:tracking_identification",
                    icon="icon-search",
                    permission="production.tracking_identification",
                    requires_superuser=True
                ),
            ]
        ),
        
        # Quality Control Section
        MenuSection(
            name="Quality Control",
            icon="icon-lab",
            permission="qc.dashboard",
            requires_superuser=True,
            items=[
                MenuItem(
                    name="Inspections",
                    url_name="qc:temporary_receipts",
                    icon="icon-search",
                    permission="qc.inspections"
                ),
                MenuItem(
                    name="Serial Assignment",
                    url_name="qc:serial_assignment_list",
                    icon="icon-tag",
                    permission="qc.serials"
                ),
                MenuItem(
                    name="Batch Assignment",
                    url_name="qc:batch_assignment_list",
                    icon="icon-tag",
                    permission="qc.serials"
                ),
            ]
        ),
        
        # Ticketing Section
        MenuSection(
            name="Ticketing",
            icon="icon-ticket",
            permission="ticketing.dashboard",
            requires_superuser=True,
            items=[
                MenuItem(
                    name="Create Ticket",
                    url_name="ticketing:ticket_create",
                    icon="icon-plus",
                    permission="ticketing.ticket.create"
                ),
                MenuItem(
                    name="Respond to Ticket",
                    url_name="ticketing:ticket_respond",
                    icon="icon-message",
                    permission="ticketing.ticket.respond"
                ),
                MenuItem(
                    name="Templates",
                    url_name="ticketing:templates",
                    icon="icon-edit",
                    permission="ticketing.management.templates"
                ),
                MenuItem(
                    name="Categories",
                    url_name="ticketing:categories",
                    icon="icon-folder-open",
                    permission="ticketing.management.categories"
                ),
                MenuItem(
                    name="Subcategories",
                    url_name="ticketing:subcategories",
                    icon="icon-folder",
                    permission="ticketing.management.subcategories"
                ),
                MenuItem(
                    name="Auto Response",
                    url_name="ticketing:auto_response",
                    icon="icon-robot",
                    permission="ticketing.auto_response"
                ),
            ]
        ),
        
        # Accounting Section
        MenuSection(
            name="Accounting",
            icon="icon-money",
            permission="accounting.dashboard",
            items=[
                MenuItem(
                    name="تعاریف پایه",
                    url_name="accounting:fiscal_years",
                    icon="icon-settings",
                    permission="accounting.base",
                    children=[
                        MenuItem(
                            name="سال مالی",
                            url_name="accounting:fiscal_years",
                            icon="icon-calendar",
                            permission="accounting.fiscal_years"
                        ),
                        MenuItem(
                            name="گروه حساب‌ها",
                            url_name="accounting:account_groups",
                            icon="icon-folder",
                            permission="accounting.accounts.groups"
                        ),
                        MenuItem(
                            name="چارت حساب‌ها",
                            url_name="accounting:accounts",
                            icon="icon-chart",
                            permission="accounting.accounts"
                        ),
                        MenuItem(
                            name="تعریف حساب کل",
                            url_name="accounting:gl_accounts",
                            icon="icon-clipboard",
                            permission="accounting.accounts.gl"
                        ),
                        MenuItem(
                            name="تعریف حساب معین",
                            url_name="accounting:sub_accounts",
                            icon="icon-clipboard",
                            permission="accounting.accounts.sub"
                        ),
                        MenuItem(
                            name="انواع تفصیلی",
                            url_name="accounting:tafsili_types",
                            icon="icon-list",
                            permission="accounting.accounts.tafsili"
                        ),
                        MenuItem(
                            name="تعریف حساب تفصیلی",
                            url_name="accounting:tafsili_accounts",
                            icon="icon-clipboard",
                            permission="accounting.accounts.tafsili"
                        ),
                        MenuItem(
                            name="مراکز هزینه",
                            url_name="accounting:cost_centers",
                            icon="icon-building",
                            permission="accounting.income_expense.cost_centers"
                        ),
                        MenuItem(
                            name="دسته‌بندی درآمد و هزینه",
                            url_name="accounting:income_expense_categories",
                            icon="icon-chart",
                            permission="accounting.income_expense.categories"
                        ),
                        MenuItem(
                            name="طرف حساب‌ها",
                            url_name="accounting:parties",
                            icon="icon-users",
                            permission="accounting.parties.list"
                        ),
                        MenuItem(
                            name="حساب‌های نقدی و بانکی",
                            url_name="accounting:treasury_accounts",
                            icon="icon-money",
                            permission="accounting.treasury.accounts"
                        ),
                    ]
                ),
                MenuItem(
                    name="اسناد حسابداری",
                    url_name="accounting:document_create",
                    icon="icon-edit",
                    permission="accounting.documents.create",
                    children=[
                        MenuItem(
                            name="ثبت سند حسابداری",
                            url_name="accounting:document_create",
                            icon="icon-edit",
                            permission="accounting.documents.create"
                        ),
                        MenuItem(
                            name="لیست اسناد حسابداری",
                            url_name="accounting:document_list",
                            icon="icon-clipboard",
                            permission="accounting.documents.list"
                        ),
                        MenuItem(
                            name="سندهای باز، قطعی، برگشتی",
                            url_name="accounting:document_status",
                            icon="icon-check",
                            permission="accounting.documents.status"
                        ),
                        MenuItem(
                            name="گردش حساب",
                            url_name="accounting:report_account_movements",
                            icon="icon-chart",
                            permission="accounting.reports.account_movements"
                        ),
                        MenuItem(
                            name="گردش تفصیلی",
                            url_name="accounting:tafsili_movements",
                            icon="icon-chart",
                            permission="accounting.documents.tafsili_movements"
                        ),
                        MenuItem(
                            name="تراز آزمایشی",
                            url_name="accounting:report_trial_balance",
                            icon="icon-chart",
                            permission="accounting.reports.trial_balance"
                        ),
                        MenuItem(
                            name="ترازنامه",
                            url_name="accounting:report_balance_sheet",
                            icon="icon-chart",
                            permission="accounting.reports.balance_sheet"
                        ),
                        MenuItem(
                            name="صورت سود و زیان",
                            url_name="accounting:report_income_statement",
                            icon="icon-chart",
                            permission="accounting.reports.income_statement"
                        ),
                    ]
                ),
                MenuItem(
                    name="خزانه‌داری",
                    url_name="accounting:treasury_receive",
                    icon="icon-money",
                    permission="accounting.treasury.receive",
                    children=[
                        MenuItem(
                            name="دریافت",
                            url_name="accounting:treasury_receive",
                            icon="icon-money",
                            permission="accounting.treasury.receive"
                        ),
                        MenuItem(
                            name="پرداخت",
                            url_name="accounting:treasury_pay",
                            icon="icon-money-out",
                            permission="accounting.treasury.pay"
                        ),
                        MenuItem(
                            name="تراکنش‌های خزانه",
                            url_name="accounting:treasury_transactions",
                            icon="icon-chart",
                            permission="accounting.treasury.transactions"
                        ),
                        MenuItem(
                            name="انتقال بین حساب‌ها",
                            url_name="accounting:treasury_transfer",
                            icon="icon-refresh",
                            permission="accounting.treasury.transfer"
                        ),
                        MenuItem(
                            name="حساب‌های نقدی و بانکی",
                            url_name="accounting:treasury_accounts",
                            icon="icon-money",
                            permission="accounting.treasury.accounts"
                        ),
                        MenuItem(
                            name="مدیریت چک‌ها",
                            url_name="accounting:treasury_checks",
                            icon="icon-check",
                            permission="accounting.treasury.checks"
                        ),
                        MenuItem(
                            name="تطبیق بانکی",
                            url_name="accounting:treasury_reconciliation",
                            icon="icon-check",
                            permission="accounting.treasury.reconciliation"
                        ),
                        MenuItem(
                            name="گزارش وجوه نقد و بانک‌ها",
                            url_name="accounting:treasury_cash_report",
                            icon="icon-chart",
                            permission="accounting.treasury.cash_report"
                        ),
                        MenuItem(
                            name="درخواست‌های پرداخت",
                            url_name="accounting:payment_requests",
                            icon="icon-money",
                            permission="accounting.payment_requests.list"
                        ),
                        MenuItem(
                            name="تخصیص مرکز هزینه",
                            url_name="accounting:cost_allocation",
                            icon="icon-chart",
                            permission="accounting.income_expense.cost_allocation"
                        ),
                        MenuItem(
                            name="گزارش درآمد",
                            url_name="accounting:income_report",
                            icon="icon-chart",
                            permission="accounting.income_expense.income_report"
                        ),
                        MenuItem(
                            name="گزارش هزینه",
                            url_name="accounting:expense_report",
                            icon="icon-chart",
                            permission="accounting.income_expense.expense_report"
                        ),
                        MenuItem(
                            name="گزارش مراکز هزینه",
                            url_name="accounting:cost_center_report",
                            icon="icon-chart",
                            permission="accounting.income_expense.cost_center_report"
                        ),
                    ]
                ),
                MenuItem(
                    name="طرف حساب‌ها",
                    url_name="accounting:parties",
                    icon="icon-users",
                    permission="accounting.parties.list",
                    children=[
                        MenuItem(
                            name="لیست طرف حساب‌ها",
                            url_name="accounting:parties",
                            icon="icon-users",
                            permission="accounting.parties.list"
                        ),
                        MenuItem(
                            name="گردش طرف حساب",
                            url_name="accounting:party_movements",
                            icon="icon-chart",
                            permission="accounting.parties.movements"
                        ),
                        MenuItem(
                            name="گزارش مانده طرف حساب‌ها",
                            url_name="accounting:party_balance_report",
                            icon="icon-chart",
                            permission="accounting.parties.balance_report"
                        ),
                    ]
                ),
                MenuItem(
                    name="حقوق و دستمزد",
                    url_name="accounting:payroll_payment",
                    icon="icon-dollar",
                    permission="accounting.payroll.payment",
                    children=[
                        MenuItem(
                            name="پرداخت حقوق و دستمزد",
                            url_name="accounting:payroll_payment",
                            icon="icon-dollar",
                            permission="accounting.payroll.payment"
                        ),
                        MenuItem(
                            name="تنظیمات بیمه و مالیات",
                            url_name="accounting:payroll_insurance_tax",
                            icon="icon-settings",
                            permission="accounting.payroll.insurance_tax"
                        ),
                        MenuItem(
                            name="بارگذاری اسناد حقوق و دستمزد",
                            url_name="accounting:payroll_document",
                            icon="icon-upload",
                            permission="accounting.payroll.document"
                        ),
                        MenuItem(
                            name="خروجی حقوق و دستمزد برای بانک",
                            url_name="accounting:payroll_bank_transfer",
                            icon="icon-download",
                            permission="accounting.payroll.bank_transfer"
                        ),
                    ]
                ),
                MenuItem(
                    name="مالیات و مقررات",
                    url_name="accounting:tax_vat",
                    icon="icon-settings",
                    permission="accounting.tax.vat",
                    children=[
                        MenuItem(
                            name="مدیریت VAT",
                            url_name="accounting:tax_vat",
                            icon="icon-settings",
                            permission="accounting.tax.vat"
                        ),
                        MenuItem(
                            name="تنظیمات سامانه مودیان",
                            url_name="accounting:tax_moadian_settings",
                            icon="icon-settings",
                            permission="accounting.tax.moadian_settings"
                        ),
                        MenuItem(
                            name="گزارش VAT",
                            url_name="accounting:report_vat",
                            icon="icon-chart",
                            permission="accounting.reports.vat"
                        ),
                        MenuItem(
                            name="گزارش فصلی (TTMS / ماده 169)",
                            url_name="accounting:tax_seasonal",
                            icon="icon-chart",
                            permission="accounting.tax.seasonal"
                        ),
                        MenuItem(
                            name="اعتبارسنجی اسناد برای ارسال به سامانه مودیان",
                            url_name="accounting:tax_validation",
                            icon="icon-check",
                            permission="accounting.tax.validation"
                        ),
                        MenuItem(
                            name="گزارش مغایرت مالیاتی",
                            url_name="accounting:tax_discrepancy_report",
                            icon="icon-chart",
                            permission="accounting.tax.discrepancy_report"
                        ),
                    ]
                ),
                MenuItem(
                    name="گزارشات مالی",
                    url_name="accounting:report_trial_balance",
                    icon="icon-chart",
                    permission="accounting.reports.trial_balance",
                    children=[
                        MenuItem(
                            name="تراز آزمایشی",
                            url_name="accounting:report_trial_balance",
                            icon="icon-chart",
                            permission="accounting.reports.trial_balance"
                        ),
                        MenuItem(
                            name="ترازنامه",
                            url_name="accounting:report_balance_sheet",
                            icon="icon-chart",
                            permission="accounting.reports.balance_sheet"
                        ),
                        MenuItem(
                            name="سود و زیان",
                            url_name="accounting:report_income_statement",
                            icon="icon-chart",
                            permission="accounting.reports.income_statement"
                        ),
                        MenuItem(
                            name="جریان وجوه نقد",
                            url_name="accounting:report_cash_flow",
                            icon="icon-chart",
                            permission="accounting.reports.cash_flow"
                        ),
                        MenuItem(
                            name="گزارش حساب‌ها",
                            url_name="accounting:report_account_movements",
                            icon="icon-chart",
                            permission="accounting.reports.account_movements"
                        ),
                        MenuItem(
                            name="گزارش تفصیلی و مراکز هزینه",
                            url_name="accounting:report_tafsili_cost_center",
                            icon="icon-chart",
                            permission="accounting.reports.tafsili_cost_center"
                        ),
                        MenuItem(
                            name="گزارش چک‌ها",
                            url_name="accounting:report_checks",
                            icon="icon-chart",
                            permission="accounting.reports.check_report"
                        ),
                        MenuItem(
                            name="گزارش خزانه",
                            url_name="accounting:report_treasury",
                            icon="icon-chart",
                            permission="accounting.reports.treasury_report"
                        ),
                        MenuItem(
                            name="گزارش طرف حساب",
                            url_name="accounting:report_party_statement",
                            icon="icon-chart",
                            permission="accounting.reports.party_statement"
                        ),
                        MenuItem(
                            name="گزارش VAT",
                            url_name="accounting:report_vat",
                            icon="icon-chart",
                            permission="accounting.reports.vat"
                        ),
                        MenuItem(
                            name="گزارش عملیات ماهانه",
                            url_name="accounting:report_monthly",
                            icon="icon-chart",
                            permission="accounting.reports.monthly"
                        ),
                    ]
                ),
                MenuItem(
                    name="اسناد و فایل‌ها",
                    url_name="accounting:attachment_upload",
                    icon="icon-upload",
                    permission="accounting.attachments.upload",
                    children=[
                        MenuItem(
                            name="بارگذاری اسناد",
                            url_name="accounting:attachment_upload",
                            icon="icon-upload",
                            permission="accounting.attachments.upload"
                        ),
                        MenuItem(
                            name="مدیریت اسناد پیوست",
                            url_name="accounting:attachment_list",
                            icon="icon-clipboard",
                            permission="accounting.attachments.list"
                        ),
                        MenuItem(
                            name="پیوست به سند",
                            url_name="accounting:attachment_attach",
                            icon="icon-link",
                            permission="accounting.attachments.attach_to_document"
                        ),
                    ]
                ),
                MenuItem(
                    name="خودکارسازی",
                    url_name="accounting:automation_processes",
                    icon="icon-gear",
                    permission="accounting.automation.processes",
                    children=[
                        MenuItem(
                            name="فرایندهای خودکار",
                            url_name="accounting:automation_processes",
                            icon="icon-gear",
                            permission="accounting.automation.processes"
                        ),
                        MenuItem(
                            name="ایجاد فرایند خودکار",
                            url_name="accounting:automation_process_create",
                            icon="icon-gear",
                            permission="accounting.automation.processes"
                        ),
                        MenuItem(
                            name="لاگ اجرا",
                            url_name="accounting:automation_execution_logs",
                            icon="icon-chart",
                            permission="accounting.automation.logs"
                        ),
                    ]
                ),
                MenuItem(
                    name="ابزارها و عملیات تکمیلی",
                    url_name="accounting:close_temp_accounts",
                    icon="icon-gear",
                    permission="accounting.utils.close_temp",
                    children=[
                        MenuItem(
                            name="بستن حساب‌های موقت",
                            url_name="accounting:close_temp_accounts",
                            icon="icon-check",
                            permission="accounting.utils.close_temp"
                        ),
                        MenuItem(
                            name="افتتاحیه خودکار",
                            url_name="accounting:opening_entry",
                            icon="icon-calendar",
                            permission="accounting.utils.opening"
                        ),
                        MenuItem(
                            name="اختتامیه",
                            url_name="accounting:closing_entry",
                            icon="icon-calendar",
                            permission="accounting.utils.closing"
                        ),
                        MenuItem(
                            name="یکپارچه‌سازی اطلاعات",
                            url_name="accounting:integration",
                            icon="icon-link",
                            permission="accounting.utils.integration"
                        ),
                        MenuItem(
                            name="پشتیبان‌گیری و بازیابی",
                            url_name="accounting:backup_restore",
                            icon="icon-download",
                            permission="accounting.utils.backup"
                        ),
                    ]
                ),
                MenuItem(
                    name="حسابداری انبار",
                    url_name="accounting:warehouse_expense",
                    icon="icon-store",
                    permission="accounting.warehouse.expense",
                    children=[
                        MenuItem(
                            name="سند هزینه انبار",
                            url_name="accounting:warehouse_expense",
                            icon="icon-money-out",
                            permission="accounting.warehouse.expense"
                        ),
                        MenuItem(
                            name="سند درآمد انبار",
                            url_name="accounting:warehouse_income",
                            icon="icon-money",
                            permission="accounting.warehouse.income"
                        ),
                        MenuItem(
                            name="افتتاحیه و اختتامیه",
                            url_name="accounting:warehouse_opening_closing",
                            icon="icon-calendar",
                            permission="accounting.warehouse.opening_closing"
                        ),
                        MenuItem(
                            name="تنظیمات حسابداری انبار",
                            url_name="accounting:warehouse_settings",
                            icon="icon-settings",
                            permission="accounting.warehouse.settings"
                        ),
                    ]
                ),
                MenuItem(
                    name="تنظیمات",
                    url_name="accounting:settings",
                    icon="icon-settings",
                    permission="accounting.settings",
                    children=[
                        MenuItem(
                            name="تنظیمات حسابداری",
                            url_name="accounting:settings",
                            icon="icon-settings",
                            permission="accounting.settings"
                        ),
                        MenuItem(
                            name="تنظیمات خزانه",
                            url_name="accounting:settings_treasury",
                            icon="icon-money",
                            permission="accounting.settings.treasury"
                        ),
                        MenuItem(
                            name="تنظیمات مالیات",
                            url_name="accounting:settings_tax",
                            icon="icon-settings",
                            permission="accounting.settings.tax"
                        ),
                    ]
                ),
            ]
        ),
        
        # Sales Section
        MenuSection(
            name="Sales",
            icon="icon-cart",
            permission="sales.dashboard",
            items=[
                MenuItem(
                    name="Dashboard",
                    url_name="sales:dashboard",
                    icon="icon-chart",
                    permission="sales.dashboard"
                ),
                MenuItem(
                    name="Item Price Cards",
                    url_name="sales:price_card_list",
                    icon="icon-list",
                    permission="sales.price_card",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Sales Invoice",
                    url_name="sales:invoice_create",
                    icon="icon-receipt",
                    permission="sales.invoice"
                ),
                MenuItem(
                    name="مشتریان",
                    url_name="sales:customers",
                    icon="icon-users",
                    permission="sales.customers",
                    requires_superuser=True
                ),
                MenuItem(
                    name="محل دریافت درآمد",
                    url_name="sales:income_receipt_location_list",
                    icon="icon-location",
                    permission="sales.income_receipt_location",
                    requires_superuser=True
                ),
                MenuItem(
                    name="تنظیمات",
                    url_name="sales:settings",
                    icon="icon-settings",
                    permission="sales.settings",
                    requires_superuser=True
                ),
            ]
        ),
        
        # Human Resources Section
        MenuSection(
            name="Human Resources",
            icon="icon-users",
            permission="hr.dashboard",
            items=[
                MenuItem(
                    name="Dashboard",
                    url_name="hr:dashboard",
                    icon="icon-chart",
                    permission="hr.dashboard"
                ),
                MenuItem(
                    name="Personnel",
                    url_name="hr:personnel_create",
                    icon="icon-user",
                    permission="hr.personnel",
                    children=[
                        MenuItem(
                            name="Create Personnel",
                            url_name="hr:personnel_create",
                            icon="icon-user",
                            permission="hr.personnel"
                        ),
                        MenuItem(
                            name="Assign Decree",
                            url_name="hr:personnel_decree_assignment",
                            icon="icon-check",
                            permission="hr.personnel.decree"
                        ),
                        MenuItem(
                            name="Personnel Form",
                            url_name="hr:personnel_form_create",
                            icon="icon-edit",
                            permission="hr.personnel.form"
                        ),
                        MenuItem(
                            name="Form Groups",
                            url_name="hr:personnel_form_groups",
                            icon="icon-folder",
                            permission="hr.personnel.form_groups"
                        ),
                        MenuItem(
                            name="Form Subgroups",
                            url_name="hr:personnel_form_subgroups",
                            icon="icon-folder",
                            permission="hr.personnel.form_subgroups"
                        ),
                    ]
                ),
                MenuItem(
                    name="حکم‌های حقوق و دستمزد",
                    url_name="hr:payroll_decrees",
                    icon="icon-dollar",
                    permission="hr.payroll.decrees",
                    children=[
                        MenuItem(
                            name="حکم‌ها",
                            url_name="hr:payroll_decrees",
                            icon="icon-dollar",
                            permission="hr.payroll.decrees"
                        ),
                        MenuItem(
                            name="گروه‌بندی حکم‌ها",
                            url_name="hr:payroll_decree_groups",
                            icon="icon-folder",
                            permission="hr.payroll.decree_groups"
                        ),
                        MenuItem(
                            name="زیر گروه‌بندی حکم‌ها",
                            url_name="hr:payroll_decree_subgroups",
                            icon="icon-folder",
                            permission="hr.payroll.decree_subgroups"
                        ),
                    ]
                ),
                MenuItem(
                    name="Loans",
                    url_name="hr:loans_management",
                    icon="icon-card",
                    permission="hr.loans.management",
                    children=[
                        MenuItem(
                            name="Loan Management",
                            url_name="hr:loans_management",
                            icon="icon-card",
                            permission="hr.loans.management"
                        ),
                        MenuItem(
                            name="Scheduling",
                            url_name="hr:loans_scheduling",
                            icon="icon-calendar",
                            permission="hr.loans.scheduling"
                        ),
                        MenuItem(
                            name="Savings Fund",
                            url_name="hr:loans_savings_fund",
                            icon="icon-money",
                            permission="hr.loans.savings_fund"
                        ),
                    ]
                ),
                MenuItem(
                    name="Leave Requests",
                    url_name="hr:requests_leave",
                    icon="icon-beach",
                    permission="hr.requests.leave"
                ),
                MenuItem(
                    name="Sick Leave Requests",
                    url_name="hr:requests_sick_leave",
                    icon="icon-hospital",
                    permission="hr.requests.sick_leave"
                ),
                MenuItem(
                    name="Loan Requests",
                    url_name="hr:requests_loan",
                    icon="icon-card",
                    permission="hr.requests.loan"
                ),
            ]
        ),
        
        # Requests Section
        MenuSection(
            name="Requests",
            icon="icon-clipboard",
            items=[
                MenuItem(
                    name="Purchase Request",
                    url_name="inventory:purchase_requests",
                    icon="icon-cart",
                    permission="inventory.requests.purchase"
                ),
                MenuItem(
                    name="Warehouse Request",
                    url_name="inventory:warehouse_requests",
                    icon="icon-clipboard",
                    permission="inventory.requests.warehouse"
                ),
                MenuItem(
                    name="Service Request",
                    url_name="procurement:service_requests",
                    icon="icon-service",
                    permission="procurement.services.request",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Transfer to Line Requests",
                    url_name="production:transfer_requests",
                    icon="icon-truck",
                    permission="production.transfer_requests",
                    requires_superuser=True
                ),
                MenuItem(
                    name="Leave Request",
                    url_name="hr:requests_leave",
                    icon="icon-beach",
                    permission="hr.requests.leave"
                ),
                MenuItem(
                    name="Sick Leave Request",
                    url_name="hr:requests_sick_leave",
                    icon="icon-hospital",
                    permission="hr.requests.sick_leave"
                ),
                MenuItem(
                    name="Loan Request",
                    url_name="hr:requests_loan",
                    icon="icon-card",
                    permission="hr.requests.loan"
                ),
            ]
        ),
        
        # Office Automation Section
        MenuSection(
            name="Office Automation",
            icon="icon-clipboard",
            permission="office_automation.dashboard",
            items=[
                MenuItem(
                    name="Dashboard",
                    url_name="office_automation:dashboard",
                    icon="icon-chart",
                    permission="office_automation.dashboard"
                ),
                MenuItem(
                    name="Inbox",
                    url_name="office_automation:inbox_incoming",
                    icon="icon-mail",
                    permission="office_automation.inbox.incoming",
                    children=[
                        MenuItem(
                            name="Incoming Letters",
                            url_name="office_automation:inbox_incoming",
                            icon="icon-mail",
                            permission="office_automation.inbox.incoming"
                        ),
                        MenuItem(
                            name="Write Letter",
                            url_name="office_automation:inbox_write",
                            icon="icon-pen",
                            permission="office_automation.inbox.write"
                        ),
                        MenuItem(
                            name="Fill Form",
                            url_name="office_automation:inbox_fill_form",
                            icon="icon-edit",
                            permission="office_automation.inbox.fill_form"
                        ),
                    ]
                ),
                MenuItem(
                    name="Processes",
                    url_name="office_automation:processes_engine",
                    icon="icon-gear",
                    permission="office_automation.processes.engine",
                    children=[
                        MenuItem(
                            name="Process Engine",
                            url_name="office_automation:processes_engine",
                            icon="icon-gear",
                            permission="office_automation.processes.engine"
                        ),
                        MenuItem(
                            name="Process-Form Connection",
                            url_name="office_automation:processes_form_connection",
                            icon="icon-link",
                            permission="office_automation.processes.form_connection"
                        ),
                    ]
                ),
                MenuItem(
                    name="Forms",
                    url_name="office_automation:forms_builder",
                    icon="icon-edit",
                    permission="office_automation.forms.builder",
                    children=[
                        MenuItem(
                            name="Form Builder",
                            url_name="office_automation:forms_builder",
                            icon="icon-edit",
                            permission="office_automation.forms.builder"
                        ),
                    ]
                ),
            ]
        ),
        
        # Transportation Section
        MenuSection(
            name="Transportation",
            icon="icon-truck",
            permission="transportation.dashboard",
            items=[
                MenuItem(
                    name="Dashboard",
                    url_name="transportation:dashboard",
                    icon="icon-chart",
                    permission="transportation.dashboard"
                ),
            ]
        ),
        
        # Procurement Section
        MenuSection(
            name="Procurement",
            icon="icon-shopping",
            permission="procurement.dashboard",
            items=[
                MenuItem(
                    name="Dashboard",
                    url_name="procurement:dashboard",
                    icon="icon-chart",
                    permission="procurement.dashboard"
                ),
                MenuItem(
                    name="Purchase",
                    url_name="procurement:purchase_orders",
                    icon="icon-cart",
                    permission="procurement.orders.list",
                    requires_superuser=True,
                    children=[
                        MenuItem(
                            name="Purchase Orders",
                            url_name="procurement:purchase_orders",
                            icon="icon-shopping-cart",
                            permission="procurement.orders.list",
                            requires_superuser=True
                        ),
                        MenuItem(
                            name="Purchase Invoices",
                            url_name="procurement:purchase_invoices",
                            icon="icon-file-text",
                            permission="procurement.invoices.purchase",
                            requires_superuser=True
                        ),
                    ]
                ),
                MenuItem(
                    name="Services",
                    url_name="procurement:service_requests",
                    icon="icon-service",
                    permission="procurement.services.request",
                    requires_superuser=True,
                    children=[
                        MenuItem(
                            name="Service Requests",
                            url_name="procurement:service_requests",
                            icon="icon-file",
                            permission="procurement.services.request",
                            requires_superuser=True
                        ),
                        MenuItem(
                            name="Service Invoices",
                            url_name="procurement:service_invoices",
                            icon="icon-file-text",
                            permission="procurement.invoices.service",
                            requires_superuser=True
                        ),
                    ]
                ),
                MenuItem(
                    name="Buyers",
                    url_name="procurement:buyers",
                    icon="icon-user",
                    permission="procurement.buyers",
                    children=[
                        MenuItem(
                            name="Buyers List",
                            url_name="procurement:buyers",
                            icon="icon-user",
                            permission="procurement.buyers"
                        ),
                        MenuItem(
                            name="Create Buyer",
                            url_name="procurement:buyer_create",
                            icon="icon-plus",
                            permission="procurement.buyers"
                        ),
                        MenuItem(
                            name="Buyer Assignment",
                            url_name="procurement:buyer_assignment",
                            icon="icon-check",
                            permission="procurement.buyers"
                        ),
                    ]
                ),
            ]
        ),
    ]
    
    return menu_sections

