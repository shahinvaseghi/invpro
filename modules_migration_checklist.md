# چک‌لیست Migration ماژول‌ها - استفاده از فایل‌های مشترک

این چک‌لیست مشخص می‌کند که کدام فایل‌ها در هر ماژول باید تغییر کنند و دقیقاً چه بخش‌هایی از کد باید حذف یا تغییر یابند.

**نکته مهم**: بعد از ساخت فایل‌های مشترک در `shared`، باید تمام viewهای ماژول‌ها را migrate کنیم تا از Base classes استفاده کنند.

---

## ماژول ۱: `shared` (Pilot Module)

### فایل: `shared/views/companies.py`

#### کلاس: `CompanyListView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, ListView` به `FeaturePermissionRequiredMixin, BaseListView`
- [ ] **حذف متد `get_queryset()`**: 
  ```python
  # حذف این بخش:
  def get_queryset(self):
      """Filter companies by user access."""
      user = self.request.user
      company_id = self.request.session.get('active_company_id')
      if not company_id:
          return models.Company.objects.none()
      
      # Get companies user has access to
      user_access = models.UserCompanyAccess.objects.filter(
          user=user,
          company_id=company_id,
          is_enabled=1
      ).values_list('company_id', flat=True)
      
      queryset = models.Company.objects.filter(id__in=user_access)
      
      # Search filter
      search = self.request.GET.get('search', '').strip()
      if search:
          queryset = queryset.filter(
              Q(public_code__icontains=search) |
              Q(display_name__icontains=search) |
              Q(legal_name__icontains=search)
          )
      
      # Status filter
      status = self.request.GET.get('status', '')
      if status in ('0', '1'):
          queryset = queryset.filter(is_enabled=int(status))
      
      return queryset.order_by('public_code')
  ```
- [ ] **حذف متد `get_context_data()`**: 
  ```python
  # حذف این بخش (حدود 40-50 خط):
  def get_context_data(self, **kwargs) -> Dict[str, Any]:
      context = super().get_context_data(**kwargs)
      context['page_title'] = _('Companies')
      context['breadcrumbs'] = [...]
      context['create_url'] = reverse_lazy('shared:company_create')
      # ... تمام context variables
      return context
  ```
- [ ] **اضافه کردن Attributes**:
  ```python
  class CompanyListView(FeaturePermissionRequiredMixin, BaseListView):
      model = models.Company
      search_fields = ['public_code', 'display_name', 'legal_name']
      filter_fields = ['is_enabled']
      feature_code = 'shared.companies'
      default_order_by = ['public_code']
      
      def get_breadcrumbs(self):
          return [
              {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
              {'label': _('Companies'), 'url': None},
          ]
      
      def get_base_queryset(self):
          """Override for custom company filtering."""
          user = self.request.user
          company_id = self.request.session.get('active_company_id')
          if not company_id:
              return models.Company.objects.none()
          
          user_access = models.UserCompanyAccess.objects.filter(
              user=user,
              company_id=company_id,
              is_enabled=1
          ).values_list('company_id', flat=True)
          
          return models.Company.objects.filter(id__in=user_access)
  ```

---

#### کلاس: `CompanyCreateView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, CreateView` به `FeaturePermissionRequiredMixin, BaseCreateView`
- [ ] **حذف متد `form_valid()`**: 
  ```python
  # حذف این بخش:
  def form_valid(self, form):
      form.instance.created_by = self.request.user
      response = super().form_valid(form)
      
      # Auto-create UserCompanyAccess for creator
      models.UserCompanyAccess.objects.create(...)
      
      messages.success(self.request, _('Company created successfully.'))
      return response
  ```
- [ ] **حذف متد `get_context_data()`**: 
  ```python
  # حذف این بخش (حدود 15-20 خط):
  def get_context_data(self, **kwargs) -> Dict[str, Any]:
      context = super().get_context_data(**kwargs)
      context['form_title'] = _('Create Company')
      context['breadcrumbs'] = [...]
      context['cancel_url'] = reverse_lazy('shared:companies')
      return context
  ```
- [ ] **اضافه کردن Attributes و Override**:
  ```python
  class CompanyCreateView(FeaturePermissionRequiredMixin, BaseCreateView):
      model = models.Company
      form_class = forms.CompanyForm
      success_url = reverse_lazy('shared:companies')
      feature_code = 'shared.companies'
      success_message = _('Company created successfully.')
      
      def get_breadcrumbs(self):
          return [
              {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
              {'label': _('Companies'), 'url': reverse_lazy('shared:companies')},
              {'label': _('Create'), 'url': None},
          ]
      
      def form_valid(self, form):
          """Override to create UserCompanyAccess."""
          response = super().form_valid(form)
          
          # Auto-create UserCompanyAccess for creator
          models.UserCompanyAccess.objects.create(
              user=self.request.user,
              company=self.object,
              access_level_id=1,  # ADMIN
              is_primary=1,
              is_enabled=1
          )
          
          return response
  ```

---

#### کلاس: `CompanyUpdateView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseUpdateView`
- [ ] **Inheritance**: تغییر از `EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView` به `FeaturePermissionRequiredMixin, BaseUpdateView` (BaseUpdateView خودش EditLockProtectedMixin دارد)
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**:
  ```python
  class CompanyUpdateView(FeaturePermissionRequiredMixin, BaseUpdateView):
      model = models.Company
      form_class = forms.CompanyForm
      success_url = reverse_lazy('shared:companies')
      feature_code = 'shared.companies'
      success_message = _('Company updated successfully.')
      
      def get_breadcrumbs(self):
          return [
              {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
              {'label': _('Companies'), 'url': reverse_lazy('shared:companies')},
              {'label': _('Edit'), 'url': None},
          ]
  ```

---

#### کلاس: `CompanyDetailView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseDetailView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, DetailView` به `FeaturePermissionRequiredMixin, BaseDetailView`
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**:
  ```python
  class CompanyDetailView(FeaturePermissionRequiredMixin, BaseDetailView):
      model = models.Company
      feature_code = 'shared.companies'
      
      def get_breadcrumbs(self):
          return [
              {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
              {'label': _('Companies'), 'url': reverse_lazy('shared:companies')},
              {'label': _('View'), 'url': None},
          ]
  ```

---

#### کلاس: `CompanyDeleteView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, DeleteView` به `FeaturePermissionRequiredMixin, BaseDeleteView`
- [ ] **حذف متد `delete()`**: 
  ```python
  # حذف این بخش:
  def delete(self, request, *args, **kwargs):
      messages.success(self.request, _('Company deleted successfully.'))
      return super().delete(request, *args, **kwargs)
  ```
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**:
  ```python
  class CompanyDeleteView(FeaturePermissionRequiredMixin, BaseDeleteView):
      model = models.Company
      success_url = reverse_lazy('shared:companies')
      feature_code = 'shared.companies'
      success_message = _('Company deleted successfully.')
      
      def get_breadcrumbs(self):
          return [
              {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
              {'label': _('Companies'), 'url': reverse_lazy('shared:companies')},
              {'label': _('Delete'), 'url': None},
          ]
      
      def get_object_details(self):
          return [
              {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
              {'label': _('Display Name'), 'value': self.object.display_name},
              {'label': _('Legal Name'), 'value': self.object.legal_name},
          ]
  ```

---

### فایل: `shared/views/users.py`

#### کلاس: `UserListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر به `BaseListView`
- [ ] **حذف**: متد `get_queryset()` (حدود 30-40 خط)
- [ ] **حذف**: متد `get_context_data()` (حدود 40-50 خط)
- [ ] **اضافه کردن**: Attributes (model, search_fields, filter_fields, feature_code)

#### کلاس: `UserCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView` (اما باید `UserAccessFormsetMixin` را حفظ کند)
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)
- [ ] **نکته**: این view از formset استفاده می‌کند، باید از `BaseFormsetCreateView` استفاده کند

#### کلاس: `UserUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetUpdateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetUpdateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `UserDetailView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDetailView`
- [ ] **Inheritance**: تغییر به `BaseDetailView`
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `UserDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر به `BaseDeleteView`
- [ ] **حذف**: متد `delete()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

---

### فایل: `shared/views/access_levels.py`

#### کلاس: `AccessLevelListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر به `BaseListView`
- [ ] **حذف**: متد `get_queryset()` (حدود 20-30 خط)
- [ ] **حذف**: متد `get_context_data()` (حدود 40-50 خط)

#### کلاس: `AccessLevelCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView` (اما باید `AccessLevelPermissionMixin` را حفظ کند)
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `AccessLevelUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseUpdateView`
- [ ] **Inheritance**: تغییر به `BaseUpdateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `AccessLevelDetailView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDetailView`
- [ ] **Inheritance**: تغییر به `BaseDetailView`
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `AccessLevelDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر به `BaseDeleteView`
- [ ] **حذف**: متد `delete()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

---

### فایل: `shared/views/groups.py`

**کلاس‌ها**: `GroupListView`, `GroupCreateView`, `GroupUpdateView`, `GroupDetailView`, `GroupDeleteView`

**تغییرات مشابه**: مانند `CompanyListView` و سایر کلاس‌ها

---

### فایل: `shared/views/company_units.py`

**کلاس‌ها**: `CompanyUnitListView`, `CompanyUnitCreateView`, `CompanyUnitUpdateView`, `CompanyUnitDetailView`, `CompanyUnitDeleteView`

**تغییرات مشابه**: مانند `CompanyListView` و سایر کلاس‌ها

---

### فایل: `shared/views/smtp_server.py`

**کلاس‌ها**: `SMTPServerListView`, `SMTPServerCreateView`, `SMTPServerUpdateView`, `SMTPServerDetailView`, `SMTPServerDeleteView`

**تغییرات مشابه**: مانند `CompanyListView` و سایر کلاس‌ها

---

## ماژول ۲: `inventory`

### فایل: `inventory/views/master_data.py`

#### کلاس: `ItemTypeListView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `InventoryBaseView, ListView` به `InventoryBaseView, BaseListView`
- [ ] **حذف متد `get_queryset()`**: 
  ```python
  # حذف این بخش:
  def get_queryset(self):
      """Filter queryset by user permissions."""
      queryset = super().get_queryset()
      queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_types', 'created_by')
      return queryset
  ```
- [ ] **حذف متد `get_context_data()`**: 
  ```python
  # حذف این بخش (حدود 20-25 خط):
  def get_context_data(self, **kwargs) -> Dict[str, Any]:
      context = super().get_context_data(**kwargs)
      context['page_title'] = _('Item Types')
      context['breadcrumbs'] = [
          {'label': _('Inventory'), 'url': None},
          {'label': _('Master Data'), 'url': None},
          {'label': _('Item Types'), 'url': None},
      ]
      context['create_url'] = reverse_lazy('inventory:itemtype_create')
      context['create_button_text'] = _('Create Item Type')
      context['table_headers'] = []
      context['show_actions'] = True
      context['feature_code'] = 'inventory.master.item_types'
      context['detail_url_name'] = 'inventory:itemtype_detail'
      context['edit_url_name'] = 'inventory:itemtype_edit'
      context['delete_url_name'] = 'inventory:itemtype_delete'
      context['empty_state_title'] = _('No Item Types Found')
      context['empty_state_message'] = _('Start by creating your first item type.')
      context['empty_state_icon'] = '🏷️'
      return context
  ```
- [ ] **اضافه کردن Attributes**:
  ```python
  class ItemTypeListView(InventoryBaseView, BaseListView):
      model = models.ItemType
      search_fields = ['name', 'public_code', 'name_en']
      filter_fields = ['is_enabled']
      feature_code = 'inventory.master.item_types'
      permission_field = 'created_by'
      default_order_by = ['public_code']
      
      def get_breadcrumbs(self):
          return [
              {'label': _('Inventory'), 'url': None},
              {'label': _('Master Data'), 'url': None},
              {'label': _('Item Types'), 'url': None},
          ]
      
      def get_page_title(self):
          return _('Item Types')
  ```

---

#### کلاس: `ItemTypeCreateView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر از `InventoryBaseView, CreateView` به `InventoryBaseView, BaseCreateView`
- [ ] **حذف متد `form_valid()`**: 
  ```python
  # حذف این بخش:
  def form_valid(self, form):
      """Set company and created_by before saving."""
      form.instance.company_id = self.request.session.get('active_company_id')
      form.instance.created_by = self.request.user
      messages.success(self.request, _('Item Type created successfully.'))
      return super().form_valid(form)
  ```
- [ ] **حذف متد `get_context_data()`**: 
  ```python
  # حذف این بخش (حدود 10-15 خط):
  def get_context_data(self, **kwargs) -> Dict[str, Any]:
      context = super().get_context_data(**kwargs)
      context['form_title'] = _('Create Item Type')
      context['breadcrumbs'] = [
          {'label': _('Inventory'), 'url': None},
          {'label': _('Master Data'), 'url': None},
          {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
          {'label': _('Create'), 'url': None},
      ]
      context['cancel_url'] = reverse_lazy('inventory:item_types')
      return context
  ```
- [ ] **اضافه کردن Attributes**:
  ```python
  class ItemTypeCreateView(InventoryBaseView, BaseCreateView):
      model = models.ItemType
      form_class = forms.ItemTypeForm
      success_url = reverse_lazy('inventory:item_types')
      feature_code = 'inventory.master.item_types'
      success_message = _('Item Type created successfully.')
      
      def get_breadcrumbs(self):
          return [
              {'label': _('Inventory'), 'url': None},
              {'label': _('Master Data'), 'url': None},
              {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
              {'label': _('Create'), 'url': None},
          ]
  ```

---

#### کلاس: `ItemTypeUpdateView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseUpdateView`
- [ ] **Inheritance**: تغییر از `EditLockProtectedMixin, InventoryBaseView, UpdateView` به `InventoryBaseView, BaseUpdateView` (BaseUpdateView خودش EditLockProtectedMixin دارد)
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**: مشابه CreateView

---

#### کلاس: `ItemTypeDetailView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseDetailView`
- [ ] **Inheritance**: تغییر از `InventoryBaseView, DetailView` به `InventoryBaseView, BaseDetailView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق تکراری (اگر وجود دارد)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**: model, feature_code

---

#### کلاس: `ItemTypeDeleteView`

**تغییرات**:
- [ ] **Import**: اضافه کردن `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر از `InventoryBaseView, DeleteView` به `InventoryBaseView, BaseDeleteView`
- [ ] **حذف متد `delete()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**: model, success_url, feature_code, success_message

---

**نکته**: همین الگو برای سایر کلاس‌های این فایل اعمال می‌شود:
- `ItemCategoryListView`, `ItemCategoryCreateView`, `ItemCategoryUpdateView`, `ItemCategoryDetailView`, `ItemCategoryDeleteView`
- `ItemSubcategoryListView`, `ItemSubcategoryCreateView`, `ItemSubcategoryUpdateView`, `ItemSubcategoryDetailView`, `ItemSubcategoryDeleteView`
- `ItemListView`, `ItemCreateView`, `ItemUpdateView`, `ItemDetailView`, `ItemDeleteView` (این از `ItemUnitFormsetMixin` استفاده می‌کند)
- `WarehouseListView`, `WarehouseCreateView`, `WarehouseUpdateView`, `WarehouseDetailView`, `WarehouseDeleteView`
- `SupplierListView`, `SupplierCreateView`, `SupplierUpdateView`, `SupplierDetailView`, `SupplierDeleteView`
- `SupplierCategoryListView`, `SupplierCategoryCreateView`, `SupplierCategoryUpdateView`, `SupplierCategoryDetailView`, `SupplierCategoryDeleteView`

---

### فایل: `inventory/views/receipts.py`

#### کلاس: `ReceiptTemporaryListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentListView`
- [ ] **Inheritance**: تغییر به `BaseDocumentListView`
- [ ] **حذف**: متد `get_queryset()` (حدود 30-40 خط)
- [ ] **حذف**: متد `get_context_data()` (حدود 40-50 خط)
- [ ] **حذف**: متد `_get_stats()` (اگر وجود دارد)
- [ ] **اضافه کردن**: Attributes (prefetch_lines=True, stats_enabled=True)

#### کلاس: `ReceiptTemporaryCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentCreateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentCreateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)
- [ ] **نکته**: این view از `LineFormsetMixin` استفاده می‌کند

#### کلاس: `ReceiptTemporaryUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentUpdateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentUpdateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `ReceiptTemporaryDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر به `BaseDeleteView` (یا استفاده از `DocumentDeleteViewBase` موجود)
- [ ] **حذف**: متد `delete()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `ReceiptPermanentListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentListView`
- [ ] **Inheritance**: تغییر به `BaseDocumentListView`
- [ ] **حذف**: متد `get_queryset()` (حدود 30-40 خط)
- [ ] **حذف**: متد `get_context_data()` (حدود 40-50 خط)
- [ ] **حذف**: متد `_get_stats()` (اگر وجود دارد)
- [ ] **اضافه کردن**: Attributes (prefetch_lines=True, stats_enabled=True)

#### کلاس: `ReceiptPermanentCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentCreateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentCreateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `ReceiptPermanentUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentUpdateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentUpdateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `ReceiptPermanentDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر به `BaseDeleteView`
- [ ] **حذف**: متد `delete()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `ReceiptConsignmentListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentListView`
- [ ] **Inheritance**: تغییر به `BaseDocumentListView`
- [ ] **حذف**: متد `get_queryset()` (حدود 30-40 خط)
- [ ] **حذف**: متد `get_context_data()` (حدود 40-50 خط)
- [ ] **حذف**: متد `_get_stats()` (اگر وجود دارد)
- [ ] **اضافه کردن**: Attributes (prefetch_lines=True, stats_enabled=True)

#### کلاس: `ReceiptConsignmentCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentCreateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentCreateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `ReceiptConsignmentUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentUpdateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentUpdateView`
- [ ] **حذف**: متد `form_valid()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

#### کلاس: `ReceiptConsignmentDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر به `BaseDeleteView`
- [ ] **حذف**: متد `delete()` (منطق تکراری)
- [ ] **حذف**: متد `get_context_data()` (منطق تکراری)

---

### فایل: `inventory/views/issues.py`

#### کلاس: `IssuePermanentListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentListView`
- [ ] **Inheritance**: تغییر از `InventoryBaseView, ListView` به `InventoryBaseView, BaseDocumentListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch و permission filtering (حدود 35 خط)
- [ ] **حذف متد `_get_stats()`**: حذف stats calculation (حدود 15 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 50 خط)
- [ ] **اضافه کردن Attributes**: model, feature_code, prefetch_lines=True, stats_enabled=True
- [ ] **اضافه کردن Hook Method**: `get_prefetch_related()` برای lines

#### کلاس: `IssuePermanentCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentCreateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentCreateView` (LineFormsetMixin در BaseDocumentCreateView موجود است)
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری formset handling
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `IssuePermanentUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentUpdateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentUpdateView` (EditLockProtectedMixin و DocumentLockProtectedMixin در BaseDocumentUpdateView موجود است)
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `IssuePermanentDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر از `DocumentDeleteViewBase` به `BaseDeleteView` (یا بهبود DocumentDeleteViewBase)
- [ ] **حذف متد `delete()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس‌های دیگر در این فایل:

**نکته**: همین الگو برای کلاس‌های زیر نیز اعمال می‌شود:
- `IssueConsumptionListView`, `IssueConsumptionCreateView`, `IssueConsumptionUpdateView`, `IssueConsumptionDeleteView`
- `IssueConsignmentListView`, `IssueConsignmentCreateView`, `IssueConsignmentUpdateView`, `IssueConsignmentDeleteView`
- `IssueWarehouseTransferListView`, `IssueWarehouseTransferCreateView`, `IssueWarehouseTransferUpdateView`

**کلاس‌های خاص** (نیاز به بررسی جداگانه):
- `IssuePermanentDetailView`, `IssueConsumptionDetailView`, `IssueConsignmentDetailView`, `IssueWarehouseTransferDetailView` → `BaseDetailView`
- `IssuePermanentLockView`, `IssueConsumptionLockView`, `IssueConsignmentLockView` → احتمالاً بدون تغییر یا نیاز به BaseLockView
- `IssueLineSerialAssignmentBaseView` و کلاس‌های مرتبط → نیاز به بررسی خاص

---

### فایل: `inventory/views/requests.py`

#### کلاس: `PurchaseRequestListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentListView`
- [ ] **Inheritance**: تغییر به `BaseDocumentListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch و filtering (حدود 30-40 خط)
- [ ] **حذف متد `_get_stats()`**: حذف stats calculation (اگر وجود دارد)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40-50 خط)
- [ ] **اضافه کردن Attributes**: model, feature_code, prefetch_lines=True, stats_enabled=True

#### کلاس: `PurchaseRequestCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentCreateView`
- [ ] **Inheritance**: تغییر به `BaseDocumentCreateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

**نکته**: همین الگو برای `PurchaseRequestUpdateView`, `PurchaseRequestDeleteView`, `PurchaseRequestDetailView` و `WarehouseRequestListView`, `WarehouseRequestCreateView`, `WarehouseRequestUpdateView`, `WarehouseRequestDeleteView`, `WarehouseRequestDetailView` اعمال می‌شود.

---

### فایل: `inventory/views/stocktaking.py`

#### کلاس: `StocktakingDeficitListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDocumentListView`
- [ ] **Inheritance**: تغییر به `BaseDocumentListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch (حدود 30 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40 خط)
- [ ] **اضافه کردن Attributes**: model, feature_code, prefetch_lines=True

**نکته**: همین الگو برای `StocktakingDeficitCreateView`, `StocktakingDeficitUpdateView`, `StocktakingDeficitDeleteView`, `StocktakingDeficitDetailView` و همچنین برای `StocktakingSurplus*` و `StocktakingRecord*` views اعمال می‌شود.

---

### فایل: `inventory/views/item_import.py`

**تغییرات**:
- [ ] بررسی viewهای این فایل - احتمالاً Import viewها هستند و نیاز به migration خاص دارند
- [ ] اگر ListView/FormView دارند، باید به Base classes migrate شوند

---

### فایل: `inventory/views/balance.py`

**تغییرات**:
- [ ] بررسی viewهای این فایل - احتمالاً Balance calculation viewها هستند
- [ ] ممکن است viewهای خاصی باشند که نیاز به migration ندارند یا نیاز به Base classes خاص دارند

---

### فایل: `inventory/views/api.py`

**تغییرات**:
- [ ] این فایل شامل API endpoints است
- [ ] باید از `BaseAPIView` در `shared/views/api.py` استفاده کند
- [ ] بررسی کلاس‌های موجود و migrate به Base API classes

---

### فایل: `inventory/views/create_issue_from_warehouse_request.py`

**تغییرات**:
- [ ] بررسی viewهای این فایل
- [ ] احتمالاً workflow view هستند که نیاز به migration خاص دارند

---

### فایل: `inventory/views/issues_from_warehouse_request.py`

**تغییرات**:
- [ ] بررسی viewهای این فایل
- [ ] احتمالاً workflow view هستند که نیاز به migration خاص دارند

---

## ماژول ۳: `production`

### فایل: `production/views/personnel.py`

#### کلاس: `PersonListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, ListView` به `FeaturePermissionRequiredMixin, BaseListView`
- [ ] **حذف متد `get_queryset()`**: 
  ```python
  # حذف این بخش (حدود 30-40 خط):
  def get_queryset(self):
      active_company_id = self.request.session.get('active_company_id')
      if not active_company_id:
          return models.Person.objects.none()
      
      queryset = models.Person.objects.filter(company_id=active_company_id)
      # ... search filter ...
      # ... status filter ...
      return queryset.order_by(...)
  ```
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40-50 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code

#### کلاس: `PersonCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView`
- [ ] **حذف متد `get_form_kwargs()`**: 
  ```python
  # حذف این بخش:
  def get_form_kwargs(self):
      kwargs = super().get_form_kwargs()
      kwargs['company_id'] = self.request.session.get('active_company_id')
      return kwargs
  ```
- [ ] **حذف متد `form_valid()`**: 
  ```python
  # حذف این بخش:
  def form_valid(self, form):
      active_company_id = self.request.session.get('active_company_id')
      if not active_company_id:
          messages.error(...)
          return self.form_invalid(form)
      
      form.instance.company_id = active_company_id
      form.instance.created_by = self.request.user
      messages.success(...)
      return super().form_valid(form)
  ```
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**: model, form_class, success_url, feature_code, success_message

**نکته**: همین الگو برای `PersonUpdateView`, `PersonDetailView`, `PersonDeleteView` اعمال می‌شود.

---

### فایل: `production/views/machine.py`

#### کلاس: `MachineListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, ListView` به `FeaturePermissionRequiredMixin, BaseListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق filtering (حدود 30-40 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40-50 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code

#### کلاس: `MachineCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView`
- [ ] **حذف متد `get_form_kwargs()`**: حذف منطق تکراری
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**: model, form_class, success_url, feature_code, success_message

**نکته**: همین الگو برای `MachineUpdateView`, `MachineDetailView`, `MachineDeleteView` اعمال می‌شود.

---

### فایل: `production/views/work_line.py`

#### کلاس: `WorkLineListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, ListView` به `FeaturePermissionRequiredMixin, BaseListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق filtering (حدود 30-40 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40-50 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code

#### کلاس: `WorkLineCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView`
- [ ] **حذف متد `get_form_kwargs()`**: حذف منطق تکراری
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**: model, form_class, success_url, feature_code, success_message

**نکته**: همین الگو برای `WorkLineUpdateView`, `WorkLineDetailView`, `WorkLineDeleteView` اعمال می‌شود.

---

### فایل: `production/views/bom.py`

#### کلاس: `BOMListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, ListView` به `FeaturePermissionRequiredMixin, BaseListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch و filtering (حدود 30-40 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40-50 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code

#### کلاس: `BOMCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetCreateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetCreateView`
- [ ] **حذف**: متد `get_context_data()` (منطق formset)
- [ ] **حذف**: متد `form_valid()` (منطق formset)
- [ ] **اضافه کردن**: Attributes (formset_class)

#### کلاس: `BOMUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetUpdateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetUpdateView`
- [ ] **حذف**: متد `get_context_data()` (منطق formset)
- [ ] **حذف**: متد `form_valid()` (منطق formset)

#### کلاس: `BOMDetailView`

**تغییرات**: مشابه سایر DetailViewها

---

### فایل: `production/views/process.py`

#### کلاس: `ProcessListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر به `BaseListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch (حدود 30 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code

#### کلاس: `ProcessCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetCreateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetCreateView`
- [ ] **حذف متد `get_context_data()`**: حذف منطق formset handling
- [ ] **حذف متد `form_valid()`**: حذف منطق formset handling
- [ ] **اضافه کردن Attributes**: formset_class

**نکته**: همین الگو برای `ProcessUpdateView`, `ProcessDetailView` اعمال می‌شود.

---

### فایل: `production/views/product_order.py`

#### کلاس: `ProductOrderListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر به `BaseListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch و filtering (حدود 40 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code

#### کلاس: `ProductOrderCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری (اما منطق پیچیده auto-generate order_code باید حفظ شود)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **نکته**: این view منطق پیچیده‌ای دارد (auto-generate order_code، ایجاد TransferToLine) که باید حفظ شود

#### کلاس: `ProductOrderUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseUpdateView`
- [ ] **Inheritance**: تغییر به `BaseUpdateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `ProductOrderDetailView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDetailView`
- [ ] **Inheritance**: تغییر به `BaseDetailView`
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

---

### فایل: `production/views/transfer_to_line.py`

#### کلاس: `TransferToLineListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, ListView` به `FeaturePermissionRequiredMixin, BaseListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch و filtering (حدود 50 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 40 خط)
- [ ] **اضافه کردن Attributes**: model, feature_code, search_fields, filter_fields

#### کلاس: `TransferToLineCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetCreateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetCreateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق formset handling
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `TransferToLineUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetUpdateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetUpdateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `TransferToLineDetailView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDetailView`
- [ ] **Inheritance**: تغییر به `BaseDetailView`
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `TransferToLineDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر به `BaseDeleteView`
- [ ] **حذف متد `delete()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### Approval Workflow Views (نیاز به بررسی خاص):

**کلاس: `TransferToLineApproveView`**
- [ ] این view از نوع `View` است و منطق approve دارد
- [ ] بررسی نیاز به BaseApprovalView یا حفظ به صورت فعلی

**کلاس: `TransferToLineRejectView`**
- [ ] این view از نوع `View` است و منطق reject دارد
- [ ] بررسی نیاز به BaseRejectionView یا حفظ به صورت فعلی

**کلاس‌های دیگر**: `TransferToLineQCApproveView`, `TransferToLineQCRejectView`, `TransferToLineCreateWarehouseTransferView`, `TransferToLineUnlockView`
- [ ] این viewها workflow views هستند
- [ ] بررسی نیاز به Base classes یا حفظ به صورت فعلی

---

### فایل: `production/views/performance_record.py`

#### کلاس: `PerformanceRecordListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, ListView` به `FeaturePermissionRequiredMixin, BaseListView`
- [ ] **حذف متد `get_queryset()`**: حذف منطق prefetch و permission filtering (حدود 60 خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 50 خط)
- [ ] **اضافه کردن Attributes**: model, feature_code, permission_field='created_by'

#### کلاس: `PerformanceRecordCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetCreateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetCreateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق formset handling (بسیار پیچیده - حدود 400+ خط)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **نکته**: این view بسیار پیچیده است و ممکن است نیاز به بررسی خاص داشته باشد

#### کلاس: `PerformanceRecordUpdateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetUpdateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetUpdateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `PerformanceRecordDetailView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDetailView`
- [ ] **Inheritance**: تغییر به `BaseDetailView`
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `PerformanceRecordDeleteView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseDeleteView`
- [ ] **Inheritance**: تغییر به `BaseDeleteView`
- [ ] **حذف متد `delete()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### Approval Workflow Views (نیاز به بررسی خاص):

**کلاس: `PerformanceRecordApproveView`**
- [ ] این view از نوع `View` است و منطق approve دارد
- [ ] بررسی نیاز به BaseApprovalView یا حفظ به صورت فعلی

**کلاس: `PerformanceRecordRejectView`**
- [ ] این view از نوع `View` است و منطق reject دارد
- [ ] بررسی نیاز به BaseRejectionView یا حفظ به صورت فعلی

**کلاس: `PerformanceRecordCreateReceiptView`**
- [ ] این view workflow view است
- [ ] بررسی نیاز به Base class یا حفظ به صورت فعلی

**کلاس: `PerformanceRecordGetOperationsView`**
- [ ] این view احتمالاً API endpoint است
- [ ] بررسی نیاز به BaseAPIView یا حفظ به صورت فعلی

---

### فایل: `production/views/rework.py`

**تغییرات**:
- [ ] بررسی viewهای این فایل
- [ ] احتمالاً مشابه سایر document views هستند
- [ ] استفاده از `BaseDocumentListView`, `BaseDocumentCreateView`, `BaseDocumentUpdateView`, `BaseDeleteView`

---

### فایل: `production/views/qc_operations.py`

**تغییرات**:
- [ ] بررسی viewهای این فایل
- [ ] احتمالاً Approval workflow views هستند
- [ ] بررسی نیاز به Base classes یا حفظ به صورت فعلی

---

### فایل: `production/views/api.py`

**تغییرات**:
- [ ] این فایل شامل API endpoints است
- [ ] باید از `BaseAPIView` در `shared/views/api.py` استفاده کند
- [ ] بررسی کلاس‌های موجود و migrate به Base API classes

---

### فایل: `production/views/placeholders.py`

**تغییرات**:
- [ ] این فایل احتمالاً placeholder views دارد
- [ ] بررسی نیاز به migration - ممکن است نیازی نباشد

---

## ماژول ۴: `accounting`

### فایل: `accounting/views/accounts.py`

#### کلاس: `AccountListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, AccountingBaseView, ListView` به `FeaturePermissionRequiredMixin, AccountingBaseView, BaseListView`
- [ ] **حذف متد `get_queryset()`**: 
  ```python
  # حذف این بخش (حدود 40-50 خط):
  def get_queryset(self):
      queryset = super().get_queryset()
      queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
      
      search = self.request.GET.get('search', '').strip()
      status = self.request.GET.get('status', '')
      # ... filters ...
      return queryset.order_by(...)
  ```
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 50-60 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code, default_status_filter, default_order_by

#### کلاس: `AccountCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView`
- [ ] **حذف متد `get_form_kwargs()`**: 
  ```python
  # حذف این بخش:
  def get_form_kwargs(self):
      kwargs = super().get_form_kwargs()
      kwargs['company_id'] = self.request.session.get('active_company_id')
      return kwargs
  ```
- [ ] **حذف متد `form_valid()`**: 
  ```python
  # حذف این بخش:
  def form_valid(self, form):
      form.instance.created_by = self.request.user
      messages.success(...)
      return super().form_valid(form)
  ```
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری
- [ ] **اضافه کردن Attributes**: model, form_class, success_url, feature_code, success_message

**نکته**: همین الگو برای `AccountUpdateView`, `AccountDetailView`, `AccountDeleteView` اعمال می‌شود.

---

### فایل: `accounting/views/tafsili_accounts.py`

**کلاس‌ها**: مشابه `accounts.py` - استفاده از Base classes

---

### فایل: `accounting/views/sub_accounts.py`

**کلاس‌ها**: مشابه `accounts.py` - استفاده از Base classes

---

### فایل: `accounting/views/gl_accounts.py`

**کلاس‌ها**: مشابه `accounts.py` - استفاده از Base classes

---

### فایل: `accounting/views/fiscal_years.py`

**کلاس‌ها**: مشابه `accounts.py` - استفاده از Base classes

---

### فایل: `accounting/views/tafsili_hierarchy.py`

**کلاس‌ها**: مشابه `accounts.py` - استفاده از Base classes

---

## ماژول ۵: `ticketing`

### فایل: `ticketing/views/categories.py`

#### کلاس: `TicketCategoryListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, TicketingBaseView, ListView` به `FeaturePermissionRequiredMixin, TicketingBaseView, BaseListView`
- [ ] **حذف متد `get_queryset()`**: 
  ```python
  # حذف این بخش (حدود 20-30 خط):
  def get_queryset(self):
      """Filter categories by company and search."""
      company_id = self.request.session.get("active_company_id")
      queryset = models.TicketCategory.objects.filter(company_id=company_id)
      
      search = self.request.GET.get("search", "")
      if search:
          queryset = queryset.filter(
              Q(name__icontains=search) |
              Q(name_en__icontains=search) |
              Q(public_code__icontains=search)
          )
      
      # Filter by parent (main categories vs subcategories)
      parent_filter = self.request.GET.get("parent_filter", "")
      if parent_filter == "main":
          queryset = queryset.filter(parent_category__isnull=True)
      elif parent_filter == "sub":
          queryset = queryset.filter(parent_category__isnull=False)
      
      return queryset.order_by("sort_order", "public_code", "name")
  ```
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (حدود 30-40 خط)
- [ ] **اضافه کردن Attributes**: model, search_fields, filter_fields, feature_code
- [ ] **اضافه کردن Hook Method**: `apply_custom_filters()` برای parent_filter

#### کلاس: `TicketCategoryCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseFormsetCreateView`
- [ ] **Inheritance**: تغییر به `BaseFormsetCreateView` (چون از formset استفاده می‌کند)
- [ ] **حذف متد `get_form_kwargs()`**: حذف منطق تکراری
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری (اما باید منطق formset را حفظ کند)
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری (اما باید formset را اضافه کند)

**نکته**: همین الگو برای `TicketCategoryUpdateView`, `TicketCategoryDetailView`, `TicketCategoryDeleteView` اعمال می‌شود.

---

### فایل: `ticketing/views/subcategories.py`

**کلاس‌ها**: مشابه `categories.py` - استفاده از Base classes

---

### فایل: `ticketing/views/templates.py`

**کلاس‌ها**: مشابه `categories.py` - استفاده از Base classes (اما formset پیچیده‌تری دارد)

---

### فایل: `ticketing/views/tickets.py`

#### کلاس: `TicketListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `TicketingBaseView, ListView` به `TicketingBaseView, BaseListView`
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

#### کلاس: `TicketCreateView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseCreateView`
- [ ] **Inheritance**: تغییر به `BaseCreateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: اما باید منطق template selection را حفظ کند

#### کلاس: `TicketEditView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseUpdateView`
- [ ] **Inheritance**: تغییر به `BaseUpdateView`
- [ ] **حذف متد `form_valid()`**: حذف منطق تکراری
- [ ] **حذف متد `get_context_data()`**: حذف منطق تکراری

---

### فایل: `ticketing/views/entity_reference.py`

**تغییرات**:
- [ ] این فایل احتمالاً API endpoints دارد
- [ ] بررسی کلاس‌های موجود
- [ ] اگر API endpoints هستند، باید از `BaseAPIView` استفاده کنند
- [ ] یا ممکن است viewهای خاصی باشند که نیاز به migration ندارند

---

### فایل: `ticketing/views/placeholders.py`

**تغییرات**:
- [ ] این فایل احتمالاً placeholder views دارد
- [ ] بررسی نیاز به migration - ممکن است نیازی نباشد

---

### فایل: `ticketing/views/debug.py`

**تغییرات**:
- [ ] این فایل احتمالاً debug views دارد
- [ ] بررسی نیاز به migration - ممکن است نیازی نباشد یا فقط در development استفاده شوند

---

## ماژول ۶: `qc`

### فایل: `qc/views/inspections.py`

#### کلاس: `TemporaryReceiptQCListView`

**تغییرات**:
- [ ] **Import**: `from shared.views.base import BaseListView`
- [ ] **Inheritance**: تغییر از `FeaturePermissionRequiredMixin, QCBaseView, ListView` به `FeaturePermissionRequiredMixin, QCBaseView, BaseListView`
- [ ] **حذف متد `get_queryset()`**: 
  ```python
  # حذف این بخش (حدود 20-30 خط):
  def get_queryset(self):
      """Show all receipts (awaiting, approved, rejected)."""
      queryset = super().get_queryset()
      queryset = queryset.filter(
          is_enabled=1
      ).select_related('supplier', 'created_by', 'qc_approved_by').prefetch_related(
          'lines__item', 
          'lines__warehouse'
      )
      queryset = queryset.order_by(
          'status',
          '-document_date',
          'document_code'
      )
      return queryset
  ```
- [ ] **حذف متد `get_context_data()`**: 
  ```python
  # حذف این بخش (حدود 30-40 خط):
  def get_context_data(self, **kwargs) -> Dict[str, Any]:
      context = super().get_context_data(**kwargs)
      context['page_title'] = _('Temporary Receipts - QC Inspection')
      context['breadcrumbs'] = [...]
      # ... stats calculation ...
      return context
  ```
- [ ] **اضافه کردن Attributes**: model, feature_code
- [ ] **اضافه کردن Hook Method**: `get_stats()` برای stats calculation
- [ ] **اضافه کردن Hook Method**: `get_prefetch_related()` برای prefetch lines

---

## خلاصه تغییرات

### الگوی کلی تغییرات برای هر View

#### ListView

**قبل**:
```python
class ItemTypeListView(InventoryBaseView, ListView):
    def get_queryset(self):
        # 30-40 خط کد تکراری
        pass
    
    def get_context_data(self, **kwargs):
        # 40-50 خط کد تکراری
        pass
```

**بعد**:
```python
from shared.views.base import BaseListView

class ItemTypeListView(InventoryBaseView, BaseListView):
    model = models.ItemType
    search_fields = ['name', 'public_code']
    filter_fields = ['is_enabled']
    feature_code = 'inventory.master.item_types'
    
    def get_breadcrumbs(self):
        return [...]
```

**حذف شده**: ~70-90 خط کد
**اضافه شده**: ~10-15 خط کد

---

#### CreateView

**قبل**:
```python
class ItemTypeCreateView(InventoryBaseView, CreateView):
    def form_valid(self, form):
        # 5-10 خط کد تکراری
        pass
    
    def get_context_data(self, **kwargs):
        # 15-20 خط کد تکراری
        pass
```

**بعد**:
```python
from shared.views.base import BaseCreateView

class ItemTypeCreateView(InventoryBaseView, BaseCreateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item Type created successfully.')
    
    def get_breadcrumbs(self):
        return [...]
```

**حذف شده**: ~20-30 خط کد
**اضافه شده**: ~10-15 خط کد

---

#### UpdateView

**قبل**:
```python
class ItemTypeUpdateView(EditLockProtectedMixin, InventoryBaseView, UpdateView):
    def form_valid(self, form):
        # 5-10 خط کد تکراری
        pass
    
    def get_context_data(self, **kwargs):
        # 15-20 خط کد تکراری
        pass
```

**بعد**:
```python
from shared.views.base import BaseUpdateView

class ItemTypeUpdateView(InventoryBaseView, BaseUpdateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item Type updated successfully.')
    
    def get_breadcrumbs(self):
        return [...]
```

**حذف شده**: ~20-30 خط کد
**اضافه شده**: ~10-15 خط کد

---

#### DeleteView

**قبل**:
```python
class ItemTypeDeleteView(InventoryBaseView, DeleteView):
    def delete(self, request, *args, **kwargs):
        # 5 خط کد تکراری
        pass
    
    def get_context_data(self, **kwargs):
        # 20-25 خط کد تکراری
        pass
```

**بعد**:
```python
from shared.views.base import BaseDeleteView

class ItemTypeDeleteView(InventoryBaseView, BaseDeleteView):
    model = models.ItemType
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item Type deleted successfully.')
    
    def get_breadcrumbs(self):
        return [...]
    
    def get_object_details(self):
        return [
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
        ]
```

**حذف شده**: ~25-30 خط کد
**اضافه شده**: ~15-20 خط کد

---

#### DetailView

**قبل**:
```python
class ItemTypeDetailView(InventoryBaseView, DetailView):
    def get_queryset(self):
        # 5-10 خط کد تکراری
        pass
    
    def get_context_data(self, **kwargs):
        # 20-25 خط کد تکراری
        pass
```

**بعد**:
```python
from shared.views.base import BaseDetailView

class ItemTypeDetailView(InventoryBaseView, BaseDetailView):
    model = models.ItemType
    feature_code = 'inventory.master.item_types'
    
    def get_breadcrumbs(self):
        return [...]
```

**حذف شده**: ~25-35 خط کد
**اضافه شده**: ~5-10 خط کد

---

## آمار کلی Migration

### تعداد فایل‌های باید تغییر کنند

| ماژول | تعداد فایل View | تعداد کلاس View | تخمین خط کد حذف شده |
|-------|----------------|-----------------|---------------------|
| `shared` | 7 | 25+ | ~1,875 خط |
| `inventory` | 6 | 81+ | ~5,670 خط |
| `production` | 12 | 41+ | ~2,870 خط |
| `accounting` | 8 | 28+ | ~1,960 خط |
| `ticketing` | 4 | 19+ | ~1,330 خط |
| `qc` | 1 | 6+ | ~420 خط |
| **مجموع** | **38** | **200+** | **~14,125 خط** |

### تعداد خط کد اضافه شده (Attributes و Hook Methods)

| ماژول | تعداد کلاس | تخمین خط کد اضافه شده |
|-------|-----------|---------------------|
| `shared` | 25+ | ~375 خط |
| `inventory` | 81+ | ~1,215 خط |
| `production` | 41+ | ~615 خط |
| `accounting` | 28+ | ~420 خط |
| `ticketing` | 19+ | ~285 خط |
| `qc` | 6+ | ~90 خط |
| **مجموع** | **200+** | **~3,000 خط** |

### صرفه‌جویی خالص

- **قبل**: ~14,125 خط کد تکراری
- **بعد**: ~3,000 خط کد (فقط Attributes و Hook Methods)
- **صرفه‌جویی**: **~11,125 خط کد** (79% کاهش)

---

## چک‌لیست Migration به تفکیک ماژول

### ماژول `shared` (Pilot)

- [ ] `shared/views/companies.py` - 5 کلاس
- [ ] `shared/views/users.py` - 5 کلاس
- [ ] `shared/views/access_levels.py` - 5 کلاس
- [ ] `shared/views/groups.py` - 5 کلاس
- [ ] `shared/views/company_units.py` - 5 کلاس
- [ ] `shared/views/smtp_server.py` - 4 کلاس
- [ ] `shared/views/notifications.py` - 1 کلاس

**مجموع**: 30 کلاس

---

### ماژول `inventory`

- [ ] `inventory/views/master_data.py` - 27 کلاس
- [ ] `inventory/views/receipts.py` - 12 کلاس
- [ ] `inventory/views/issues.py` - 10 کلاس
- [ ] `inventory/views/requests.py` - 6 کلاس
- [ ] `inventory/views/stocktaking.py` - 9 کلاس
- [ ] `inventory/views/issues_from_warehouse_request.py` - چندین کلاس

**مجموع**: 64+ کلاس

---

### ماژول `production`

- [ ] `production/views/personnel.py` - 5 کلاس
- [ ] `production/views/machine.py` - 5 کلاس
- [ ] `production/views/work_line.py` - 5 کلاس
- [ ] `production/views/bom.py` - 4 کلاس
- [ ] `production/views/process.py` - 4 کلاس
- [ ] `production/views/product_order.py` - 4 کلاس
- [ ] `production/views/transfer_to_line.py` - 11 کلاس (شامل Approval workflow views)
- [ ] `production/views/performance_record.py` - 9 کلاس (شامل Approval workflow views)
- [ ] `production/views/rework.py` - 4 کلاس
- [ ] `production/views/qc_operations.py` - 3 کلاس
- [ ] `production/views/api.py` - API endpoints
- [ ] `production/views/placeholders.py` - بررسی نیاز به migration

**مجموع**: 47+ کلاس + Approval workflow views + API endpoints

---

### ماژول `accounting`

- [ ] `accounting/views/accounts.py` - 5 کلاس
- [ ] `accounting/views/tafsili_accounts.py` - 5 کلاس
- [ ] `accounting/views/sub_accounts.py` - 5 کلاس
- [ ] `accounting/views/gl_accounts.py` - 5 کلاس
- [ ] `accounting/views/fiscal_years.py` - 5 کلاس
- [ ] `accounting/views/tafsili_hierarchy.py` - 5 کلاس
- [ ] `accounting/views/document_attachments.py` - 3 کلاس

**مجموع**: 33+ کلاس

---

### ماژول `ticketing`

- [ ] `ticketing/views/categories.py` - 5 کلاس
- [ ] `ticketing/views/subcategories.py` - 5 کلاس
- [ ] `ticketing/views/templates.py` - 5 کلاس
- [ ] `ticketing/views/tickets.py` - 4 کلاس
- [ ] `ticketing/views/entity_reference.py` - بررسی viewها (احتمالاً API endpoints)
- [ ] `ticketing/views/placeholders.py` - بررسی نیاز به migration
- [ ] `ticketing/views/debug.py` - بررسی نیاز به migration

**مجموع**: 19+ کلاس + فایل‌های اضافی

---

### ماژول `qc`

- [ ] `qc/views/inspections.py` - 6+ کلاس

**مجموع**: 6+ کلاس

---

## نکات مهم Migration

### ۱. ترتیب Migration

1. **اول**: ماژول `shared` (Pilot)
2. **دوم**: ماژول `inventory` (بزرگترین)
3. **سوم**: ماژول `production`
4. **چهارم**: ماژول `accounting`
5. **پنجم**: ماژول `ticketing`
6. **ششم**: ماژول `qc`

### ۲. تست بعد از هر Migration

- [ ] تست Unit Tests
- [ ] تست Integration Tests
- [ ] تست Manual (UI/UX)
- [ ] بررسی Performance

### ۳. Rollback Plan

- [ ] نگه داشتن backup از فایل‌های قدیمی
- [ ] استفاده از Git branches
- [ ] امکان rollback سریع

---

---

## خلاصه تغییرات انجام شده در این فایل

### تغییرات اضافه شده:

1. **تکمیل جزئیات برای `inventory/views/issues.py`**:
   - اضافه کردن جزئیات کامل برای تمام 28 کلاس view موجود
   - تفکیک بین Document Views و Workflow Views
   - مشخص کردن نیاز به بررسی خاص برای Lock Views و Serial Assignment Views

2. **تکمیل جزئیات برای `inventory/views/requests.py` و `stocktaking.py`**:
   - اضافه کردن جزئیات کامل برای PurchaseRequest و WarehouseRequest views
   - اضافه کردن جزئیات برای Stocktaking views

3. **افزودن فایل‌های Missing در `inventory`**:
   - `item_import.py`
   - `balance.py`
   - `api.py`
   - `create_issue_from_warehouse_request.py`
   - `issues_from_warehouse_request.py`

4. **تکمیل جزئیات برای `production/views`**:
   - جزئیات کامل برای `personnel.py`, `machine.py`, `work_line.py`
   - جزئیات کامل برای `bom.py`, `process.py`, `product_order.py`
   - جزئیات کامل برای `transfer_to_line.py` (شامل Approval workflow views)
   - جزئیات کامل برای `performance_record.py` (شامل Approval workflow views)
   - اضافه کردن فایل‌های `rework.py`, `qc_operations.py`, `api.py`, `placeholders.py`

5. **افزودن Approval Workflow Views**:
   - `TransferToLineApproveView`, `TransferToLineRejectView`, `TransferToLineQCApproveView`, `TransferToLineQCRejectView`
   - `PerformanceRecordApproveView`, `PerformanceRecordRejectView`, `PerformanceRecordCreateReceiptView`
   - مشخص کردن نیاز به بررسی خاص برای این viewها

6. **افزودن فایل‌های Missing در `ticketing`**:
   - `entity_reference.py`
   - `placeholders.py`
   - `debug.py`

7. **به‌روزرسانی چک‌لیست Migration**:
   - اضافه کردن فایل‌های جدید به آمار کلی
   - مشخص کردن Approval workflow views در آمار

### موارد باقی‌مانده که نیاز به بررسی دقیق‌تر دارند:

1. **Receipt Views**: جزئیات کامل فقط برای یک نمونه (`ReceiptTemporaryListView`) آمده است. باید برای `ReceiptPermanent` و `ReceiptConsignment` نیز تکمیل شود.

2. **Approval Workflow Views**: این viewها از نوع `View` هستند و نیاز به بررسی دارند که آیا باید Base classes خاص داشته باشند یا نه.

3. **API Endpoints**: فایل‌های `api.py` در ماژول‌ها نیاز به بررسی دقیق‌تر برای استفاده از `BaseAPIView` دارند.

4. **Lock/Unlock Views**: این viewها خاص هستند و نیاز به بررسی دارند که آیا باید Base classes داشته باشند یا نه.

5. **Serial Assignment Views**: این viewها خاص هستند و نیاز به بررسی دارند.

---

**تاریخ ایجاد**: 2024  
**آخرین به‌روزرسانی**: 2024  
**وضعیت**: تکمیل شده با جزئیات کامل - آماده برای Migration

