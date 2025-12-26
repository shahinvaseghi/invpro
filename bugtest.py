"""
Bug Test File - این فایل شامل تمام انواع مشکلات و تخلفات از استانداردها است
برای تست کردن Standards Checker استفاده می‌شود
"""

# ============================================================================
# 1. BASE CLASSES ISSUES
# ============================================================================

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.views import View
from django.http import HttpResponse
from django.db import models, connection
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
import os

# ❌ مشکل: استفاده از Django generic views به جای Base views
class ItemListView(ListView):
    model = None

class ItemCreateView(CreateView):
    model = None

class ItemUpdateView(UpdateView):
    model = None

class ItemDeleteView(DeleteView):
    model = None

class ItemDetailView(DetailView):
    model = None

class ItemFormView(FormView):
    pass

# ============================================================================
# 2. DOCUMENTATION ISSUES
# ============================================================================

# ❌ مشکل: Missing docstring
class UserModel:
    def __init__(self):
        pass
    
    def get_name(self):
        return "Test"
    
    def process_data(self, data):
        return data

# ❌ مشکل: Function بدون docstring
def calculate_total(price, quantity):
    return price * quantity

def process_order(order_id):
    # Missing docstring
    pass

# ❌ مشکل: Class بدون docstring
class OrderProcessor:
    def process(self):
        pass

# ============================================================================
# 3. SECURITY ISSUES
# ============================================================================

# ❌ مشکل: SQL Injection
def get_user_data(user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL Injection!
    return cursor.fetchall()

# ❌ مشکل: Hardcoded secret
SECRET_KEY = "django-insecure-test-key-12345"  # Hardcoded secret!
API_KEY = "sk-1234567890abcdef"  # Hardcoded API key!

# ❌ مشکل: XSS vulnerability
def render_user_content(content):
    return mark_safe(content)  # XSS risk!

# ============================================================================
# 4. NAMING ISSUES
# ============================================================================

# ❌ مشکل: Class با snake_case به جای PascalCase
class user_service:  # Should be UserService
    pass

class order_processor:  # Should be OrderProcessor
    pass

# ❌ مشکل: Function با PascalCase به جای snake_case
def GetUserData():  # Should be get_user_data
    pass

def ProcessOrder():  # Should be process_order
    pass

# ============================================================================
# 5. PERFORMANCE ISSUES
# ============================================================================

from django.db.models import Q

# ❌ مشکل: N+1 Query
def get_items_with_categories():
    items = models.Model.objects.all()  # Missing select_related!
    for item in items:
        print(item.category.name)  # N+1 query!
        print(item.subcategory.name)  # Another query!
    return items

# ❌ مشکل: Missing prefetch_related
def get_orders_with_lines():
    orders = models.Model.objects.all()  # Missing prefetch_related!
    for order in orders:
        for line in order.lines.all():  # N+1 query!
            print(line.product.name)
    return orders

# ❌ مشکل: Query بدون optimization
def get_user_data():
    users = models.Model.objects.all()  # Should use only() or defer()
    return users

# ============================================================================
# 6. SHARED COMPONENTS ISSUES
# ============================================================================

# ❌ مشکل: استفاده مستقیم از search به جای apply_search
def search_items(request):
    search = request.GET.get('search')
    queryset = models.Model.objects.all()
    if search:
        queryset = queryset.filter(Q(name__icontains=search))  # Should use apply_search!
    return queryset

# ❌ مشکل: استفاده مستقیم از filter به جای apply_status_filter
def filter_by_status(request):
    status = request.GET.get('status')
    queryset = models.Model.objects.all()
    if status:
        queryset = queryset.filter(status=status)  # Should use apply_status_filter!
    return queryset

# ❌ مشکل: Missing mixins
class MyView(View):
    # Should use PermissionFilterMixin, AutoSetFieldsMixin, etc.
    pass

# ============================================================================
# 7. SECURITY ENHANCED ISSUES
# ============================================================================

# ❌ مشکل: View بدون @login_required
def unprotected_view(request):
    return HttpResponse("This should be protected!")

# ❌ مشکل: View بدون feature_code
class UnprotectedListView(View):
    # Missing feature_code attribute!
    pass

# ❌ مشکل: Form بدون CSRF (این در template است اما برای مثال)
# در template باید {% csrf_token %} باشد

# ============================================================================
# 8. TESTING ISSUES
# ============================================================================

# ❌ مشکل: Test method نامناسب
def test():  # Too short!
    pass

def testUser():  # PascalCase instead of snake_case!
    pass

def test_user():  # Missing docstring!
    assert True

# ❌ مشکل: Test بدون AAA pattern
def test_order_creation():
    order = models.Model.objects.create()  # Missing Arrange, Act, Assert comments!
    assert order.id is not None

# ❌ مشکل: Test بدون setUp
class OrderTest:
    def test_something(self):
        # Missing setUp method!
        pass

# ============================================================================
# 9. API ISSUES
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response

# ❌ مشکل: استفاده از APIView به جای BaseAPIView
class MyAPIView(APIView):  # Should use BaseAPIView!
    def get(self, request):
        return Response({'data': []}, status=200)  # Magic number!

# ❌ مشکل: Response format نادرست
class BadAPIView(APIView):
    def get(self, request):
        return Response({'items': []})  # Missing status, message!

# ❌ مشکل: بدون versioning
# URL should be /api/v1/endpoint/ not /api/endpoint/

# ============================================================================
# 10. DATABASE & MIGRATION ISSUES
# ============================================================================

# ❌ مشکل: ForeignKey بدون on_delete
class BadModel(models.Model):
    user = models.ForeignKey('auth.User')  # Missing on_delete!
    category = models.ForeignKey('Category')  # Missing on_delete!

# ❌ مشکل: Migration بدون reverse
# در migration files باید RunPython(forward_func, reverse_func) باشد

# ============================================================================
# 11. ERROR HANDLING & LOGGING ISSUES
# ============================================================================

# ❌ مشکل: استفاده از print به جای logger
def process_data(data):
    print(f"Processing data: {data}")  # Should use logger!
    return data

# ❌ مشکل: Bare except
def risky_function():
    try:
        # Some code
        pass
    except:  # Bare except!
        pass

# ❌ مشکل: Logging sensitive data
import logging
logger = logging.getLogger(__name__)

def login_user(username, password):
    logger.info(f"User {username} logged in with password: {password}")  # Sensitive data!

# ============================================================================
# 12. CODE QUALITY ISSUES
# ============================================================================

# ❌ مشکل: Function خیلی طولانی (بیشتر از 50 خط)
def very_long_function():
    # Line 1
    x = 1
    # Line 2
    y = 2
    # Line 3
    z = 3
    # Line 4
    a = 4
    # Line 5
    b = 5
    # Line 6
    c = 6
    # Line 7
    d = 7
    # Line 8
    e = 8
    # Line 9
    f = 9
    # Line 10
    g = 10
    # Line 11
    h = 11
    # Line 12
    i = 12
    # Line 13
    j = 13
    # Line 14
    k = 14
    # Line 15
    l = 15
    # Line 16
    m = 16
    # Line 17
    n = 17
    # Line 18
    o = 18
    # Line 19
    p = 19
    # Line 20
    q = 20
    # Line 21
    r = 21
    # Line 22
    s = 22
    # Line 23
    t = 23
    # Line 24
    u = 24
    # Line 25
    v = 25
    # Line 26
    w = 26
    # Line 27
    x2 = 27
    # Line 28
    y2 = 28
    # Line 29
    z2 = 29
    # Line 30
    a2 = 30
    # Line 31
    b2 = 31
    # Line 32
    c2 = 32
    # Line 33
    d2 = 33
    # Line 34
    e2 = 34
    # Line 35
    f2 = 35
    # Line 36
    g2 = 36
    # Line 37
    h2 = 37
    # Line 38
    i2 = 38
    # Line 39
    j2 = 39
    # Line 40
    k2 = 40
    # Line 41
    l2 = 41
    # Line 42
    m2 = 42
    # Line 43
    n2 = 43
    # Line 44
    o2 = 44
    # Line 45
    p2 = 45
    # Line 46
    q2 = 46
    # Line 47
    r2 = 47
    # Line 48
    s2 = 48
    # Line 49
    t2 = 49
    # Line 50
    u2 = 50
    # Line 51 - بیش از 50 خط!
    v2 = 51
    return v2

# ❌ مشکل: Class خیلی طولانی (بیشتر از 500 خط - برای مثال کوچک)
class VeryLongClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
    
    def method3(self):
        pass
    
    def method4(self):
        pass
    
    def method5(self):
        pass

# ============================================================================
# 13. TEMPLATE ISSUES (برای مثال - این در template files است)
# ============================================================================

# در template files باید چک شود:
# - Inline styles: <div style="color: red;">
# - Inline JavaScript: <button onclick="doSomething()">
# - Missing {% load static %} when using {% static %}
# - Missing {% csrf_token %} in forms

# ============================================================================
# 14. GIT WORKFLOW ISSUES (این در git history است)
# ============================================================================

# Commit messages باید فرمت conventional commits داشته باشند:
# ✅ درست: feat(inventory): add barcode support
# ❌ اشتباه: added new feature

# Branch names باید فرمت داشته باشند:
# ✅ درست: feature/add-barcode-support
# ❌ اشتباه: new-feature

