"""
سرویس برای فراخوانی درختچه حساب‌ها از فایل معیار
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.core.exceptions import ValidationError

from accounting.models.accounts import AccountGroup, Account


class AccountTreeImporter:
    """کلاس برای پارس کردن فایل و ایجاد درختچه حساب‌ها"""
    
    def __init__(self, company_id: int, update_existing: bool = True, skip_protected: bool = True):
        """
        Args:
            company_id: شناسه شرکت
            update_existing: اگر True باشد، حساب‌های موجود را update می‌کند (اگر تفصیلی نداشته باشند)
            skip_protected: اگر True باشد، حساب‌هایی که تفصیلی دارند را skip می‌کند
        """
        self.company_id = company_id
        self.update_existing = update_existing
        self.skip_protected = skip_protected
        self.stats = {
            'groups_created': 0,
            'groups_skipped': 0,
            'groups_updated': 0,
            'gl_accounts_created': 0,
            'gl_accounts_skipped': 0,
            'gl_accounts_updated': 0,
            'gl_accounts_protected': 0,
            'sub_accounts_created': 0,
            'sub_accounts_skipped': 0,
            'sub_accounts_updated': 0,
            'sub_accounts_protected': 0,
            'errors': [],
        }
        self.group_cache: Dict[str, AccountGroup] = {}
        self.gl_account_cache: Dict[str, Account] = {}
    
    def get_file_path(self) -> Path:
        """مسیر فایل معیار را برمی‌گرداند (اول JSON، سپس TXT برای backward compatibility)"""
        # فایل در پوشه data ماژول accounting قرار دارد
        accounting_dir = Path(__file__).parent.parent
        json_path = accounting_dir / 'data' / 'chart_of_accounts.json'
        txt_path = accounting_dir / 'data' / 'chart_of_accounts.txt'
        
        # اول JSON را چک می‌کنیم (فایل اصلی)
        if json_path.exists():
            return json_path
        # اگر JSON وجود نداشت، از txt استفاده می‌کنیم (backward compatibility)
        elif txt_path.exists():
            return txt_path
        else:
            raise FileNotFoundError(f"هیچ فایل معیاری یافت نشد. لطفاً فایل chart_of_accounts.json را در {accounting_dir / 'data'} قرار دهید.")
    
    def parse_file(self) -> Dict:
        """
        فایل را پارس می‌کند و ساختار حساب‌ها را برمی‌گرداند
        
        Returns:
            dict: شامل groups, gl_accounts, sub_accounts
        """
        file_path = self.get_file_path()
        
        if not file_path.exists():
            raise FileNotFoundError(f"فایل معیار در مسیر {file_path} یافت نشد")
        
        # اگر فایل JSON است، از JSON استفاده می‌کنیم
        if file_path.suffix == '.json':
            return self._parse_json_file(file_path)
        else:
            # در غیر این صورت از فایل متنی استفاده می‌کنیم
            return self._parse_text_file(file_path)
    
    def _parse_json_file(self, file_path: Path) -> Dict:
        """پارس کردن فایل JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        groups = []
        gl_accounts = []
        sub_accounts = []
        
        for group_data in data.get('groups', []):
            group_code = group_data.get('code')
            group_name = group_data.get('name', '')
            
            groups.append({
                'code': group_code,
                'name': group_name,
            })
            
            for gl_data in group_data.get('gl_accounts', []):
                gl_code = gl_data.get('code')
                gl_name = gl_data.get('name', '')
                
                gl_accounts.append({
                    'code': gl_code,
                    'name': gl_name,
                    'group_code': group_code,
                })
                
                for sub_data in gl_data.get('sub_accounts', []):
                    sub_code = sub_data.get('code')
                    sub_name = sub_data.get('name', '')
                    
                    sub_accounts.append({
                        'code': sub_code,
                        'name': sub_name,
                        'gl_code': gl_code,
                    })
        
        return {
            'groups': groups,
            'gl_accounts': gl_accounts,
            'sub_accounts': sub_accounts,
        }
    
    def _parse_text_file(self, file_path: Path) -> Dict:
        """پارس کردن فایل متنی (برای backward compatibility)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # پارس کردن محتوا
        groups = []
        gl_accounts = []
        sub_accounts = []
        
        lines = content.split('\n')
        current_group_code = None
        current_group_name = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # تشخیص گروه جدید - چند فرمت مختلف
            # فرمت 1: "گروه اول دارایی های جاری که ... کد گروه اول پس 1 شروع میشودو نام آن دارایی های جاری است"
            # فرمت 2: "گرو ه 2 که نام آن دارایی های غیر جاری است:"
            # فرمت 3: "گروه 3 که نام آن بدهی های جاری است :"
            # فرمت 4: "گروه 6 که نام آن درآمد هاست:"
            # فرمت 5: "گروه 9 که حساب های انتظامی است :" (بدون نام)
            group_match = None
            if 'گروه اول' in line or ('گروه 1' in line and 'دارایی های جاری' in line):
                # برای گروه اول، نام از خط استخراج می‌شود
                if 'دارایی های جاری' in line:
                    group_match = {'code': '1', 'name': 'دارایی های جاری'}
            elif re.search(r'گرو\s*ه\s*(\d+)', line):
                # فرمت: "گرو ه X که نام آن ... است" یا "گروه X که ... است" (بدون نام)
                match = re.search(r'گرو\s*ه\s*(\d+)\s*که\s*(?:نام\s*آن\s*)?(.+?)\s*است', line)
                if match:
                    group_code = match.group(1)
                    group_name = match.group(2).strip().rstrip(':').rstrip()
                    # اگر نام خالی است یا فقط "حساب های انتظامی" است، نام را خالی می‌گذاریم
                    if not group_name or group_name == 'حساب های انتظامی':
                        group_name = ''
                    group_match = {'code': group_code, 'name': group_name}
            elif re.search(r'^گروه\s*(\d+)', line):
                # فرمت: "گروه X که نام آن ... است" یا "گروه X که ... است" (بدون نام)
                match = re.search(r'^گروه\s*(\d+)\s*که\s*(?:نام\s*آن\s*)?(.+?)\s*است', line)
                if match:
                    group_code = match.group(1)
                    group_name = match.group(2).strip().rstrip(':').rstrip()
                    # اگر نام خالی است یا فقط "حساب های انتظامی" است، نام را خالی می‌گذاریم
                    if not group_name or group_name == 'حساب های انتظامی':
                        group_name = ''
                    group_match = {'code': group_code, 'name': group_name}
            
            if group_match:
                current_group_code = group_match['code']
                current_group_name = group_match['name']
                groups.append({
                    'code': current_group_code,
                    'name': current_group_name,
                })
                i += 1
                continue
            
            # ابتدا معین را چک می‌کنیم (4 رقمی) تا با حساب کل (2 رقمی) اشتباه نشود
            # تشخیص معین
            sub_match = None
            # فرمت با "کد" - "صندوق کد 1101"
            match_with_kod = re.search(r'^(.+?)\s+کد\s+(\d{4})\s*$', line)
            if match_with_kod:
                # نام را بدون "کد" می‌گیریم
                account_name = match_with_kod.group(1).strip()
                account_code = match_with_kod.group(2).strip()
                if len(account_code) == 4 and account_code.isdigit():
                    gl_code = account_code[:2]
                    is_duplicate = any(acc['code'] == account_code for acc in sub_accounts)
                    if not is_duplicate and current_group_code:
                        sub_account = {
                            'code': account_code,
                            'name': account_name,
                            'gl_code': gl_code,
                        }
                        sub_accounts.append(sub_account)
                        i += 1
                        continue
            else:
                # فرمت: کد در ابتدای خط "3401 مالیات پرداختنی سال"
                match_code_first = re.search(r'^(\d{4})\s+(.+?)\s*$', line)
                if match_code_first:
                    account_code = match_code_first.group(1)
                    account_name = match_code_first.group(2).strip()
                    # بررسی اینکه آیا قبلاً ثبت نشده
                    is_duplicate = any(acc['code'] == account_code for acc in sub_accounts)
                    if not is_duplicate and current_group_code:
                        gl_code = account_code[:2]  # دو رقم اول = کد حساب کل
                        sub_account = {
                            'code': account_code,
                            'name': account_name,
                            'gl_code': gl_code,
                        }
                        sub_accounts.append(sub_account)
                        i += 1
                        continue
                else:
                    # فرمت بدون "کد" - عدد 4 رقمی در انتها (با یا بدون فاصله)
                    # ممکن است نقطه‌های اضافی قبل از کد باشد: "... 5302" یا ".. 5701"
                    # مهم: باید مطمئن شویم که عدد دقیقاً 4 رقم است (نه 2 رقم)
                    match_without_kod = re.search(r'^(.+?)\s*\.{0,3}\s*(\d{4})\s*$', line)
                    if match_without_kod:
                        account_code = match_without_kod.group(2)
                        # بررسی اینکه عدد دقیقاً 4 رقم است
                        if len(account_code) == 4 and account_code.isdigit():
                            # بررسی اینکه خط قبلی "که شامل" نیست
                            prev_line = lines[i - 1].strip() if i > 0 else ""
                            if (not prev_line.startswith('که شامل') and 
                                not prev_line.startswith('حساب های کل')):
                                sub_match = match_without_kod
            
            if sub_match and current_group_code:
                account_name = sub_match.group(1).strip()
                account_code = sub_match.group(2).strip()
                
                # بررسی اینکه آیا این معین است (4 رقم)
                if len(account_code) == 4 and account_code.isdigit():
                    gl_code = account_code[:2]  # دو رقم اول = کد حساب کل
                    
                    # بررسی اینکه آیا قبلاً ثبت نشده
                    is_duplicate = any(acc['code'] == account_code for acc in sub_accounts)
                    if not is_duplicate:
                        sub_account = {
                            'code': account_code,
                            'name': account_name,
                            'gl_code': gl_code,
                        }
                        sub_accounts.append(sub_account)
                        i += 1
                        continue
            
            # تشخیص حساب کل (بعد از چک کردن معین)
            # فرمت: "نام حساب کل11" یا "نام حساب کل 11" یا "دارایی های نامشهود24"
            # یا "حسابها و اسناد دریافتنی تجاری 14" یا "حساب ها و اسناد دریافتنی بلند مدت 21"
            # یا "اسناد پرداختنی 31که شامل" (بدون فاصله بین کد و "که")
            # یا "حسابهای انتظامی 91که شامل" (بدون نام یا با نام)
            # شرط: عدد 2 رقمی در انتها و خط بعدی "که شامل دفتر" است
            # یا عدد 2 رقمی که بعدش "که شامل" آمده (در همان خط)
            # مهم: باید مطمئن شویم که عدد دقیقاً 2 رقم است (نه 4 رقم)
            gl_match = None
            # فرمت: "نام 31که شامل" یا "حسابهای انتظامی 91که شامل" - عدد 2 رقمی که بعدش "که" آمده
            match_with_ke = re.search(r'^(.+?)\s*(\d{2})که\s*شامل', line)
            if match_with_ke:
                account_code = match_with_ke.group(2)
                # بررسی اینکه عدد دقیقاً 2 رقم است و بعدش "که" آمده (نه 4 رقم)
                if len(account_code) == 2 and account_code.isdigit():
                    gl_match = match_with_ke
            else:
                # فرمت: "نام 11" یا "نام11" - عدد 2 رقمی در انتها
                # مهم: باید مطمئن شویم که عدد دقیقاً 2 رقم است (نه 4 رقم)
                match_normal = re.search(r'^(.+?)\s*(\d{2})\s*$', line)
                if match_normal:
                    account_code = match_normal.group(2)
                    # بررسی اینکه عدد دقیقاً 2 رقم است (نه 4 رقم)
                    if len(account_code) == 2 and account_code.isdigit():
                        # بررسی خط بعدی - اگر "که شامل دفتر" باشد، این حساب کل است
                        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                        if 'که شامل دفتر' in next_line or 'که شامل' in next_line:
                            gl_match = match_normal
            
            if gl_match and current_group_code:
                account_name = gl_match.group(1).strip()
                account_code = gl_match.group(2).strip()
                
                # بررسی اینکه آیا این حساب کل است (2 رقم)
                if len(account_code) == 2 and account_code.isdigit():
                    # بررسی اینکه آیا قبلاً به عنوان معین ثبت نشده
                    is_duplicate = any(acc['code'] == account_code for acc in gl_accounts)
                    if not is_duplicate:
                        gl_account = {
                            'code': account_code,
                            'name': account_name,
                            'group_code': current_group_code,
                        }
                        gl_accounts.append(gl_account)
                        i += 1
                        continue
            
            i += 1
        
        return {
            'groups': groups,
            'gl_accounts': gl_accounts,
            'sub_accounts': sub_accounts,
        }
    
    def create_or_get_group(self, group_code: str, group_name: str) -> AccountGroup:
        """گروه را ایجاد می‌کند یا برمی‌گرداند (یا update می‌کند)"""
        if group_code in self.group_cache:
            return self.group_cache[group_code]
        
        # بررسی وجود گروه
        try:
            group = AccountGroup.objects.get(
                company_id=self.company_id,
                group_code=group_code
            )
            # اگر update_existing فعال باشد، نام را update می‌کنیم
            if self.update_existing and group.group_name != group_name:
                group.group_name = group_name
                group.save()
                self.stats['groups_updated'] += 1
            else:
                self.stats['groups_skipped'] += 1
        except AccountGroup.DoesNotExist:
            group = AccountGroup.objects.create(
                company_id=self.company_id,
                group_code=group_code,
                group_name=group_name,
                is_enabled=1,
            )
            self.stats['groups_created'] += 1
        
        self.group_cache[group_code] = group
        return group
    
    def has_tafsili_children(self, account: Account) -> bool:
        """بررسی می‌کند که آیا حساب تفصیلی (child) دارد یا نه"""
        # بررسی child_accounts (معین‌ها یا تفصیلی‌ها)
        if account.child_accounts.filter(is_enabled=1).exists():
            return True
        
        # اگر حساب معین است، بررسی tafsili_sub_relations
        if account.account_level == 2:
            from accounting.models.accounts import TafsiliSubAccountRelation
            if TafsiliSubAccountRelation.objects.filter(
                company_id=self.company_id,
                sub_account=account,
                is_enabled=1
            ).exists():
                return True
        
        return False
    
    def create_or_get_gl_account(self, account_code: str, account_name: str, group_code: str) -> Account:
        """حساب کل را ایجاد می‌کند یا برمی‌گرداند (یا update می‌کند)"""
        cache_key = f"{group_code}_{account_code}"
        if cache_key in self.gl_account_cache:
            return self.gl_account_cache[cache_key]
        
        # دریافت گروه
        group = self.create_or_get_group(group_code, '')  # نام گروه قبلاً ایجاد شده
        
        # بررسی وجود حساب کل
        try:
            gl_account = Account.objects.get(
                company_id=self.company_id,
                account_code=account_code,
                account_level=1
            )
            
            # بررسی اینکه آیا حساب تفصیلی (معین) دارد
            has_children = self.has_tafsili_children(gl_account)
            
            if has_children and self.skip_protected:
                # اگر تفصیلی دارد و skip_protected فعال است، skip می‌کنیم
                self.stats['gl_accounts_protected'] += 1
            elif self.update_existing:
                # اگر تفصیلی ندارد یا skip_protected غیرفعال است، update می‌کنیم
                account_type = self._get_account_type_from_group(int(group_code))
                gl_account.account_name = account_name
                gl_account.account_group = group
                if account_type:
                    gl_account.account_type = account_type
                gl_account.is_system_account = 1
                gl_account.save()
                self.stats['gl_accounts_updated'] += 1
            else:
                self.stats['gl_accounts_skipped'] += 1
        except Account.DoesNotExist:
            # تعیین account_type بر اساس گروه
            account_type = self._get_account_type_from_group(int(group_code))
            
            try:
                gl_account = Account.objects.create(
                    company_id=self.company_id,
                    account_code=account_code,
                    account_name=account_name,
                    account_level=1,  # کل
                    account_group=group,
                    account_type=account_type,
                    is_enabled=1,
                    is_system_account=1,  # حساب‌های سیستم
                )
                self.stats['gl_accounts_created'] += 1
            except Exception as e:
                self.stats['errors'].append(f"خطا در ایجاد حساب کل {account_code}: {str(e)}")
                raise
        
        self.gl_account_cache[cache_key] = gl_account
        return gl_account
    
    def create_or_get_sub_account(self, account_code: str, account_name: str, gl_code: str) -> Account:
        """حساب معین را ایجاد می‌کند یا برمی‌گرداند (یا update می‌کند)"""
        # دریافت حساب کل
        group_code = gl_code[0]
        gl_account = self.create_or_get_gl_account(gl_code, '', group_code)
        
        # بررسی وجود معین
        try:
            sub_account = Account.objects.get(
                company_id=self.company_id,
                account_code=account_code,
                account_level=2
            )
            
            # بررسی اینکه آیا حساب تفصیلی دارد
            has_children = self.has_tafsili_children(sub_account)
            
            if has_children and self.skip_protected:
                # اگر تفصیلی دارد و skip_protected فعال است، skip می‌کنیم
                self.stats['sub_accounts_protected'] += 1
            elif self.update_existing:
                # اگر تفصیلی ندارد یا skip_protected غیرفعال است، update می‌کنیم
                account_type = gl_account.account_type
                sub_account.account_name = account_name
                sub_account.parent_account = gl_account
                if account_type:
                    sub_account.account_type = account_type
                sub_account.is_system_account = 1
                sub_account.save()
                self.stats['sub_accounts_updated'] += 1
            else:
                self.stats['sub_accounts_skipped'] += 1
        except Account.DoesNotExist:
            # تعیین account_type از حساب کل والد
            account_type = gl_account.account_type
            
            try:
                sub_account = Account.objects.create(
                    company_id=self.company_id,
                    account_code=account_code,
                    account_name=account_name,
                    account_level=2,  # معین
                    parent_account=gl_account,
                    account_type=account_type,
                    is_enabled=1,
                    is_system_account=1,  # حساب‌های سیستم
                )
                self.stats['sub_accounts_created'] += 1
            except Exception as e:
                self.stats['errors'].append(f"خطا در ایجاد حساب معین {account_code}: {str(e)}")
                raise
        
        return sub_account
    
    def _get_account_type_from_group(self, group_code: int) -> str:
        """نوع حساب را بر اساس کد گروه تعیین می‌کند"""
        # گروه 1: دارایی‌های جاری -> ASSET
        # گروه 2: دارایی‌های غیرجاری -> ASSET
        # گروه 3: بدهی‌های جاری -> LIABILITY
        # گروه 4: بدهی‌های بلندمدت -> LIABILITY
        # گروه 5: حقوق صاحبان سهام -> EQUITY
        # گروه 6: درآمدها -> REVENUE
        # گروه 7: هزینه‌ها -> EXPENSE
        # گروه 9: حساب‌های انتظامی -> None (nullable)
        
        type_mapping = {
            1: 'ASSET',
            2: 'ASSET',
            3: 'LIABILITY',
            4: 'LIABILITY',
            5: 'EQUITY',
            6: 'REVENUE',
            7: 'EXPENSE',
            9: None,  # حساب‌های انتظامی
        }
        
        return type_mapping.get(group_code)
    
    def import_account_tree(self) -> Dict:
        """
        درختچه حساب‌ها را از فایل فراخوانی و ایجاد می‌کند
        
        Returns:
            dict: آمار ایجاد شده
        """
        # پارس کردن فایل
        parsed_data = self.parse_file()
        
        # ایجاد گروه‌ها
        for group_data in parsed_data['groups']:
            self.create_or_get_group(
                group_data['code'],
                group_data['name']
            )
        
        # ایجاد حساب‌های کل
        for gl_data in parsed_data['gl_accounts']:
            self.create_or_get_gl_account(
                gl_data['code'],
                gl_data['name'],
                gl_data['group_code']
            )
        
        # ایجاد معین‌ها
        for sub_data in parsed_data['sub_accounts']:
            self.create_or_get_sub_account(
                sub_data['code'],
                sub_data['name'],
                sub_data['gl_code']
            )
        
        return self.stats

