#!/usr/bin/env python3
"""
Compare Standards Reports
مقایسه دو گزارش استانداردها برای tracking پیشرفت

استفاده:
    python compare_reports.py report1.json report2.json
"""

import json
import sys
from pathlib import Path


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_report(file_path: str) -> dict:
    """بارگذاری گزارش JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: File '{file_path}' not found{Colors.ENDC}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}Error: Invalid JSON in '{file_path}'{Colors.ENDC}")
        sys.exit(1)


def compare_summaries(report1: dict, report2: dict):
    """مقایسه خلاصه دو گزارش"""
    summary1 = report1.get('summary', {})
    summary2 = report2.get('summary', {})
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}Summary Comparison{Colors.ENDC}\n")
    
    print(f"{'Metric':<20} {'Report 1':>12} {'Report 2':>12} {'Change':>12}")
    print("=" * 60)
    
    metrics = ['total_issues', 'critical', 'errors', 'warnings', 'info', 'auto_fixable']
    
    for metric in metrics:
        val1 = summary1.get(metric, 0)
        val2 = summary2.get(metric, 0)
        change = val2 - val1
        
        # رنگ بر اساس تغییر
        if change > 0:
            color = Colors.FAIL
            change_str = f"+{change}"
        elif change < 0:
            color = Colors.OKGREEN
            change_str = str(change)
        else:
            color = Colors.OKCYAN
            change_str = "0"
        
        # استثنا برای auto_fixable (بیشتر شدن خوب است)
        if metric == 'auto_fixable' and change > 0:
            color = Colors.OKGREEN
        
        print(f"{metric.replace('_', ' ').title():<20} {val1:>12} {val2:>12} "
              f"{color}{change_str:>12}{Colors.ENDC}")
    
    # نتیجه کلی
    total_change = summary2.get('total_issues', 0) - summary1.get('total_issues', 0)
    
    print("\n" + "=" * 60)
    
    if total_change < 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Improvement: "
              f"{abs(total_change)} fewer issues!{Colors.ENDC}\n")
    elif total_change > 0:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Regression: "
              f"{total_change} more issues{Colors.ENDC}\n")
    else:
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}➡️  No change in total issues{Colors.ENDC}\n")


def compare_categories(report1: dict, report2: dict):
    """مقایسه issues بر اساس category"""
    issues1 = report1.get('issues', [])
    issues2 = report2.get('issues', [])
    
    # گروه‌بندی بر اساس category
    def group_by_category(issues):
        categories = {}
        for issue in issues:
            cat = issue.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    cats1 = group_by_category(issues1)
    cats2 = group_by_category(issues2)
    
    # تمام categories
    all_categories = set(cats1.keys()) | set(cats2.keys())
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}Category Comparison{Colors.ENDC}\n")
    
    print(f"{'Category':<30} {'Report 1':>12} {'Report 2':>12} {'Change':>12}")
    print("=" * 70)
    
    for category in sorted(all_categories):
        val1 = cats1.get(category, 0)
        val2 = cats2.get(category, 0)
        change = val2 - val1
        
        if change > 0:
            color = Colors.FAIL
            change_str = f"+{change}"
        elif change < 0:
            color = Colors.OKGREEN
            change_str = str(change)
        else:
            color = Colors.OKCYAN
            change_str = "0"
        
        print(f"{category:<30} {val1:>12} {val2:>12} "
              f"{color}{change_str:>12}{Colors.ENDC}")


def show_new_issues(report1: dict, report2: dict):
    """نمایش issues جدید"""
    issues1 = report1.get('issues', [])
    issues2 = report2.get('issues', [])
    
    # ایجاد set از issues برای مقایسه
    def issue_key(issue):
        return (issue.get('file'), issue.get('line'), issue.get('category'))
    
    keys1 = {issue_key(i) for i in issues1}
    keys2 = {issue_key(i) for i in issues2}
    
    # Issues جدید
    new_keys = keys2 - keys1
    
    if new_keys:
        new_issues = [i for i in issues2 if issue_key(i) in new_keys]
        
        print(f"\n{Colors.BOLD}{Colors.FAIL}New Issues ({len(new_issues)}){Colors.ENDC}\n")
        
        for issue in new_issues[:10]:  # نمایش 10 تای اول
            print(f"  {Colors.FAIL}[{issue.get('severity', '').upper()}]{Colors.ENDC} "
                  f"{issue.get('file')}:{issue.get('line')}")
            print(f"    Category: {issue.get('category')}")
            print(f"    {issue.get('message')}\n")
        
        if len(new_issues) > 10:
            print(f"  ... and {len(new_issues) - 10} more\n")


def show_fixed_issues(report1: dict, report2: dict):
    """نمایش issues رفع شده"""
    issues1 = report1.get('issues', [])
    issues2 = report2.get('issues', [])
    
    def issue_key(issue):
        return (issue.get('file'), issue.get('line'), issue.get('category'))
    
    keys1 = {issue_key(i) for i in issues1}
    keys2 = {issue_key(i) for i in issues2}
    
    # Issues رفع شده
    fixed_keys = keys1 - keys2
    
    if fixed_keys:
        fixed_issues = [i for i in issues1 if issue_key(i) in fixed_keys]
        
        print(f"\n{Colors.BOLD}{Colors.OKGREEN}Fixed Issues ({len(fixed_issues)}){Colors.ENDC}\n")
        
        for issue in fixed_issues[:10]:  # نمایش 10 تای اول
            print(f"  {Colors.OKGREEN}[FIXED]{Colors.ENDC} "
                  f"{issue.get('file')}:{issue.get('line')}")
            print(f"    Category: {issue.get('category')}")
            print(f"    {issue.get('message')}\n")
        
        if len(fixed_issues) > 10:
            print(f"  ... and {len(fixed_issues) - 10} more\n")


def main():
    """Main entry point"""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <report1.json> <report2.json>")
        sys.exit(1)
    
    report1_path = sys.argv[1]
    report2_path = sys.argv[2]
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("           Standards Reports Comparison")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    print(f"\n📊 Report 1: {report1_path}")
    print(f"📊 Report 2: {report2_path}\n")
    
    # بارگذاری گزارش‌ها
    report1 = load_report(report1_path)
    report2 = load_report(report2_path)
    
    # مقایسه
    compare_summaries(report1, report2)
    compare_categories(report1, report2)
    show_fixed_issues(report1, report2)
    show_new_issues(report1, report2)
    
    print(f"\n{Colors.BOLD}━{'━' * 68}━{Colors.ENDC}\n")


if __name__ == '__main__':
    main()

