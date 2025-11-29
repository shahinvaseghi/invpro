# راهنمای اجرای Migration برای عملیات تولید

## مشکل
جدول `production_processoperation` در دیتابیس وجود ندارد و باید migration اجرا شود.

## راه حل

### 1. فعال کردن Virtual Environment
```bash
source .venv/bin/activate
# یا
source venv/bin/activate
```

### 2. بررسی وضعیت Migration
```bash
python manage.py showmigrations production
```

### 3. اجرای Migration
```bash
python manage.py migrate production
```

### 4. بررسی موفقیت Migration
```bash
python manage.py showmigrations production
```

باید خط `[X] 0022_add_process_operations` را ببینید که علامت X دارد (اجرا شده).

## اگر خطا داد

اگر migration خطا داد، می‌توانید به صورت دستی migration را اجرا کنید:

```bash
python manage.py migrate production 0022_add_process_operations
```

یا اگر می‌خواهید همه migrations را اجرا کنید:

```bash
python manage.py migrate
```

## بعد از Migration

بعد از اجرای migration، سرور را restart کنید و صفحه Processes را refresh کنید.

