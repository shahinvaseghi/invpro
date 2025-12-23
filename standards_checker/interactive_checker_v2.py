#!/usr/bin/env python3
"""
Interactive Standards Checker v2
نسخه بهبود یافته با curses برای Terminal UI

استفاده:
    python interactive_checker_v2.py
"""

import os
import sys
import curses
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

# رنگ‌ها در curses
COLOR_HEADER = 1
COLOR_FOLDER = 2
COLOR_FILE = 3
COLOR_CURSOR = 4
COLOR_ERROR = 5
COLOR_WARNING = 6
COLOR_SUCCESS = 7


class FileNode:
    """یک node در file tree"""
    
    def __init__(self, path: Path, parent: Optional['FileNode'] = None):
        self.path = path
        self.parent = parent
        self.children: List['FileNode'] = []
        self.is_expanded = False
        
        if self.is_dir:
            self._load_children()
    
    @property
    def name(self) -> str:
        return self.path.name
    
    @property
    def is_dir(self) -> bool:
        return self.path.is_dir()
    
    @property
    def icon(self) -> str:
        if self.is_dir:
            return "[+]" if not self.is_expanded else "[-]"
        
        ext = self.path.suffix.lower()
        if ext == '.py':
            return " .py"
        elif ext in ['.html', '.htm']:
            return ".html"
        elif ext == '.css':
            return " .css"
        elif ext == '.js':
            return "  .js"
        else:
            return " file"
    
    def _load_children(self):
        if not self.is_dir:
            return
        
        ignore_patterns = {
            '__pycache__', '.git', '.venv', 'venv', 'env',
            'node_modules', '.pytest_cache', '.mypy_cache',
            'staticfiles', 'media', '.idea', '.vscode'
        }
        
        try:
            for item in sorted(self.path.iterdir(), key=lambda x: (x.is_file(), x.name)):
                if item.name.startswith('.') and item.name not in {'.env', '.gitignore'}:
                    continue
                if item.name in ignore_patterns:
                    continue
                
                child = FileNode(item, parent=self)
                self.children.append(child)
        except PermissionError:
            pass
    
    def toggle_expand(self):
        if self.is_dir:
            self.is_expanded = not self.is_expanded
    
    def get_display_list(self, level: int = 0) -> List[Tuple['FileNode', int]]:
        result = [(self, level)]
        
        if self.is_expanded and self.is_dir:
            for child in self.children:
                result.extend(child.get_display_list(level + 1))
        
        return result


class FileBrowser:
    """مرورگر فایل با curses"""
    
    def __init__(self, root_path: Path):
        self.root = FileNode(root_path)
        self.root.is_expanded = True
        self.display_list: List[Tuple[FileNode, int]] = []
        self.cursor_index = 0
        self.scroll_offset = 0
        self.selected_file: Optional[Path] = None
        self._update_display_list()
    
    def _update_display_list(self):
        self.display_list = self.root.get_display_list()
    
    @property
    def current_node(self) -> FileNode:
        if 0 <= self.cursor_index < len(self.display_list):
            return self.display_list[self.cursor_index][0]
        return self.root
    
    def move_up(self):
        if self.cursor_index > 0:
            self.cursor_index -= 1
    
    def move_down(self):
        if self.cursor_index < len(self.display_list) - 1:
            self.cursor_index += 1
    
    def select_current(self) -> Optional[Path]:
        node = self.current_node
        
        if node.is_dir:
            node.toggle_expand()
            self._update_display_list()
            return None
        else:
            self.selected_file = node.path
            return node.path
    
    def go_back(self) -> bool:
        node = self.current_node
        
        if node.is_dir and node.is_expanded:
            node.toggle_expand()
            self._update_display_list()
            return True
        
        if node.parent and node.parent != self.root:
            for i, (n, _) in enumerate(self.display_list):
                if n == node.parent:
                    self.cursor_index = i
                    break
            return True
        
        return False
    
    def render(self, stdscr, max_y, max_x):
        """رندر کردن file browser"""
        stdscr.clear()
        
        # Header
        header = "File Browser - Select a File"
        stdscr.addstr(0, 0, "=" * max_x, curses.color_pair(COLOR_HEADER))
        stdscr.addstr(1, (max_x - len(header)) // 2, header, 
                     curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
        stdscr.addstr(2, 0, "=" * max_x, curses.color_pair(COLOR_HEADER))
        
        # File list
        display_height = max_y - 6
        
        # محاسبه scroll
        if self.cursor_index < self.scroll_offset:
            self.scroll_offset = self.cursor_index
        elif self.cursor_index >= self.scroll_offset + display_height:
            self.scroll_offset = self.cursor_index - display_height + 1
        
        # نمایش فایل‌ها
        for i in range(display_height):
            list_idx = self.scroll_offset + i
            if list_idx >= len(self.display_list):
                break
            
            node, level = self.display_list[list_idx]
            
            y = 4 + i
            indent = "  " * level
            
            # نام
            display_name = f"{indent}{node.icon} {node.name}"
            if len(display_name) > max_x - 5:
                display_name = display_name[:max_x - 8] + "..."
            
            # رنگ و cursor
            if list_idx == self.cursor_index:
                stdscr.addstr(y, 0, "> ", curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
                stdscr.addstr(y, 2, display_name, 
                            curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
            else:
                stdscr.addstr(y, 2, display_name, 
                            curses.color_pair(COLOR_FOLDER if node.is_dir else COLOR_FILE))
        
        # Footer
        footer_y = max_y - 2
        stdscr.addstr(footer_y, 0, "-" * max_x, curses.color_pair(COLOR_HEADER))
        help_text = "[UP/DOWN] Navigate  [ENTER] Select  [ESC] Back  [Q] Quit"
        stdscr.addstr(footer_y + 1, (max_x - len(help_text)) // 2, help_text)
        
        stdscr.refresh()


class InteractiveChecker:
    """Checker تعاملی اصلی"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checker_root = project_root / "standards_checker"
        
        # Import checker اصلی
        sys.path.insert(0, str(self.checker_root))
        try:
            from check_standards import (
                BaseClassChecker, TemplateChecker, DocstringChecker,
                SecurityChecker, NamingChecker
            )
            self.base_class_checker = BaseClassChecker()
            self.template_checker = TemplateChecker()
            self.docstring_checker = DocstringChecker()
            self.security_checker = SecurityChecker()
            self.naming_checker = NamingChecker()
        except ImportError as e:
            print(f"Error importing checker: {e}")
            sys.exit(1)
        
        # مسیر فولدر reports
        self.reports_dir = self.checker_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def save_report(self, check_type: str, target_name: str, issues: List, total_files: int = 1):
        """
        ذخیره گزارش در فایل
        
        Args:
            check_type: نوع چک ('manual', 'module', 'all')
            target_name: نام فایل/ماژول/پروژه
            issues: لیست issues
            total_files: تعداد فایل‌های چک شده
        """
        # ساخت نام فایل با timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = target_name.replace('/', '_').replace('\\', '_')
        filename = f"{check_type}_{safe_name}_{timestamp}.txt"
        report_path = self.reports_dir / filename
        
        # گروه‌بندی issues
        by_severity = defaultdict(list)
        by_file = defaultdict(list)
        
        for issue in issues:
            by_severity[issue.severity.value].append(issue)
            file_path = getattr(issue, 'file_path', 'Unknown')
            by_file[file_path].append(issue)
        
        # نوشتن گزارش
        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write(f"STANDARDS CHECKER REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # اطلاعات کلی
            f.write(f"Check Type:     {check_type.upper()}\n")
            f.write(f"Target:         {target_name}\n")
            f.write(f"Date/Time:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Files:    {total_files}\n")
            f.write(f"Files with Issues: {len(by_file)}\n")
            f.write(f"Total Issues:   {len(issues)}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # خلاصه بر اساس severity
            f.write("SUMMARY BY SEVERITY\n")
            f.write("-" * 80 + "\n")
            if 'critical' in by_severity:
                f.write(f"Critical: {len(by_severity['critical'])}\n")
            if 'error' in by_severity:
                f.write(f"Errors:   {len(by_severity['error'])}\n")
            if 'warning' in by_severity:
                f.write(f"Warnings: {len(by_severity['warning'])}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # نمایش issues بر اساس فایل
            if issues:
                f.write("DETAILED ISSUES BY FILE\n")
                f.write("=" * 80 + "\n\n")
                
                for file_path in sorted(by_file.keys()):
                    file_issues = by_file[file_path]
                    
                    f.write(f"File: {file_path}\n")
                    f.write(f"Issues: {len(file_issues)}\n")
                    f.write("-" * 80 + "\n")
                    
                    # گروه‌بندی issues این فایل بر اساس severity
                    file_by_severity = defaultdict(list)
                    for issue in file_issues:
                        file_by_severity[issue.severity.value].append(issue)
                    
                    # نمایش بر اساس اولویت
                    for severity in ['critical', 'error', 'warning']:
                        if severity not in file_by_severity:
                            continue
                        
                        issues_list = file_by_severity[severity]
                        f.write(f"\n[{severity.upper()}] ({len(issues_list)} issues)\n")
                        
                        for i, issue in enumerate(issues_list, 1):
                            f.write(f"  {i}. Line {issue.line_number}\n")
                            f.write(f"     {issue.message}\n")
                            
                            # کد snippet اگر وجود دارد
                            if hasattr(issue, 'code_snippet') and issue.code_snippet:
                                code_lines = issue.code_snippet.split('\n')
                                for code_line in code_lines[:3]:
                                    if code_line.strip():
                                        f.write(f"     Code: {code_line}\n")
                            
                            f.write("\n")
                    
                    f.write("\n" + "=" * 80 + "\n\n")
            else:
                f.write("✓ No issues found! All checks passed successfully.\n")
                f.write("\n" + "=" * 80 + "\n")
        
        return report_path
    
    def show_main_menu(self, stdscr):
        """نمایش منوی اصلی"""
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        
        # Header
        title = "Standards Checker - Interactive"
        subtitle = "ابزار تعاملی برای چک کردن استانداردها"
        
        stdscr.addstr(2, (max_x - len(title)) // 2, title, 
                     curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
        stdscr.addstr(3, (max_x - len(subtitle)) // 2, subtitle)
        
        # Menu
        menu_items = [
            ("1", "چک دستی (Manual Check)"),
            ("2", "چک ماژول (Module Check)"),
            ("3", "چک کامل (All Check)"),
            ("4", "گزارش هفتگی (Weekly Report)"),
            ("5", "تنظیمات (Settings)"),
            ("Q", "خروج (Exit)")
        ]
        
        y_start = 6
        for i, (key, text) in enumerate(menu_items):
            y = y_start + i * 2
            stdscr.addstr(y, max_x // 4, f"{key}. {text}")
        
        stdscr.addstr(max_y - 2, max_x // 4, "Select option: ", curses.A_BOLD)
        stdscr.refresh()
        
        # دریافت ورودی
        curses.echo()
        choice = stdscr.getstr(max_y - 2, max_x // 4 + 15, 1).decode('utf-8')
        curses.noecho()
        
        return choice.lower()
    
    def get_project_modules(self):
        """دریافت لیست ماژول‌های پروژه"""
        modules = []
        ignore_dirs = {
            'standards_checker', 'staticfiles', 'media', 
            '__pycache__', '.git', '.venv', 'venv', 'env',
            'locale', 'templates', 'static'
        }
        
        for item in self.project_root.iterdir():
            if item.is_dir() and item.name not in ignore_dirs:
                if not item.name.startswith('.'):
                    # چک کنیم که حداقل یک فایل .py داره
                    py_files = list(item.rglob('*.py'))
                    if py_files:
                        modules.append(item.name)
        
        return sorted(modules)
    
    def select_module(self, stdscr):
        """انتخاب ماژول از لیست"""
        modules = self.get_project_modules()
        
        if not modules:
            stdscr.clear()
            stdscr.addstr(5, 5, "No modules found!", curses.color_pair(COLOR_ERROR))
            stdscr.addstr(7, 5, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return None
        
        cursor_idx = 0
        
        while True:
            max_y, max_x = stdscr.getmaxyx()
            stdscr.clear()
            
            # Header
            title = "Select Module to Check"
            stdscr.addstr(1, (max_x - len(title)) // 2, title, 
                         curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
            stdscr.addstr(2, 0, "=" * max_x, curses.color_pair(COLOR_HEADER))
            
            # نمایش ماژول‌ها
            y_start = 4
            display_height = max_y - 8
            
            for i, module in enumerate(modules):
                if i >= display_height:
                    break
                
                y = y_start + i
                if i == cursor_idx:
                    stdscr.addstr(y, 2, "> ", curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
                    stdscr.addstr(y, 4, module, 
                                 curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
                else:
                    stdscr.addstr(y, 4, module)
            
            # Footer
            footer_y = max_y - 2
            stdscr.addstr(footer_y, 0, "-" * max_x)
            help_text = "[UP/DOWN] Navigate  [ENTER] Select  [ESC] Cancel"
            stdscr.addstr(footer_y + 1, (max_x - len(help_text)) // 2, help_text)
            
            stdscr.refresh()
            
            # دریافت کلید
            key = stdscr.getch()
            
            if key == curses.KEY_UP:
                cursor_idx = max(0, cursor_idx - 1)
            elif key == curses.KEY_DOWN:
                cursor_idx = min(len(modules) - 1, cursor_idx + 1)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                return modules[cursor_idx]
            elif key == 27 or key == ord('q') or key == ord('Q'):  # ESC
                return None
    
    def file_browser_loop(self, stdscr):
        """حلقه اصلی file browser"""
        browser = FileBrowser(self.project_root)
        
        while True:
            max_y, max_x = stdscr.getmaxyx()
            browser.render(stdscr, max_y, max_x)
            
            # دریافت کلید
            key = stdscr.getch()
            
            if key == curses.KEY_UP:
                browser.move_up()
            elif key == curses.KEY_DOWN:
                browser.move_down()
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                selected = browser.select_current()
                if selected:
                    return selected
            elif key == 27:  # ESC
                if not browser.go_back():
                    return None
            elif key == ord('q') or key == ord('Q'):
                return None
    
    def get_checkable_files(self, directory: Path):
        """دریافت فایل‌های قابل چک در یک دایرکتوری"""
        files = []
        
        # Python files
        for py_file in directory.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                files.append(py_file)
        
        # Template files
        for html_file in directory.rglob('*.html'):
            files.append(html_file)
        
        return sorted(files)
    
    def check_module(self, stdscr, module_name: str):
        """چک کردن تمام فایل‌های یک ماژول"""
        module_path = self.project_root / module_name
        files = self.get_checkable_files(module_path)
        
        if not files:
            stdscr.clear()
            stdscr.addstr(5, 5, f"No checkable files in {module_name}!", 
                         curses.color_pair(COLOR_WARNING))
            stdscr.addstr(7, 5, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return
        
        # نمایش صفحه در حال پردازش
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        
        title = f"Checking Module: {module_name}"
        stdscr.addstr(1, (max_x - len(title)) // 2, title, 
                     curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
        stdscr.addstr(2, 0, "=" * max_x, curses.color_pair(COLOR_HEADER))
        stdscr.addstr(4, 2, f"Total files: {len(files)}", curses.A_BOLD)
        stdscr.addstr(5, 0, "-" * max_x)
        stdscr.refresh()
        
        # چک کردن فایل‌ها
        all_issues = []
        y = 7
        
        for i, file_path in enumerate(files, 1):
            rel_path = str(file_path.relative_to(self.project_root))
            
            # نمایش پیشرفت
            if y < max_y - 5:
                progress = f"[{i}/{len(files)}] {rel_path}"
                if len(progress) > max_x - 4:
                    progress = progress[:max_x - 7] + "..."
                stdscr.addstr(y, 2, progress)
                stdscr.refresh()
                y += 1
            
            # چک فایل
            file_str = str(file_path)
            file_issues = []
            
            if file_path.suffix == '.py':
                file_issues.extend(self.base_class_checker.check_file(file_str))
                file_issues.extend(self.docstring_checker.check_file(file_str))
                file_issues.extend(self.security_checker.check_file(file_str))
                file_issues.extend(self.naming_checker.check_file(file_str))
            elif file_path.suffix in ['.html', '.htm']:
                file_issues.extend(self.template_checker.check_file(file_str))
            
            # اضافه کردن نام فایل به هر issue
            for issue in file_issues:
                issue.file_path = rel_path
                all_issues.append(issue)
        
        # نمایش خلاصه
        stdscr.addstr(y + 1, 2, f"Completed! Found {len(all_issues)} issues", 
                     curses.A_BOLD)
        stdscr.addstr(y + 2, 2, "Generating report...", curses.A_DIM)
        stdscr.refresh()
        curses.napms(500)
        
        # ذخیره گزارش در فایل
        report_path = self.save_report('module', module_name, all_issues, len(files))
        
        # نمایش نتایج
        self.display_module_results(stdscr, module_name, all_issues, len(files), max_y, max_x)
        
        # نمایش پیام ذخیره گزارش
        max_y, max_x = stdscr.getmaxyx()
        report_msg = f"Report saved: {report_path.name}"
        stdscr.addstr(max_y - 1, 2, report_msg, curses.color_pair(COLOR_SUCCESS) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(2000)  # نمایش 2 ثانیه
    
    def check_all_project(self, stdscr):
        """چک کردن کل پروژه"""
        # دریافت تمام ماژول‌ها
        modules = self.get_project_modules()
        
        if not modules:
            stdscr.clear()
            stdscr.addstr(5, 5, "No modules found!", curses.color_pair(COLOR_ERROR))
            stdscr.addstr(7, 5, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return
        
        # نمایش صفحه در حال پردازش
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        
        title = "Checking Entire Project"
        stdscr.addstr(1, (max_x - len(title)) // 2, title, 
                     curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
        stdscr.addstr(2, 0, "=" * max_x, curses.color_pair(COLOR_HEADER))
        stdscr.addstr(4, 2, f"Total modules: {len(modules)}", curses.A_BOLD)
        stdscr.addstr(5, 0, "-" * max_x)
        stdscr.refresh()
        
        # چک کردن تمام ماژول‌ها
        all_issues = []
        total_files = 0
        y = 7
        
        for i, module_name in enumerate(modules, 1):
            module_path = self.project_root / module_name
            files = self.get_checkable_files(module_path)
            total_files += len(files)
            
            # نمایش پیشرفت
            if y < max_y - 5:
                progress = f"[{i}/{len(modules)}] {module_name} ({len(files)} files)"
                stdscr.addstr(y, 2, progress, curses.color_pair(COLOR_WARNING))
                stdscr.refresh()
                y += 1
            
            # چک فایل‌ها
            for file_path in files:
                file_str = str(file_path)
                file_issues = []
                
                if file_path.suffix == '.py':
                    file_issues.extend(self.base_class_checker.check_file(file_str))
                    file_issues.extend(self.docstring_checker.check_file(file_str))
                    file_issues.extend(self.security_checker.check_file(file_str))
                    file_issues.extend(self.naming_checker.check_file(file_str))
                elif file_path.suffix in ['.html', '.htm']:
                    file_issues.extend(self.template_checker.check_file(file_str))
                
                # اضافه کردن نام فایل به هر issue
                rel_path = str(file_path.relative_to(self.project_root))
                for issue in file_issues:
                    issue.file_path = rel_path
                    all_issues.append(issue)
        
        # نمایش خلاصه
        stdscr.addstr(y + 1, 2, f"Completed! Checked {total_files} files", 
                     curses.A_BOLD)
        stdscr.addstr(y + 2, 2, f"Found {len(all_issues)} issues", curses.A_BOLD)
        stdscr.addstr(y + 3, 2, "Generating report...", curses.A_DIM)
        stdscr.refresh()
        curses.napms(500)
        
        # ذخیره گزارش در فایل
        project_name = self.project_root.name
        report_path = self.save_report('all', project_name, all_issues, total_files)
        
        # نمایش نتایج
        self.display_module_results(stdscr, "All Modules", all_issues, total_files, max_y, max_x)
        
        # نمایش پیام ذخیره گزارش
        max_y, max_x = stdscr.getmaxyx()
        report_msg = f"Report saved: {report_path.name}"
        stdscr.addstr(max_y - 1, 2, report_msg, curses.color_pair(COLOR_SUCCESS) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(2000)  # نمایش 2 ثانیه
    
    def check_file(self, stdscr, file_path: Path):
        """چک کردن یک فایل"""
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        
        # Header
        rel_path = str(file_path.relative_to(self.project_root))
        title = "CHECKING FILE"
        stdscr.addstr(1, (max_x - len(title)) // 2, title, 
                     curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
        stdscr.addstr(2, 0, "=" * max_x, curses.color_pair(COLOR_HEADER))
        stdscr.addstr(3, 2, rel_path, curses.color_pair(COLOR_WARNING) | curses.A_BOLD)
        stdscr.addstr(4, 0, "=" * max_x, curses.color_pair(COLOR_HEADER))
        
        # پیام در حال اجرا
        stdscr.addstr(6, 2, "Running checks...", curses.A_BOLD)
        stdscr.refresh()
        
        # اجرای چک‌ها
        issues = []
        file_str = str(file_path)
        
        y = 8
        checks_run = []
        
        if file_path.suffix == '.py':
            stdscr.addstr(y, 2, "✓ Checking base classes...", curses.color_pair(COLOR_SUCCESS))
            stdscr.refresh()
            issues.extend(self.base_class_checker.check_file(file_str))
            checks_run.append("Base Classes")
            y += 1
            
            stdscr.addstr(y, 2, "✓ Checking docstrings...", curses.color_pair(COLOR_SUCCESS))
            stdscr.refresh()
            issues.extend(self.docstring_checker.check_file(file_str))
            checks_run.append("Docstrings")
            y += 1
            
            stdscr.addstr(y, 2, "✓ Checking security...", curses.color_pair(COLOR_SUCCESS))
            stdscr.refresh()
            issues.extend(self.security_checker.check_file(file_str))
            checks_run.append("Security")
            y += 1
            
            stdscr.addstr(y, 2, "✓ Checking naming conventions...", curses.color_pair(COLOR_SUCCESS))
            stdscr.refresh()
            issues.extend(self.naming_checker.check_file(file_str))
            checks_run.append("Naming")
            y += 1
            
        elif file_path.suffix in ['.html', '.htm']:
            stdscr.addstr(y, 2, "✓ Checking template...", curses.color_pair(COLOR_SUCCESS))
            stdscr.refresh()
            issues.extend(self.template_checker.check_file(file_str))
            checks_run.append("Template")
            y += 1
        
        # اضافه کردن file_path به هر issue
        rel_path = str(file_path.relative_to(self.project_root))
        for issue in issues:
            issue.file_path = rel_path
        
        y += 1
        stdscr.addstr(y, 2, f"Completed {len(checks_run)} checks", curses.A_BOLD)
        stdscr.addstr(y + 1, 2, "Generating report...", curses.A_DIM)
        stdscr.refresh()
        
        # کمی صبر برای نمایش
        curses.napms(500)
        
        # ذخیره گزارش در فایل
        report_path = self.save_report('manual', rel_path, issues, 1)
        
        # نمایش نتایج در صفحه جدید
        self.display_results(stdscr, issues, max_y, max_x)
        
        # نمایش پیام ذخیره گزارش بعد از بستن صفحه نتایج
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        report_msg = f"✓ Report saved successfully!"
        file_msg = f"File: {report_path.name}"
        path_msg = f"Location: {report_path.relative_to(self.project_root)}"
        
        stdscr.addstr(max_y // 2 - 1, (max_x - len(report_msg)) // 2, report_msg,
                     curses.color_pair(COLOR_SUCCESS) | curses.A_BOLD)
        stdscr.addstr(max_y // 2, (max_x - len(file_msg)) // 2, file_msg)
        stdscr.addstr(max_y // 2 + 1, (max_x - len(path_msg)) // 2, path_msg,
                     curses.color_pair(COLOR_WARNING))
        stdscr.addstr(max_y - 1, (max_x - 30) // 2, "Press any key to continue...",
                     curses.A_BOLD)
        stdscr.refresh()
        stdscr.getch()
    
    def display_module_results(self, stdscr, module_name: str, issues, total_files: int, max_y, max_x):
        """نمایش نتایج چک ماژول یا کل پروژه"""
        if not issues:
            stdscr.clear()
            title = f"{module_name} - All Clean!"
            stdscr.addstr(max_y // 2 - 1, (max_x - len(title)) // 2, title,
                         curses.color_pair(COLOR_SUCCESS) | curses.A_BOLD)
            stdscr.addstr(max_y // 2, (max_x - 40) // 2,
                         f"Checked {total_files} files - No issues found!",
                         curses.color_pair(COLOR_SUCCESS))
            stdscr.addstr(max_y // 2 + 2, (max_x - 35) // 2,
                         "All checks passed successfully.")
            stdscr.addstr(max_y - 1, 2, "Press any key to continue...", curses.A_BOLD)
            stdscr.refresh()
            stdscr.getch()
            return
        
        # گروه‌بندی بر اساس فایل و severity
        from collections import defaultdict
        by_file = defaultdict(list)
        by_severity = defaultdict(list)
        
        for issue in issues:
            file_path = getattr(issue, 'file_path', 'Unknown')
            by_file[file_path].append(issue)
            by_severity[issue.severity.value].append(issue)
        
        # آماده‌سازی خطوط برای نمایش
        display_lines = []
        
        # Header
        display_lines.append((f"RESULTS - {module_name}", 
                             curses.A_BOLD | curses.color_pair(COLOR_HEADER)))
        display_lines.append(("=" * 70, curses.color_pair(COLOR_HEADER)))
        display_lines.append(("", 0))
        
        # خلاصه کلی
        display_lines.append(("SUMMARY", curses.A_BOLD))
        display_lines.append((f"  Total Files Checked: {total_files}", 0))
        display_lines.append((f"  Files with Issues:   {len(by_file)}", 0))
        display_lines.append((f"  Total Issues:        {len(issues)}", curses.A_BOLD))
        
        if 'critical' in by_severity:
            display_lines.append((f"    Critical: {len(by_severity['critical'])}", 
                                 curses.color_pair(COLOR_ERROR) | curses.A_BOLD))
        if 'error' in by_severity:
            display_lines.append((f"    Errors:   {len(by_severity['error'])}", 
                                 curses.color_pair(COLOR_ERROR)))
        if 'warning' in by_severity:
            display_lines.append((f"    Warnings: {len(by_severity['warning'])}", 
                                 curses.color_pair(COLOR_WARNING)))
        
        display_lines.append(("", 0))
        display_lines.append(("=" * 70, 0))
        display_lines.append(("", 0))
        
        # نمایش بر اساس فایل
        display_lines.append(("ISSUES BY FILE", curses.A_BOLD | curses.color_pair(COLOR_HEADER)))
        display_lines.append(("", 0))
        
        for file_path in sorted(by_file.keys()):
            file_issues = by_file[file_path]
            
            # عنوان فایل
            display_lines.append((f"📄 {file_path} ({len(file_issues)} issues)", 
                                 curses.A_BOLD | curses.color_pair(COLOR_WARNING)))
            display_lines.append(("", 0))
            
            # گروه‌بندی issues این فایل بر اساس severity
            file_by_severity = defaultdict(list)
            for issue in file_issues:
                file_by_severity[issue.severity.value].append(issue)
            
            # نمایش issues بر اساس اولویت
            for severity in ['critical', 'error', 'warning']:
                if severity not in file_by_severity:
                    continue
                
                issues_list = file_by_severity[severity]
                color = COLOR_ERROR if severity in ['critical', 'error'] else COLOR_WARNING
                
                for i, issue in enumerate(issues_list, 1):
                    # شماره و خط
                    header = f"  [{severity.upper()}] Line {issue.line_number}"
                    display_lines.append((header, curses.A_BOLD | curses.color_pair(color)))
                    
                    # پیام
                    msg_lines = self._wrap_text(issue.message, max_x - 8)
                    for msg_line in msg_lines:
                        display_lines.append((f"    {msg_line}", 0))
                    
                    display_lines.append(("", 0))
            
            display_lines.append(("-" * 70, curses.A_DIM))
            display_lines.append(("", 0))
        
        # نمایش با اسکرول
        self._display_scrollable(stdscr, display_lines, max_y, max_x)
    
    def display_results(self, stdscr, issues, max_y, max_x):
        """نمایش نتایج با قابلیت اسکرول"""
        if not issues:
            stdscr.clear()
            stdscr.addstr(max_y // 2, (max_x - 20) // 2, "No issues found!", 
                         curses.color_pair(COLOR_SUCCESS) | curses.A_BOLD)
            stdscr.addstr(max_y // 2 + 1, (max_x - 35) // 2, 
                         "All checks passed successfully.",
                         curses.color_pair(COLOR_SUCCESS))
            stdscr.addstr(max_y - 1, 2, "Press any key to continue...", curses.A_BOLD)
            stdscr.refresh()
            stdscr.getch()
            return
        
        # گروه‌بندی
        from collections import defaultdict
        by_severity = defaultdict(list)
        
        for issue in issues:
            by_severity[issue.severity.value].append(issue)
        
        # آماده‌سازی خطوط برای نمایش
        display_lines = []
        
        # Header
        display_lines.append(("RESULTS", curses.A_BOLD | curses.color_pair(COLOR_HEADER)))
        display_lines.append(("=" * 60, curses.color_pair(COLOR_HEADER)))
        display_lines.append(("", 0))
        
        # خلاصه
        display_lines.append((f"Total Issues: {len(issues)}", curses.A_BOLD))
        if 'critical' in by_severity:
            display_lines.append((f"  Critical: {len(by_severity['critical'])}", 
                                 curses.color_pair(COLOR_ERROR)))
        if 'error' in by_severity:
            display_lines.append((f"  Errors:   {len(by_severity['error'])}", 
                                 curses.color_pair(COLOR_ERROR)))
        if 'warning' in by_severity:
            display_lines.append((f"  Warnings: {len(by_severity['warning'])}", 
                                 curses.color_pair(COLOR_WARNING)))
        
        display_lines.append(("", 0))
        display_lines.append(("-" * 60, 0))
        display_lines.append(("", 0))
        
        # نمایش تمام issues
        for severity in ['critical', 'error', 'warning']:
            if severity not in by_severity:
                continue
            
            issues_list = by_severity[severity]
            color = COLOR_ERROR if severity in ['critical', 'error'] else COLOR_WARNING
            
            display_lines.append((f"[{severity.upper()}] ({len(issues_list)} issues)", 
                                 curses.A_BOLD | curses.color_pair(color)))
            display_lines.append(("", 0))
            
            for i, issue in enumerate(issues_list, 1):
                # شماره issue
                display_lines.append((f"  {i}. Line {issue.line_number}", 
                                     curses.A_BOLD | curses.color_pair(color)))
                
                # پیام (ممکن است چند خطی باشد)
                msg = issue.message
                # تقسیم پیام‌های طولانی
                msg_lines = self._wrap_text(msg, max_x - 8)
                for msg_line in msg_lines:
                    display_lines.append((f"     {msg_line}", 0))
                
                # کد (اگر وجود دارد)
                if hasattr(issue, 'code_snippet') and issue.code_snippet:
                    display_lines.append(("     Code:", curses.A_DIM))
                    code_lines = issue.code_snippet.split('\n')
                    for code_line in code_lines[:3]:  # فقط 3 خط اول
                        if code_line.strip():
                            display_lines.append((f"       {code_line[:max_x-12]}", 
                                                 curses.color_pair(COLOR_WARNING)))
                
                display_lines.append(("", 0))
            
            display_lines.append(("", 0))
        
        # نمایش با اسکرول
        self._display_scrollable(stdscr, display_lines, max_y, max_x)
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """تقسیم متن طولانی به چند خط"""
        if len(text) <= width:
            return [text]
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text[:width]]
    
    def _display_scrollable(self, stdscr, lines, max_y, max_x):
        """نمایش محتوای قابل اسکرول"""
        scroll_pos = 0
        total_lines = len(lines)
        display_height = max_y - 3
        
        while True:
            stdscr.clear()
            
            # نمایش خطوط
            for i in range(display_height):
                line_idx = scroll_pos + i
                if line_idx >= total_lines:
                    break
                
                text, attr = lines[line_idx]
                if len(text) > max_x - 4:
                    text = text[:max_x - 7] + "..."
                
                try:
                    stdscr.addstr(i, 2, text, attr)
                except:
                    pass
            
            # Footer با راهنما
            footer_y = max_y - 2
            stdscr.addstr(footer_y, 0, "─" * max_x)
            
            help_text = "[↑/↓] Scroll  [PgUp/PgDn] Page  [Home/End] Top/Bottom  [Q] Back"
            stdscr.addstr(footer_y + 1, (max_x - len(help_text)) // 2, help_text, 
                         curses.A_BOLD)
            
            # نمایش scroll position
            if total_lines > display_height:
                scroll_info = f"Line {scroll_pos + 1}-{min(scroll_pos + display_height, total_lines)}/{total_lines}"
                stdscr.addstr(footer_y + 1, max_x - len(scroll_info) - 2, scroll_info)
            
            stdscr.refresh()
            
            # دریافت کلید
            key = stdscr.getch()
            
            if key == curses.KEY_UP:
                scroll_pos = max(0, scroll_pos - 1)
            elif key == curses.KEY_DOWN:
                scroll_pos = min(max(0, total_lines - display_height), scroll_pos + 1)
            elif key == curses.KEY_PPAGE:  # Page Up
                scroll_pos = max(0, scroll_pos - display_height)
            elif key == curses.KEY_NPAGE:  # Page Down
                scroll_pos = min(max(0, total_lines - display_height), 
                               scroll_pos + display_height)
            elif key == curses.KEY_HOME:
                scroll_pos = 0
            elif key == curses.KEY_END:
                scroll_pos = max(0, total_lines - display_height)
            elif key == ord('q') or key == ord('Q') or key == 27:  # ESC
                break
    
    def run(self, stdscr):
        """اجرای اصلی با curses"""
        # راه‌اندازی رنگ‌ها
        curses.start_color()
        curses.init_pair(COLOR_HEADER, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(COLOR_FOLDER, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(COLOR_FILE, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(COLOR_ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(COLOR_WARNING, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(COLOR_SUCCESS, curses.COLOR_GREEN, curses.COLOR_BLACK)
        
        # تنظیمات
        curses.curs_set(0)  # مخفی کردن cursor
        
        while True:
            choice = self.show_main_menu(stdscr)
            
            if choice == '1':
                # چک دستی - انتخاب یک فایل
                selected_file = self.file_browser_loop(stdscr)
                if selected_file:
                    self.check_file(stdscr, selected_file)
            
            elif choice == '2':
                # چک ماژول - انتخاب یک ماژول
                selected_module = self.select_module(stdscr)
                if selected_module:
                    self.check_module(stdscr, selected_module)
            
            elif choice == '3':
                # چک کامل - چک کردن کل پروژه
                stdscr.clear()
                max_y, max_x = stdscr.getmaxyx()
                
                # تایید از کاربر
                title = "Check Entire Project?"
                stdscr.addstr(max_y // 2 - 3, (max_x - len(title)) // 2, title,
                             curses.color_pair(COLOR_WARNING) | curses.A_BOLD)
                
                msg1 = "This will check ALL modules and may take some time."
                stdscr.addstr(max_y // 2 - 1, (max_x - len(msg1)) // 2, msg1)
                
                msg2 = "Continue? [Y/N]"
                stdscr.addstr(max_y // 2 + 1, (max_x - len(msg2)) // 2, msg2,
                             curses.A_BOLD)
                
                stdscr.refresh()
                
                curses.echo()
                confirm = stdscr.getch()
                curses.noecho()
                
                if confirm in [ord('y'), ord('Y')]:
                    self.check_all_project(stdscr)
            
            elif choice == '4':
                stdscr.clear()
                stdscr.addstr(5, 5, "Weekly Report - Coming Soon!")
                stdscr.addstr(7, 5, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
            
            elif choice == '5':
                stdscr.clear()
                stdscr.addstr(5, 5, "Settings - Coming Soon!")
                stdscr.addstr(7, 5, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
            
            elif choice == 'q':
                break


def main():
    """Entry point"""
    # تشخیص project root
    current_dir = Path.cwd()
    
    if current_dir.name == 'standards_checker':
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    if not (project_root / 'manage.py').exists():
        print("Error: Not in Django project directory")
        print("Please run from project root or standards_checker folder")
        sys.exit(1)
    
    # اجرا با curses
    checker = InteractiveChecker(project_root)
    
    try:
        curses.wrapper(checker.run)
        print("\nGoodbye! 👋\n")
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye! 👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

