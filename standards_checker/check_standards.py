#!/usr/bin/env python3
"""
Standards Checker - ابزار چک کردن رعایت استانداردهای پروژه

این اسکریپت فایل‌های پروژه را تحلیل می‌کند و بررسی می‌کند که آیا
استانداردهای تعریف شده در DEVELOPMENT_GUIDE.md رعایت شده است یا خیر.

استفاده:
    python check_standards.py                    # چک کردن همه
    python check_standards.py --module inventory # چک کردن یک ماژول خاص
    python check_standards.py --fix              # Auto-fix مشکلات قابل تعمیر
    python check_standards.py --json             # خروجی JSON
    python check_standards.py --verbose          # خروجی کامل
"""

import os
import re
import ast
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


# رنگ‌ها برای خروجی ترمینال
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


class Severity(Enum):
    """سطح شدت مشکل"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Issue:
    """یک مشکل/تخلف از استانداردها"""
    file_path: str
    line_number: int
    severity: Severity
    category: str
    message: str
    suggestion: str = ""
    auto_fixable: bool = False
    
    def __str__(self):
        """نمایش رنگی مشکل"""
        color_map = {
            Severity.INFO: Colors.OKBLUE,
            Severity.WARNING: Colors.WARNING,
            Severity.ERROR: Colors.FAIL,
            Severity.CRITICAL: Colors.FAIL + Colors.BOLD,
        }
        color = color_map.get(self.severity, "")
        
        output = f"{color}[{self.severity.value.upper()}]{Colors.ENDC} "
        output += f"{Colors.BOLD}{self.file_path}:{self.line_number}{Colors.ENDC}\n"
        output += f"  Category: {self.category}\n"
        output += f"  {self.message}\n"
        
        if self.suggestion:
            output += f"  {Colors.OKCYAN}💡 Suggestion: {self.suggestion}{Colors.ENDC}\n"
        
        if self.auto_fixable:
            output += f"  {Colors.OKGREEN}🔧 Auto-fixable{Colors.ENDC}\n"
        
        return output


@dataclass
class CheckResult:
    """نتیجه چک کردن"""
    issues: List[Issue] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)
    
    def add_issue(self, issue: Issue):
        """اضافه کردن یک مشکل"""
        self.issues.append(issue)
    
    def get_summary(self) -> Dict:
        """خلاصه نتایج"""
        return {
            'total_issues': len(self.issues),
            'critical': sum(1 for i in self.issues if i.severity == Severity.CRITICAL),
            'errors': sum(1 for i in self.issues if i.severity == Severity.ERROR),
            'warnings': sum(1 for i in self.issues if i.severity == Severity.WARNING),
            'info': sum(1 for i in self.issues if i.severity == Severity.INFO),
            'auto_fixable': sum(1 for i in self.issues if i.auto_fixable),
        }


class BaseClassChecker:
    """چک کردن استفاده از Base Classes"""
    
    # Base Classes که باید استفاده شوند
    REQUIRED_BASE_CLASSES = {
        'ListView': 'BaseListView',
        'CreateView': 'BaseCreateView',
        'UpdateView': 'BaseUpdateView',
        'DeleteView': 'BaseDeleteView',
        'DetailView': 'BaseDetailView',
        'FormView': 'BaseFormView',
    }
    
    # ماژول‌هایی که از چک معاف هستند
    EXEMPT_MODULES = {'shared', 'migrations', 'tests'}
    
    def check_file(self, file_path: str) -> List[Issue]:
        """چک کردن یک فایل Python"""
        issues = []
        
        # فایل‌های معاف از چک
        if any(exempt in file_path for exempt in self.EXEMPT_MODULES):
            return issues
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # بررسی base classes
                    for base in node.bases:
                        base_name = self._get_base_name(base)
                        
                        if base_name in self.REQUIRED_BASE_CLASSES:
                            # استفاده از Django generic view به جای Base Class
                            required = self.REQUIRED_BASE_CLASSES[base_name]
                            issues.append(Issue(
                                file_path=file_path,
                                line_number=node.lineno,
                                severity=Severity.ERROR,
                                category="Base Classes",
                                message=f"Class '{node.name}' uses '{base_name}' instead of '{required}'",
                                suggestion=f"Replace 'from django.views.generic import {base_name}' "
                                          f"with 'from shared.views.base import {required}'",
                                auto_fixable=False
                            ))
        
        except Exception as e:
            issues.append(Issue(
                file_path=file_path,
                line_number=0,
                severity=Severity.WARNING,
                category="Parsing",
                message=f"Failed to parse file: {str(e)}"
            ))
        
        return issues
    
    def _get_base_name(self, base) -> str:
        """دریافت نام base class"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return ""


class TemplateChecker:
    """چک کردن Templates"""
    
    GENERIC_TEMPLATES = [
        'generic_list.html',
        'generic_form.html',
        'generic_detail.html',
        'generic_confirm_delete.html'
    ]
    
    def check_file(self, file_path: str) -> List[Issue]:
        """چک کردن یک فایل template"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # چک کردن inline styles
            issues.extend(self._check_inline_styles(file_path, lines))
            
            # چک کردن inline JavaScript
            issues.extend(self._check_inline_javascript(file_path, lines))
            
            # چک کردن استفاده از generic templates
            issues.extend(self._check_generic_templates(file_path, content))
            
            # چک کردن استفاده از template tags
            issues.extend(self._check_template_tags(file_path, content))
        
        except Exception as e:
            issues.append(Issue(
                file_path=file_path,
                line_number=0,
                severity=Severity.WARNING,
                category="Parsing",
                message=f"Failed to read template: {str(e)}"
            ))
        
        return issues
    
    def _check_inline_styles(self, file_path: str, lines: List[str]) -> List[Issue]:
        """چک کردن inline styles"""
        issues = []
        
        # Pattern برای inline style
        style_pattern = re.compile(r'style\s*=\s*["\']')
        
        for i, line in enumerate(lines, 1):
            if style_pattern.search(line):
                # استثنا برای برخی موارد خاص
                if 'display: none' in line or 'visibility: hidden' in line:
                    continue
                
                issues.append(Issue(
                    file_path=file_path,
                    line_number=i,
                    severity=Severity.ERROR,
                    category="Template - CSS",
                    message="Inline style detected",
                    suggestion="Move styles to shared.css",
                    auto_fixable=False
                ))
        
        return issues
    
    def _check_inline_javascript(self, file_path: str, lines: List[str]) -> List[Issue]:
        """چک کردن inline JavaScript"""
        issues = []
        
        # Pattern برای inline event handlers
        inline_js_patterns = [
            r'onclick\s*=',
            r'onchange\s*=',
            r'onsubmit\s*=',
            r'onload\s*=',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in inline_js_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=i,
                        severity=Severity.ERROR,
                        category="Template - JavaScript",
                        message="Inline event handler detected",
                        suggestion="Use addEventListener in separate JS file",
                        auto_fixable=False
                    ))
                    break
        
        return issues
    
    def _check_generic_templates(self, file_path: str, content: str) -> List[Issue]:
        """چک کردن استفاده از generic templates"""
        issues = []
        
        # فقط برای فایل‌های اصلی (نه partials)
        if 'partials' in file_path or 'generic' in file_path:
            return issues
        
        # چک کردن extends
        extends_match = re.search(r'{%\s*extends\s+["\'](.+?)["\']\s*%}', content)
        
        if extends_match:
            extended_template = extends_match.group(1)
            
            # آیا از generic template استفاده کرده؟
            if not any(generic in extended_template for generic in self.GENERIC_TEMPLATES):
                # تشخیص نوع template
                if '_list.html' in file_path or 'list.html' in file_path:
                    suggestion = "Consider extending 'shared/generic/generic_list.html'"
                elif '_form.html' in file_path or 'form.html' in file_path:
                    suggestion = "Consider extending 'shared/generic/generic_form.html'"
                elif '_detail.html' in file_path or 'detail.html' in file_path:
                    suggestion = "Consider extending 'shared/generic/generic_detail.html'"
                else:
                    suggestion = "Consider using a generic template if applicable"
                
                issues.append(Issue(
                    file_path=file_path,
                    line_number=1,
                    severity=Severity.WARNING,
                    category="Template - Structure",
                    message=f"Not using generic template (extends '{extended_template}')",
                    suggestion=suggestion,
                    auto_fixable=False
                ))
        
        return issues
    
    def _check_template_tags(self, file_path: str, content: str) -> List[Issue]:
        """چک کردن استفاده از template tags"""
        issues = []
        
        # اگر از static استفاده می‌کند، باید load static داشته باشد
        if "{% static" in content and "{% load static %}" not in content:
            issues.append(Issue(
                file_path=file_path,
                line_number=1,
                severity=Severity.ERROR,
                category="Template - Tags",
                message="Using {% static %} without {% load static %}",
                suggestion="Add {% load static %} at the top of template",
                auto_fixable=True
            ))
        
        return issues


class DocstringChecker:
    """چک کردن docstrings"""
    
    def check_file(self, file_path: str) -> List[Issue]:
        """چک کردن docstrings در یک فایل"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                # چک کردن functions
                if isinstance(node, ast.FunctionDef):
                    if not self._has_docstring(node):
                        # استثنا برای متدهای خاص
                        if node.name.startswith('_') or node.name in ['setUp', 'tearDown']:
                            continue
                        
                        issues.append(Issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=Severity.WARNING,
                            category="Documentation",
                            message=f"Function '{node.name}' missing docstring",
                            suggestion="Add docstring explaining function purpose, args, and returns",
                            auto_fixable=False
                        ))
                
                # چک کردن classes
                elif isinstance(node, ast.ClassDef):
                    if not self._has_docstring(node):
                        issues.append(Issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=Severity.WARNING,
                            category="Documentation",
                            message=f"Class '{node.name}' missing docstring",
                            suggestion="Add docstring explaining class purpose",
                            auto_fixable=False
                        ))
        
        except Exception as e:
            pass  # Ignore parsing errors
        
        return issues
    
    def _has_docstring(self, node) -> bool:
        """بررسی وجود docstring"""
        return (
            ast.get_docstring(node) is not None and 
            len(ast.get_docstring(node).strip()) > 0
        )


class SecurityChecker:
    """چک کردن مشکلات امنیتی"""
    
    DANGEROUS_PATTERNS = {
        'sql_injection': [
            (r'cursor\.execute\([^)]*%s', 'Potential SQL injection - use parameterized queries'),
            (r'\.raw\([^)]*%', 'Potential SQL injection in raw query'),
        ],
        'xss': [
            (r'\|safe(?!\})', 'Using |safe filter - ensure content is trusted'),
            (r'mark_safe\(', 'Using mark_safe - ensure content is sanitized'),
        ],
        'secrets': [
            (r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', 'Hardcoded SECRET_KEY - use environment variables'),
            (r'PASSWORD\s*=\s*["\'][^"\']+["\']', 'Hardcoded password - use environment variables'),
            (r'API_KEY\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key - use environment variables'),
        ],
    }
    
    def check_file(self, file_path: str) -> List[Issue]:
        """چک کردن امنیت یک فایل"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                for category, patterns in self.DANGEROUS_PATTERNS.items():
                    for pattern, message in patterns:
                        if re.search(pattern, line):
                            issues.append(Issue(
                                file_path=file_path,
                                line_number=i,
                                severity=Severity.CRITICAL,
                                category=f"Security - {category}",
                                message=message,
                                suggestion="Review security best practices in DEVELOPMENT_GUIDE.md",
                                auto_fixable=False
                            ))
        
        except Exception:
            pass
        
        return issues


class NamingChecker:
    """چک کردن naming conventions"""
    
    def check_file(self, file_path: str) -> List[Issue]:
        """چک کردن naming conventions"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                # Classes باید PascalCase باشند
                if isinstance(node, ast.ClassDef):
                    if not self._is_pascal_case(node.name):
                        issues.append(Issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=Severity.WARNING,
                            category="Naming - Class",
                            message=f"Class '{node.name}' should use PascalCase",
                            suggestion=f"Rename to {self._to_pascal_case(node.name)}",
                            auto_fixable=False
                        ))
                
                # Functions باید snake_case باشند
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_') and not self._is_snake_case(node.name):
                        issues.append(Issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=Severity.WARNING,
                            category="Naming - Function",
                            message=f"Function '{node.name}' should use snake_case",
                            suggestion=f"Rename to {self._to_snake_case(node.name)}",
                            auto_fixable=False
                        ))
        
        except Exception:
            pass
        
        return issues
    
    def _is_pascal_case(self, name: str) -> bool:
        """بررسی PascalCase"""
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
    
    def _is_snake_case(self, name: str) -> bool:
        """بررسی snake_case"""
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name))
    
    def _to_pascal_case(self, name: str) -> str:
        """تبدیل به PascalCase"""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _to_snake_case(self, name: str) -> str:
        """تبدیل به snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class StandardsChecker:
    """Checker اصلی"""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize checker
        
        Args:
            base_dir: مسیر پایه پروژه
        """
        self.base_dir = Path(base_dir or os.getcwd())
        self.result = CheckResult()
        
        # Checkers
        self.base_class_checker = BaseClassChecker()
        self.template_checker = TemplateChecker()
        self.docstring_checker = DocstringChecker()
        self.security_checker = SecurityChecker()
        self.naming_checker = NamingChecker()
    
    def check_all(self, module: str = None, verbose: bool = False):
        """
        چک کردن همه فایل‌ها
        
        Args:
            module: نام ماژول برای چک کردن (None = همه)
            verbose: نمایش جزئیات
        """
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("=" * 70)
        print("          ERP Standards Checker")
        print("=" * 70)
        print(f"{Colors.ENDC}\n")
        
        # تعیین مسیر جستجو
        if module:
            search_path = self.base_dir / module
            if not search_path.exists():
                print(f"{Colors.FAIL}Module '{module}' not found{Colors.ENDC}")
                return
        else:
            search_path = self.base_dir
        
        # جستجوی فایل‌ها
        python_files = list(search_path.rglob('*.py'))
        template_files = list(search_path.rglob('*.html'))
        
        total_files = len(python_files) + len(template_files)
        
        print(f"📁 Scanning {total_files} files...")
        print(f"   - Python files: {len(python_files)}")
        print(f"   - Template files: {len(template_files)}")
        print()
        
        # چک کردن Python files
        print(f"{Colors.OKBLUE}Checking Python files...{Colors.ENDC}")
        for i, file_path in enumerate(python_files, 1):
            if verbose:
                print(f"  [{i}/{len(python_files)}] {file_path.relative_to(self.base_dir)}")
            
            file_str = str(file_path)
            
            # چک کردن Base Classes
            self.result.issues.extend(
                self.base_class_checker.check_file(file_str)
            )
            
            # چک کردن Docstrings
            self.result.issues.extend(
                self.docstring_checker.check_file(file_str)
            )
            
            # چک کردن Security
            self.result.issues.extend(
                self.security_checker.check_file(file_str)
            )
            
            # چک کردن Naming
            self.result.issues.extend(
                self.naming_checker.check_file(file_str)
            )
        
        # چک کردن Template files
        print(f"\n{Colors.OKBLUE}Checking Template files...{Colors.ENDC}")
        for i, file_path in enumerate(template_files, 1):
            if verbose:
                print(f"  [{i}/{len(template_files)}] {file_path.relative_to(self.base_dir)}")
            
            file_str = str(file_path)
            
            # چک کردن Templates
            self.result.issues.extend(
                self.template_checker.check_file(file_str)
            )
        
        # نمایش نتایج
        self._display_results()
    
    def _display_results(self):
        """نمایش نتایج"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}=" * 70)
        print("                         Results")
        print("=" * 70 + f"{Colors.ENDC}\n")
        
        summary = self.result.get_summary()
        
        # خلاصه
        print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
        print(f"  Total Issues: {summary['total_issues']}")
        
        if summary['critical'] > 0:
            print(f"  {Colors.FAIL}Critical: {summary['critical']}{Colors.ENDC}")
        if summary['errors'] > 0:
            print(f"  {Colors.FAIL}Errors: {summary['errors']}{Colors.ENDC}")
        if summary['warnings'] > 0:
            print(f"  {Colors.WARNING}Warnings: {summary['warnings']}{Colors.ENDC}")
        if summary['info'] > 0:
            print(f"  {Colors.OKBLUE}Info: {summary['info']}{Colors.ENDC}")
        
        if summary['auto_fixable'] > 0:
            print(f"  {Colors.OKGREEN}Auto-fixable: {summary['auto_fixable']}{Colors.ENDC}")
        
        # نمایش issues
        if self.result.issues:
            print(f"\n{Colors.BOLD}Issues:{Colors.ENDC}\n")
            
            # گروه‌بندی بر اساس category
            categories = {}
            for issue in self.result.issues:
                if issue.category not in categories:
                    categories[issue.category] = []
                categories[issue.category].append(issue)
            
            for category, issues in sorted(categories.items()):
                print(f"\n{Colors.BOLD}{Colors.UNDERLINE}{category} ({len(issues)} issues){Colors.ENDC}")
                for issue in issues[:10]:  # نمایش 10 تای اول
                    print(issue)
                
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more issues\n")
        else:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ No issues found! All standards met.{Colors.ENDC}\n")
        
        # نتیجه نهایی
        if summary['critical'] > 0 or summary['errors'] > 0:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ FAILED - Fix errors before committing{Colors.ENDC}\n")
            return False
        elif summary['warnings'] > 0:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  WARNINGS - Consider fixing before committing{Colors.ENDC}\n")
            return True
        else:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ PASSED - All checks passed{Colors.ENDC}\n")
            return True
    
    def export_json(self, output_file: str = 'standards_report.json'):
        """خروجی JSON برای CI/CD"""
        report = {
            'summary': self.result.get_summary(),
            'issues': [
                {
                    'file': issue.file_path,
                    'line': issue.line_number,
                    'severity': issue.severity.value,
                    'category': issue.category,
                    'message': issue.message,
                    'suggestion': issue.suggestion,
                    'auto_fixable': issue.auto_fixable,
                }
                for issue in self.result.issues
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.OKGREEN}Report exported to {output_file}{Colors.ENDC}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Check project files against development standards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Check all files
  %(prog)s --module inventory       # Check inventory module
  %(prog)s --verbose                # Verbose output
  %(prog)s --json report.json       # Export JSON report
  %(prog)s --fix                    # Auto-fix issues
        """
    )
    
    parser.add_argument(
        '--module',
        help='Check specific module only',
        type=str
    )
    
    parser.add_argument(
        '--verbose', '-v',
        help='Verbose output',
        action='store_true'
    )
    
    parser.add_argument(
        '--json',
        help='Export JSON report',
        type=str,
        metavar='FILE'
    )
    
    parser.add_argument(
        '--fix',
        help='Auto-fix issues where possible',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # ایجاد checker
    checker = StandardsChecker()
    
    # چک کردن
    checker.check_all(module=args.module, verbose=args.verbose)
    
    # خروجی JSON
    if args.json:
        checker.export_json(args.json)
    
    # Auto-fix
    if args.fix:
        print(f"\n{Colors.WARNING}Auto-fix not yet implemented{Colors.ENDC}")


if __name__ == '__main__':
    main()

