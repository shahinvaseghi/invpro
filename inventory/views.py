"""
Views for the inventory module.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, View, FormView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import date
from typing import Set
import json
from django.utils.safestring import mark_safe
from django.db.models import Q
from . import models
from . import inventory_balance
from . import forms
from .services import serials as serial_service
from shared.models import Person
from shared.mixins import FeaturePermissionRequiredMixin
from decimal import Decimal, InvalidOperation


class InventoryBaseView(LoginRequiredMixin):
    """Base view with common context for inventory module."""
    login_url = '/admin/login/'
    
    def get_queryset(self):
        """Filter queryset by active company."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(queryset.model, 'company'):
            queryset = queryset.filter(company_id=company_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        return context


class DocumentLockProtectedMixin:
    """Prevent modifying locked inventory documents."""

    lock_redirect_url_name = ''
    lock_error_message = _('سند قفل شده و قابل ویرایش یا حذف نیست.')
    owner_field = 'created_by'
    owner_error_message = _('فقط ایجاد کننده می‌تواند این سند را ویرایش کند.')
    protected_methods = ('get', 'post', 'put', 'patch', 'delete')

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.protected_methods:
            obj = self.get_object()
            self.object = obj
            if getattr(obj, 'is_locked', 0):
                messages.error(request, self.lock_error_message)
                return HttpResponseRedirect(self._get_lock_redirect_url())
            if self.owner_field:
                owner = getattr(obj, self.owner_field, None)
                owner_id = getattr(owner, 'id', None)
                if owner_id and owner_id != request.user.id:
                    messages.error(request, self.owner_error_message)
                    return HttpResponseRedirect(self._get_lock_redirect_url())
        return super().dispatch(request, *args, **kwargs)

    def _get_lock_redirect_url(self):
        if self.lock_redirect_url_name:
            return reverse(self.lock_redirect_url_name)
        if hasattr(self, 'list_url_name') and getattr(self, 'list_url_name'):
            return reverse(self.list_url_name)
        return reverse('inventory:inventory_balance')


class DocumentLockView(LoginRequiredMixin, View):
    """Generic view to lock inventory documents."""

    model = None
    success_url_name = ''
    success_message = _('سند با موفقیت قفل شد و دیگر قابل ویرایش نیست.')
    already_locked_message = _('این سند قبلاً قفل شده است.')
    lock_field = 'is_locked'

    def after_lock(self, obj, request):
        """Hook for subclasses to perform extra actions after locking."""
        return None

    def before_lock(self, obj, request):
        """Hook executed before locking. Return False to cancel lock."""
        return True

    def post(self, request, *args, **kwargs):
        if self.model is None or not self.success_url_name:
            messages.error(request, _('پیکربندی قفل سند نامعتبر است.'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        queryset = self.model.objects.all()
        company_id = request.session.get('active_company_id')
        if company_id and hasattr(self.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)

        obj = get_object_or_404(queryset, pk=kwargs.get('pk'))

        if getattr(obj, self.lock_field, 0):
            messages.info(request, self.already_locked_message)
        else:
            if not self.before_lock(obj, request):
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse(self.success_url_name)))

            update_fields = {self.lock_field}
            setattr(obj, self.lock_field, 1)
            if hasattr(obj, 'locked_at'):
                obj.locked_at = timezone.now()
                update_fields.add('locked_at')
            if hasattr(obj, 'locked_by_id'):
                obj.locked_by = request.user
                update_fields.add('locked_by')
            if hasattr(obj, 'edited_by_id'):
                obj.edited_by = request.user
                update_fields.add('edited_by')
            obj.save(update_fields=list(update_fields))
            self.after_lock(obj, request)
            messages.success(request, self.success_message)

        return HttpResponseRedirect(reverse(self.success_url_name))


class LineFormsetMixin:
    """Mixin to handle line formset creation and saving for multi-line documents."""
    
    formset_class = None
    formset_prefix = 'lines'
    
    def build_line_formset(self, data=None, instance=None, company_id=None):
        """Build line formset for the document."""
        if instance is None:
            instance = getattr(self, "object", None)
        if company_id is None:
            if instance and instance.company_id:
                company_id = instance.company_id
            else:
                company_id = self.request.session.get('active_company_id')
        
        if self.formset_class is None:
            raise ValueError("formset_class must be set in view class")
        
        kwargs = {
            'instance': instance,
            'prefix': self.formset_prefix,
            'company_id': company_id,
        }
        if data is not None:
            kwargs['data'] = data
        return self.formset_class(**kwargs)
    
    def get_line_formset(self, data=None):
        """Get line formset for current request."""
        return self.build_line_formset(data=data)
    
    def get_context_data(self, **kwargs):
        """Add line formset to context."""
        context = super().get_context_data(**kwargs)
        if 'lines_formset' not in context:
            if self.request.method == 'POST':
                context['lines_formset'] = self.get_line_formset(data=self.request.POST)
            else:
                context['lines_formset'] = self.get_line_formset()
        return context
    
    def form_invalid(self, form):
        """Handle invalid form with formset."""
        company_id = getattr(form.instance, "company_id", None) or self.request.session.get('active_company_id')
        return self.render_to_response(
            self.get_context_data(
                form=form,
                lines_formset=self.build_line_formset(data=self.request.POST, instance=form.instance, company_id=company_id),
            )
        )
    
    def _save_line_formset(self, formset):
        """Save line formset instances."""
        instances = formset.save(commit=False)
        for line in instances:
            line.company = self.object.company
            line.document = self.object
            if not hasattr(line, 'company_id') or not line.company_id:
                line.company_id = self.object.company_id
            line.save()
        formset.save_m2m()  # Save ManyToMany relationships (serials)
        for obj in formset.deleted_objects:
            obj.delete()


class ItemUnitFormsetMixin:
    """Mixin to handle item unit formset creation and saving."""

    formset_prefix = 'units'

    def build_unit_formset(self, data=None, instance=None, company_id=None):
        if instance is None:
            instance = getattr(self, "object", None) or models.Item()
        if company_id is None:
            if instance and instance.company_id:
                company_id = instance.company_id
            else:
                company_id = self.request.session.get('active_company_id')

        kwargs = {
            'instance': instance,
            'prefix': self.formset_prefix,
            'company_id': company_id,
        }
        if data is not None:
            kwargs['data'] = data
        return forms.ItemUnitFormSet(**kwargs)

    def get_unit_formset(self, data=None):
        return self.build_unit_formset(data=data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'units_formset' not in context:
            if self.request.method == 'POST':
                context['units_formset'] = self.get_unit_formset(data=self.request.POST)
            else:
                context['units_formset'] = self.get_unit_formset()
        return context

    def form_invalid(self, form):
        company_id = getattr(form.instance, "company_id", None) or self.request.session.get('active_company_id')
        return self.render_to_response(
            self.get_context_data(
                form=form,
                units_formset=self.build_unit_formset(data=self.request.POST, instance=form.instance, company_id=company_id),
            )
        )

    def _generate_unit_code(self, company):
        last_code = (
            models.ItemUnit.objects.filter(company=company)
            .order_by("-public_code")
            .values_list("public_code", flat=True)
            .first()
        )
        if last_code and last_code.isdigit():
            return str(int(last_code) + 1).zfill(6)
        return "000001"

    def _save_unit_formset(self, formset):
        instances = formset.save(commit=False)
        for unit in instances:
            if not unit.from_unit or not unit.to_unit:
                continue
            unit.company = self.object.company
            unit.item = self.object
            unit.item_code = self.object.item_code
            if not unit.public_code:
                unit.public_code = self._generate_unit_code(self.object.company)
            unit.save()
        for obj in formset.deleted_objects:
            obj.delete()

    def _sync_item_warehouses(self, item, warehouses, user):
        warehouses = list(warehouses or [])
        selected_ids = {w.id for w in warehouses}
        existing = {iw.warehouse_id: iw for iw in item.warehouses.all()}

        # Delete removed warehouses
        if selected_ids:
            item.warehouses.exclude(warehouse_id__in=selected_ids).delete()
        else:
            item.warehouses.all().delete()

        for idx, warehouse in enumerate(warehouses):
            is_primary = 1 if idx == 0 else 0
            current = existing.get(warehouse.id)
            if current:
                updated = False
                if current.is_primary != is_primary:
                    current.is_primary = is_primary
                    updated = True
                if updated:
                    current.save()
            else:
                item.warehouses.create(
                    company=item.company,
                    warehouse=warehouse,
                    is_primary=is_primary,
                )

    def _get_ordered_warehouses(self, form):
        selected = list(form.cleaned_data.get('allowed_warehouses') or [])
        if not selected:
            return selected
        order_keys = [key for key in self.request.POST.getlist('allowed_warehouses') if key]
        if not order_keys:
            return selected
        mapping = {str(w.id): w for w in selected}
        ordered = []
        for key in order_keys:
            warehouse = mapping.get(key)
            if warehouse and warehouse not in ordered:
                ordered.append(warehouse)
        for warehouse in selected:
            if warehouse not in ordered:
                ordered.append(warehouse)
        return ordered


# Master Data Views
class ItemTypeListView(InventoryBaseView, ListView):
    model = models.ItemType
    template_name = 'inventory/item_types.html'
    context_object_name = 'item_types'
    paginate_by = 50


class ItemCategoryListView(InventoryBaseView, ListView):
    model = models.ItemCategory
    template_name = 'inventory/item_categories.html'
    context_object_name = 'item_categories'
    paginate_by = 50


class ItemListView(InventoryBaseView, ListView):
    model = models.Item
    template_name = 'inventory/items.html'
    context_object_name = 'items'
    paginate_by = 50


class ItemSerialListView(FeaturePermissionRequiredMixin, InventoryBaseView, ListView):
    feature_code = 'inventory.master.item_serials'
    model = models.ItemSerial
    template_name = 'inventory/item_serials.html'
    context_object_name = 'serials'
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('item', 'receipt_document', 'current_warehouse')
        receipt_code = (self.request.GET.get('receipt_code') or '').strip()
        item_code = (self.request.GET.get('item_code') or '').strip()
        serial_code = (self.request.GET.get('serial_code') or '').strip()
        status = (self.request.GET.get('status') or '').strip()

        if receipt_code:
            queryset = queryset.filter(receipt_document_code__icontains=receipt_code)
        if item_code:
            queryset = queryset.filter(item__item_code__icontains=item_code)
        if serial_code:
            queryset = queryset.filter(serial_code__icontains=serial_code)
        if status:
            queryset = queryset.filter(current_status=status)

        return queryset.order_by('-created_at', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receipt_code'] = (self.request.GET.get('receipt_code') or '').strip()
        context['item_code'] = (self.request.GET.get('item_code') or '').strip()
        context['serial_code'] = (self.request.GET.get('serial_code') or '').strip()
        context['status'] = (self.request.GET.get('status') or '').strip()
        context['status_choices'] = models.ItemSerial.Status.choices
        context['has_filters'] = any([
            context['receipt_code'],
            context['item_code'],
            context['serial_code'],
            context['status'],
        ])
        return context


class ItemCreateView(ItemUnitFormsetMixin, InventoryBaseView, CreateView):
    model = models.Item
    form_class = forms.ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:items')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        units_formset = self.build_unit_formset(data=self.request.POST, company_id=company_id)
        if not units_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, units_formset=units_formset)
            )
        self.object = form.save()
        units_formset.instance = self.object
        self._save_unit_formset(units_formset)
        ordered = self._get_ordered_warehouses(form)
        self._sync_item_warehouses(self.object, ordered, self.request.user)
        messages.success(self.request, _('کالا با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('تعریف کالای جدید')
        return context


class ItemUpdateView(ItemUnitFormsetMixin, InventoryBaseView, UpdateView):
    model = models.Item
    form_class = forms.ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:items')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = kwargs.get('instance')
        company_id = instance.company_id if instance else self.request.session.get('active_company_id')
        kwargs['company_id'] = company_id
        return kwargs
    
    def form_valid(self, form):
        company_id = form.instance.company_id
        units_formset = self.build_unit_formset(data=self.request.POST, instance=form.instance)
        if not units_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, units_formset=units_formset)
            )
        form.instance.edited_by = self.request.user
        self.object = form.save()
        units_formset.instance = self.object
        self._save_unit_formset(units_formset)
        ordered = self._get_ordered_warehouses(form)
        self._sync_item_warehouses(self.object, ordered, self.request.user)
        messages.success(self.request, _('اطلاعات کالا با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش کالا')
        return context


class ItemDeleteView(InventoryBaseView, DeleteView):
    model = models.Item
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:items')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('کالا حذف شد.'))
        return super().delete(request, *args, **kwargs)


class WarehouseListView(InventoryBaseView, ListView):
    model = models.Warehouse
    template_name = 'inventory/warehouses.html'
    context_object_name = 'warehouses'
    paginate_by = 50


class WorkLineListView(InventoryBaseView, ListView):
    model = models.WorkLine
    template_name = 'inventory/work_lines.html'
    context_object_name = 'work_lines'
    paginate_by = 50


# Supplier Views
class SupplierCategoryListView(InventoryBaseView, ListView):
    model = models.SupplierCategory
    template_name = 'inventory/supplier_categories.html'
    context_object_name = 'supplier_categories'
    paginate_by = 50


class SupplierCategoryCreateView(InventoryBaseView, CreateView):
    model = models.SupplierCategory
    form_class = forms.SupplierCategoryForm
    template_name = 'inventory/suppliercategory_form.html'
    success_url = reverse_lazy('inventory:supplier_categories')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        self.object = form.save()
        self._sync_supplier_links(form)
        messages.success(self.request, _('دسته‌بندی تأمین‌کننده با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def _sync_supplier_links(self, form):
        supplier = self.object.supplier
        company = self.object.company
        category = self.object.category
        subcategories = list(form.cleaned_data.get('subcategories') or [])
        items = list(form.cleaned_data.get('items') or [])

        selected_sub_ids = {sub.id for sub in subcategories}
        models.SupplierSubcategory.objects.filter(
            supplier=supplier,
            company=company,
            subcategory__category=category,
        ).exclude(subcategory_id__in=selected_sub_ids).delete()
        for sub in subcategories:
            obj, created = models.SupplierSubcategory.objects.get_or_create(
                supplier=supplier,
                company=company,
                subcategory=sub,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

        selected_item_ids = {item.id for item in items}
        models.SupplierItem.objects.filter(
            supplier=supplier,
            company=company,
            item__category=category,
        ).exclude(item_id__in=selected_item_ids).delete()
        for item in items:
            obj, created = models.SupplierItem.objects.get_or_create(
                supplier=supplier,
                company=company,
                item=item,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ایجاد دسته‌بندی تأمین‌کننده')
        return context


class SupplierCategoryUpdateView(InventoryBaseView, UpdateView):
    model = models.SupplierCategory
    form_class = forms.SupplierCategoryForm
    template_name = 'inventory/suppliercategory_form.html'
    success_url = reverse_lazy('inventory:supplier_categories')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        self.object = form.save()
        self._sync_supplier_links(form)
        messages.success(self.request, _('دسته‌بندی تأمین‌کننده با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def _sync_supplier_links(self, form):
        supplier = self.object.supplier
        company = self.object.company
        category = self.object.category
        subcategories = list(form.cleaned_data.get('subcategories') or [])
        items = list(form.cleaned_data.get('items') or [])

        selected_sub_ids = {sub.id for sub in subcategories}
        models.SupplierSubcategory.objects.filter(
            supplier=supplier,
            company=company,
            subcategory__category=category,
        ).exclude(subcategory_id__in=selected_sub_ids).delete()
        for sub in subcategories:
            obj, created = models.SupplierSubcategory.objects.get_or_create(
                supplier=supplier,
                company=company,
                subcategory=sub,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

        selected_item_ids = {item.id for item in items}
        models.SupplierItem.objects.filter(
            supplier=supplier,
            company=company,
            item__category=category,
        ).exclude(item_id__in=selected_item_ids).delete()
        for item in items:
            obj, created = models.SupplierItem.objects.get_or_create(
                supplier=supplier,
                company=company,
                item=item,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش دسته‌بندی تأمین‌کننده')
        return context


class SupplierCategoryDeleteView(InventoryBaseView, DeleteView):
    model = models.SupplierCategory
    template_name = 'inventory/suppliercategory_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_categories')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('دسته‌بندی تأمین‌کننده حذف شد.'))
        return super().delete(request, *args, **kwargs)


class SupplierListView(InventoryBaseView, ListView):
    model = models.Supplier
    template_name = 'inventory/suppliers.html'
    context_object_name = 'suppliers'
    paginate_by = 50


class SupplierCreateView(InventoryBaseView, CreateView):
    model = models.Supplier
    form_class = forms.SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:suppliers')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('تأمین‌کننده با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ایجاد تأمین‌کننده')
        return context


class SupplierUpdateView(InventoryBaseView, UpdateView):
    model = models.Supplier
    form_class = forms.SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:suppliers')
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('تأمین‌کننده با موفقیت ویرایش شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش تأمین‌کننده')
        return context


class SupplierDeleteView(InventoryBaseView, DeleteView):
    model = models.Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:suppliers')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('تأمین‌کننده حذف شد.'))
        return super().delete(request, *args, **kwargs)


# Purchase Request Views
class PurchaseRequestFormMixin(InventoryBaseView):
    template_name = 'inventory/purchase_request_form.html'
    form_title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        kwargs['request_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        form = context.get('form')
        raw_fieldsets = self.get_fieldsets()
        render_fieldsets = []
        used_fields = []
        if form and raw_fieldsets:
            for title, names in raw_fieldsets:
                bound_fields = []
                for name in names:
                    if name in form.fields:
                        bound_fields.append(form[name])
                        used_fields.append(name)
                if bound_fields:
                    render_fieldsets.append((title, bound_fields))
        context['fieldsets'] = render_fieldsets
        context['used_fields'] = used_fields
        context['list_url'] = reverse_lazy('inventory:purchase_requests')
        context['is_edit'] = bool(getattr(self, 'object', None))
        context['purchase_request'] = getattr(self, 'object', None)

        if form and 'item' in form.fields and 'unit' in form.fields:
            unit_map = {}
            for item in form.fields['item'].queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
            context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
        else:
            context['unit_options_json'] = mark_safe('{}')
        context['unit_placeholder'] = str(forms.UNIT_CHOICES[0][1])
        return context

    def get_fieldsets(self):
        return []


class PurchaseRequestListView(InventoryBaseView, ListView):
    model = models.PurchaseRequest
    template_name = 'inventory/purchase_requests.html'
    context_object_name = 'purchase_requests'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('item', 'requested_by', 'approver')
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        search = self.request.GET.get('search')
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if search:
            value = search.strip()
            if value:
                queryset = queryset.filter(
                    Q(request_code__icontains=value)
                    | Q(item__name__icontains=value)
                    | Q(item_code__icontains=value)
                )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.request.session.get('active_company_id')
        stats_queryset = models.PurchaseRequest.objects.filter(company_id=company_id)
        context['total_count'] = stats_queryset.count()
        context['draft_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.DRAFT).count()
        context['approved_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.APPROVED).count()
        context['ordered_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.ORDERED).count()
        context['fulfilled_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.FULFILLED).count()
        context['create_url'] = reverse_lazy('inventory:purchase_request_create')
        context['edit_url_name'] = 'inventory:purchase_request_edit'
        context['approve_url_name'] = 'inventory:purchase_request_approve'
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['search_term'] = self.request.GET.get('search', '')
        current_person = Person.objects.filter(company_id=company_id, user=self.request.user).first()
        context['current_person'] = current_person
        approver_queryset = forms.get_purchase_request_approvers(company_id)
        approver_ids = set(approver_queryset.values_list('id', flat=True))
        for pr in context['purchase_requests']:
            requested_by_id = getattr(pr, 'requested_by_id', None)
            pr.can_current_user_edit = (
                pr.status == models.PurchaseRequest.Status.DRAFT
                and current_person
                and requested_by_id == getattr(current_person, 'id', None)
            )
            pr.can_current_user_approve = (
                pr.status == models.PurchaseRequest.Status.DRAFT
                and current_person
                and (
                    (pr.approver_id and pr.approver_id == current_person.id)
                    or (not pr.approver_id and current_person.id in approver_ids)
                )
            )
        context['approver_person_ids'] = list(approver_ids)
        return context


class PurchaseRequestCreateView(PurchaseRequestFormMixin, CreateView):
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
    success_url = reverse_lazy('inventory:purchase_requests')
    form_title = _('ایجاد درخواست خرید')

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        requester = Person.objects.filter(company_id=company_id, user=self.request.user).first()
        if not requester:
            form.add_error(None, _('برای این شرکت پروفایل پرسنلی متصل به کاربر فعلی یافت نشد.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        form.instance.requested_by = requester
        form.instance.request_date = timezone.now().date()
        form.instance.status = models.PurchaseRequest.Status.DRAFT
        response = super().form_valid(form)
        messages.success(self.request, _('درخواست خرید با موفقیت ثبت شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'needed_by_date', 'priority']),
            (_('تایید'), ['approver', 'reason_code']),
        ]


class PurchaseRequestUpdateView(PurchaseRequestFormMixin, UpdateView):
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
    success_url = reverse_lazy('inventory:purchase_requests')
    form_title = _('ویرایش درخواست خرید')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            status=models.PurchaseRequest.Status.DRAFT,
            requested_by__user=self.request.user,
        )

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        response = super().form_valid(form)
        messages.success(self.request, _('درخواست خرید با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'needed_by_date', 'priority']),
            (_('تایید'), ['approver', 'reason_code']),
        ]


class PurchaseRequestApproveView(InventoryBaseView, View):
    def post(self, request, *args, **kwargs):
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            messages.error(request, _('شرکت فعال مشخص نشده است.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        purchase_request = get_object_or_404(
            models.PurchaseRequest,
            pk=kwargs.get('pk'),
            company_id=company_id,
        )

        if purchase_request.status == models.PurchaseRequest.Status.APPROVED:
            messages.info(request, _('این درخواست قبلاً تایید شده است.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        current_person = Person.objects.filter(company_id=company_id, user=request.user).first()
        if not current_person:
            messages.error(request, _('برای این شرکت پروفایل پرسنلی متصل به کاربر فعلی یافت نشد.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        if purchase_request.approver_id and purchase_request.approver_id != current_person.id:
            messages.error(request, _('تنها تاییدکننده تعیین‌شده می‌تواند این درخواست را تایید کند.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        allowed_person_ids = set(forms.get_purchase_request_approvers(company_id).values_list('id', flat=True))
        if current_person.id not in allowed_person_ids:
            messages.error(request, _('شما مجوز تایید درخواست خرید را ندارید.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        now = timezone.now()
        purchase_request.status = models.PurchaseRequest.Status.APPROVED
        purchase_request.approved_at = now
        if not purchase_request.approver_id:
            purchase_request.approver = current_person
        purchase_request.is_locked = 1
        update_fields = ['status', 'approved_at', 'approver', 'is_locked']
        if hasattr(purchase_request, 'locked_at'):
            purchase_request.locked_at = now
            update_fields.append('locked_at')
        if hasattr(purchase_request, 'locked_by_id'):
            purchase_request.locked_by = request.user
            update_fields.append('locked_by')
        if hasattr(purchase_request, 'edited_by_id'):
            purchase_request.edited_by = request.user
            update_fields.append('edited_by')
        purchase_request.save(update_fields=update_fields)
        messages.success(request, _('درخواست خرید تایید شد و برای استفاده در رسیدها آماده است.'))
        return HttpResponseRedirect(reverse('inventory:purchase_requests'))


class WarehouseRequestFormMixin(InventoryBaseView):
    template_name = 'inventory/warehouse_request_form.html'
    form_title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        kwargs['request_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        form = context.get('form')
        raw_fieldsets = self.get_fieldsets()
        render_fieldsets = []
        used_fields = []
        if form and raw_fieldsets:
            for title, names in raw_fieldsets:
                bound_fields = []
                for name in names:
                    if name in form.fields:
                        bound_fields.append(form[name])
                        used_fields.append(name)
                if bound_fields:
                    render_fieldsets.append((title, bound_fields))
        context['fieldsets'] = render_fieldsets
        context['used_fields'] = used_fields
        context['list_url'] = reverse_lazy('inventory:warehouse_requests')
        context['is_edit'] = bool(getattr(self, 'object', None))
        context['warehouse_request'] = getattr(self, 'object', None)

        if form and 'item' in form.fields:
            unit_map = {}
            warehouse_map = {}
            for item in form.fields['item'].queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
                warehouse_map[str(item.pk)] = form._get_item_allowed_warehouses(item)
            context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
            context['warehouse_options_json'] = mark_safe(json.dumps(warehouse_map, ensure_ascii=False))
        else:
            context['unit_options_json'] = mark_safe('{}')
            context['warehouse_options_json'] = mark_safe('{}')
        context['unit_placeholder'] = str(forms.UNIT_CHOICES[0][1])
        context['warehouse_placeholder'] = _('--- انتخاب کنید ---')
        return context

    def get_fieldsets(self):
        return []


class WarehouseRequestListView(InventoryBaseView, ListView):
    model = models.WarehouseRequest
    template_name = 'inventory/warehouse_requests.html'
    context_object_name = 'requests'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('item', 'warehouse', 'requester', 'approver')
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        search = self.request.GET.get('search')
        if status:
            queryset = queryset.filter(request_status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if search:
            value = search.strip()
            if value:
                queryset = queryset.filter(
                    Q(request_code__icontains=value)
                    | Q(item__name__icontains=value)
                    | Q(item_code__icontains=value)
                )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.request.session.get('active_company_id')
        stats_queryset = models.WarehouseRequest.objects.filter(company_id=company_id)
        context['total_count'] = stats_queryset.count()
        context['draft_count'] = stats_queryset.filter(request_status='draft').count()
        context['approved_count'] = stats_queryset.filter(request_status='approved').count()
        context['issued_count'] = stats_queryset.filter(request_status='issued').count()
        context['create_url'] = reverse_lazy('inventory:warehouse_request_create')
        context['edit_url_name'] = 'inventory:warehouse_request_edit'
        context['approve_url_name'] = 'inventory:warehouse_request_approve'
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['search_term'] = self.request.GET.get('search', '')
        current_person = Person.objects.filter(company_id=company_id, user=self.request.user).first()
        context['current_person'] = current_person
        approver_queryset = forms.get_feature_approvers("inventory.requests.warehouse", company_id)
        approver_ids = set(approver_queryset.values_list('id', flat=True))
        for wr in context['requests']:
            requester_id = getattr(wr, 'requester_id', None)
            wr.can_current_user_edit = (
                wr.request_status == 'draft'
                and current_person
                and requester_id == getattr(current_person, 'id', None)
            )
            wr.can_current_user_approve = (
                wr.request_status == 'draft'
                and current_person
                and (
                    (wr.approver_id and wr.approver_id == current_person.id)
                    or (not wr.approver_id and current_person.id in approver_ids)
                )
            )
        context['approver_person_ids'] = list(approver_ids)
        return context


class WarehouseRequestCreateView(WarehouseRequestFormMixin, CreateView):
    model = models.WarehouseRequest
    form_class = forms.WarehouseRequestForm
    success_url = reverse_lazy('inventory:warehouse_requests')
    form_title = _('ایجاد درخواست انبار')

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        requester = Person.objects.filter(company_id=company_id, user=self.request.user).first()
        if not requester:
            form.add_error(None, _('برای این شرکت پروفایل پرسنلی متصل به کاربر فعلی یافت نشد.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        form.instance.requester = requester
        form.instance.request_date = timezone.now().date()
        form.instance.request_status = 'draft'
        response = super().form_valid(form)
        messages.success(self.request, _('درخواست انبار با موفقیت ثبت شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'warehouse', 'department_unit']),
            (_('زمان‌بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'purpose']),
        ]


class WarehouseRequestUpdateView(WarehouseRequestFormMixin, UpdateView):
    model = models.WarehouseRequest
    form_class = forms.WarehouseRequestForm
    success_url = reverse_lazy('inventory:warehouse_requests')
    form_title = _('ویرایش درخواست انبار')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            request_status='draft',
            requester__user=self.request.user,
        )

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        response = super().form_valid(form)
        messages.success(self.request, _('درخواست انبار با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'warehouse', 'department_unit']),
            (_('زمان‌بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'purpose']),
        ]


class WarehouseRequestApproveView(InventoryBaseView, View):
    def post(self, request, *args, **kwargs):
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            messages.error(request, _('شرکت فعال مشخص نشده است.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        warehouse_request = get_object_or_404(
            models.WarehouseRequest,
            pk=kwargs.get('pk'),
            company_id=company_id,
        )

        if warehouse_request.request_status == 'approved':
            messages.info(request, _('این درخواست قبلاً تایید شده است.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        current_person = Person.objects.filter(company_id=company_id, user=request.user).first()
        if not current_person:
            messages.error(request, _('برای این شرکت پروفایل پرسنلی متصل به کاربر فعلی یافت نشد.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        if warehouse_request.approver_id and warehouse_request.approver_id != current_person.id:
            messages.error(request, _('تنها تاییدکننده تعیین‌شده می‌تواند این درخواست را تایید کند.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        allowed_person_ids = set(forms.get_feature_approvers("inventory.requests.warehouse", company_id).values_list('id', flat=True))
        if current_person.id not in allowed_person_ids:
            messages.error(request, _('شما مجوز تایید درخواست انبار را ندارید.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        now = timezone.now()
        warehouse_request.request_status = 'approved'
        warehouse_request.approved_at = now
        warehouse_request.approved_by = current_person
        warehouse_request.approved_by_code = current_person.public_code
        if not warehouse_request.approver_id:
            warehouse_request.approver = current_person
        warehouse_request.is_locked = 1
        update_fields = ['request_status', 'approved_at', 'approved_by', 'approved_by_code', 'approver', 'is_locked']
        if hasattr(warehouse_request, 'locked_at'):
            warehouse_request.locked_at = now
            update_fields.append('locked_at')
        if hasattr(warehouse_request, 'locked_by_id'):
            warehouse_request.locked_by = request.user
            update_fields.append('locked_by')
        if hasattr(warehouse_request, 'edited_by_id'):
            warehouse_request.edited_by = request.user
            update_fields.append('edited_by')
        warehouse_request.save(update_fields=update_fields)
        messages.success(request, _('درخواست انبار تایید شد و برای استفاده در رسیدها آماده است.'))
        return HttpResponseRedirect(reverse('inventory:warehouse_requests'))


# Receipt Views
class ReceiptTemporaryListView(InventoryBaseView, ListView):
    model = models.ReceiptTemporary
    template_name = 'inventory/receipt_temporary.html'
    context_object_name = 'receipts'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:receipt_temporary_create')
        context['edit_url_name'] = 'inventory:receipt_temporary_edit'
        context['lock_url_name'] = 'inventory:receipt_temporary_lock'
        context['create_label'] = _('Temporary Receipt')
        context['show_qc'] = True
        context['show_conversion'] = True
        context['empty_heading'] = _('No Temporary Receipts Found')
        context['empty_text'] = _('Start by creating your first temporary receipt.')
        return context


class ReceiptPermanentListView(InventoryBaseView, ListView):
    model = models.ReceiptPermanent
    template_name = 'inventory/receipt_permanent.html'
    context_object_name = 'receipts'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:receipt_permanent_create')
        context['edit_url_name'] = 'inventory:receipt_permanent_edit'
        context['lock_url_name'] = 'inventory:receipt_permanent_lock'
        context['create_label'] = _('Permanent Receipt')
        context['show_qc'] = False
        context['show_conversion'] = False
        context['empty_heading'] = _('No Permanent Receipts Found')
        context['empty_text'] = _('Start by creating your first permanent receipt.')
        context['serial_url_name'] = 'inventory:receipt_permanent_serials'
        return context


class ReceiptConsignmentListView(InventoryBaseView, ListView):
    model = models.ReceiptConsignment
    template_name = 'inventory/receipt_consignment.html'
    context_object_name = 'receipts'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:receipt_consignment_create')
        context['edit_url_name'] = 'inventory:receipt_consignment_edit'
        context['lock_url_name'] = 'inventory:receipt_consignment_lock'
        context['create_label'] = _('Consignment Receipt')
        context['show_qc'] = False
        context['show_conversion'] = False
        context['empty_heading'] = _('No Consignment Receipts Found')
        context['empty_text'] = _('Start by creating your first consignment receipt.')
        context['serial_url_name'] = 'inventory:receipt_consignment_serials'
        return context


class ReceiptFormMixin(InventoryBaseView):
    """Shared helpers for receipt create/update views."""

    template_name = 'inventory/receipt_form.html'
    form_title = ''
    receipt_variant = ''
    list_url_name = ''
    lock_url_name = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        context['receipt_variant'] = self.receipt_variant
        form = context.get('form')
        raw_fieldsets = self.get_fieldsets()
        render_fieldsets = []
        used_fields = []
        if form:
            for title, names in raw_fieldsets:
                bound_fields = []
                for name in names:
                    if name in form.fields:
                        bound_fields.append(form[name])
                        used_fields.append(name)
                if bound_fields:
                    render_fieldsets.append((title, bound_fields))
        context['fieldsets'] = render_fieldsets
        context['used_fields'] = used_fields
        context['list_url'] = reverse_lazy(self.list_url_name)
        context['is_edit'] = bool(getattr(self, 'object', None))

        if form and 'item' in form.fields and 'unit' in form.fields:
            unit_map = {}
            item_queryset = form.fields['item'].queryset
            for item in item_queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
            context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
        else:
            context['unit_options_json'] = mark_safe('{}')

        placeholder_label = str(forms.UNIT_CHOICES[0][1])
        context['unit_placeholder'] = placeholder_label

        instance = getattr(form, 'instance', None)
        context['document_instance'] = instance
        if instance and getattr(instance, 'pk', None):
            if hasattr(instance, 'get_status_display'):
                try:
                    context['document_status_display'] = instance.get_status_display()
                except TypeError:
                    context['document_status_display'] = None
            else:
                context['document_status_display'] = None
            is_locked = bool(getattr(instance, 'is_locked', 0))
            context['document_is_locked'] = is_locked
            if not is_locked and getattr(self, 'lock_url_name', None):
                context['lock_url'] = reverse(self.lock_url_name, args=[instance.pk])
            else:
                context['lock_url'] = None
        else:
            context['document_status_display'] = None
            context['document_is_locked'] = False
            context['lock_url'] = None

        return context

    def get_fieldsets(self):
        return []


class StocktakingFormMixin(InventoryBaseView):
    """Shared helpers for stocktaking create/update views."""

    template_name = 'inventory/stocktaking_form.html'
    form_title = ''
    list_url_name = ''
    lock_url_name = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def get_fieldsets(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        form = context.get('form')
        raw_fieldsets = self.get_fieldsets()
        render_fieldsets = []
        used_fields = []
        if form:
            for title, names in raw_fieldsets:
                bound_fields = []
                for name in names:
                    if name in form.fields:
                        bound_fields.append(form[name])
                        used_fields.append(name)
                if bound_fields:
                    render_fieldsets.append((title, bound_fields))
        context['fieldsets'] = render_fieldsets
        context['used_fields'] = used_fields
        context['list_url'] = reverse_lazy(self.list_url_name)
        context['is_edit'] = bool(getattr(self, 'object', None))

        unit_map = {}
        warehouse_map = {}
        if form and 'item' in form.fields:
            item_queryset = form.fields['item'].queryset
            for item in item_queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
                warehouse_map[str(item.pk)] = form._get_item_allowed_warehouses(item)
        context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
        context['unit_placeholder'] = str(forms.UNIT_CHOICES[0][1])
        context['warehouse_options_json'] = mark_safe(json.dumps(warehouse_map, ensure_ascii=False))
        context['warehouse_placeholder'] = _("--- انتخاب کنید ---")

        instance = getattr(form, 'instance', None)
        context['document_instance'] = instance
        if instance and getattr(instance, 'pk', None):
            is_locked = bool(getattr(instance, 'is_locked', 0))
            context['document_is_locked'] = is_locked
            if not is_locked and getattr(self, 'lock_url_name', None):
                context['lock_url'] = reverse(self.lock_url_name, args=[instance.pk])
            else:
                context['lock_url'] = None
        else:
            context['document_is_locked'] = False
            context['lock_url'] = None

        return context


class ReceiptTemporaryCreateView(ReceiptFormMixin, CreateView):
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    success_url = reverse_lazy('inventory:receipt_temporary')
    form_title = _('ایجاد رسید موقت')
    receipt_variant = 'temporary'
    list_url_name = 'inventory:receipt_temporary'
    lock_url_name = 'inventory:receipt_temporary_lock'

    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('رسید موقت با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('Item & Warehouse'), ['item', 'warehouse', 'unit', 'quantity', 'expected_receipt_date']),
            (_('Supplier & References'), ['supplier', 'source_document_type', 'source_document_code', 'qc_approval_notes']),
        ]


class ReceiptTemporaryUpdateView(DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    success_url = reverse_lazy('inventory:receipt_temporary')
    form_title = _('ویرایش رسید موقت')
    receipt_variant = 'temporary'
    list_url_name = 'inventory:receipt_temporary'
    lock_url_name = 'inventory:receipt_temporary_lock'
    lock_redirect_url_name = 'inventory:receipt_temporary'

    def form_valid(self, form):
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('رسید موقت با موفقیت ویرایش شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('Item & Warehouse'), ['item', 'warehouse', 'unit', 'quantity', 'expected_receipt_date']),
            (_('Supplier & References'), ['supplier', 'source_document_type', 'source_document_code', 'qc_approval_notes']),
        ]


class ReceiptPermanentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    model = models.ReceiptPermanent
    form_class = forms.ReceiptPermanentForm
    formset_class = forms.ReceiptPermanentLineFormSet
    success_url = reverse_lazy('inventory:receipt_permanent')
    form_title = _('ایجاد رسید دائم')
    receipt_variant = 'permanent'
    list_url_name = 'inventory:receipt_permanent'
    lock_url_name = 'inventory:receipt_permanent_lock'

    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید دائم با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request']),
        ]


class ReceiptPermanentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    model = models.ReceiptPermanent
    form_class = forms.ReceiptPermanentForm
    formset_class = forms.ReceiptPermanentLineFormSet
    success_url = reverse_lazy('inventory:receipt_permanent')
    form_title = _('ویرایش رسید دائم')
    receipt_variant = 'permanent'
    list_url_name = 'inventory:receipt_permanent'
    lock_url_name = 'inventory:receipt_permanent_lock'
    lock_redirect_url_name = 'inventory:receipt_permanent'

    def form_valid(self, form):
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید دائم با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request']),
        ]


class ReceiptConsignmentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    model = models.ReceiptConsignment
    form_class = forms.ReceiptConsignmentForm
    formset_class = forms.ReceiptConsignmentLineFormSet
    success_url = reverse_lazy('inventory:receipt_consignment')
    form_title = _('ایجاد رسید امانی')
    receipt_variant = 'consignment'
    list_url_name = 'inventory:receipt_consignment'
    lock_url_name = 'inventory:receipt_consignment_lock'

    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید امانی با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'consignment_contract_code', 'expected_return_date', 'valuation_method', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request', 'ownership_status', 'conversion_receipt', 'conversion_date', 'return_document_id']),
        ]


class ReceiptConsignmentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    model = models.ReceiptConsignment
    form_class = forms.ReceiptConsignmentForm
    formset_class = forms.ReceiptConsignmentLineFormSet
    success_url = reverse_lazy('inventory:receipt_consignment')
    form_title = _('ویرایش رسید امانی')
    receipt_variant = 'consignment'
    list_url_name = 'inventory:receipt_consignment'
    lock_url_name = 'inventory:receipt_consignment_lock'
    lock_redirect_url_name = 'inventory:receipt_consignment'

    def form_valid(self, form):
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید امانی با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'consignment_contract_code', 'expected_return_date', 'valuation_method', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request', 'ownership_status', 'conversion_receipt', 'conversion_date', 'return_document_id']),
        ]


class IssuePermanentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    model = models.IssuePermanent
    form_class = forms.IssuePermanentForm
    formset_class = forms.IssuePermanentLineFormSet
    success_url = reverse_lazy('inventory:issue_permanent')
    form_title = _('ایجاد حواله دائم')
    receipt_variant = 'issue_permanent'
    list_url_name = 'inventory:issue_permanent'
    lock_url_name = 'inventory:issue_permanent_lock'

    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله دائم با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'department_unit']),
        ]


class IssuePermanentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    model = models.IssuePermanent
    form_class = forms.IssuePermanentForm
    formset_class = forms.IssuePermanentLineFormSet
    success_url = reverse_lazy('inventory:issue_permanent')
    form_title = _('ویرایش حواله دائم')
    receipt_variant = 'issue_permanent'
    list_url_name = 'inventory:issue_permanent'
    lock_url_name = 'inventory:issue_permanent_lock'
    lock_redirect_url_name = 'inventory:issue_permanent'

    def form_valid(self, form):
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله دائم با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'department_unit']),
        ]


class IssueConsumptionCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    model = models.IssueConsumption
    form_class = forms.IssueConsumptionForm
    formset_class = forms.IssueConsumptionLineFormSet
    success_url = reverse_lazy('inventory:issue_consumption')
    form_title = _('ایجاد حواله مصرف')
    receipt_variant = 'issue_consumption'
    list_url_name = 'inventory:issue_consumption'
    lock_url_name = 'inventory:issue_consumption_lock'

    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله مصرف با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'department_unit']),
        ]


class IssueConsumptionUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    model = models.IssueConsumption
    form_class = forms.IssueConsumptionForm
    formset_class = forms.IssueConsumptionLineFormSet
    success_url = reverse_lazy('inventory:issue_consumption')
    form_title = _('ویرایش حواله مصرف')
    receipt_variant = 'issue_consumption'
    list_url_name = 'inventory:issue_consumption'
    lock_url_name = 'inventory:issue_consumption_lock'
    lock_redirect_url_name = 'inventory:issue_consumption'

    def form_valid(self, form):
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله مصرف با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'department_unit']),
        ]


class IssueConsignmentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    model = models.IssueConsignment
    form_class = forms.IssueConsignmentForm
    formset_class = forms.IssueConsignmentLineFormSet
    success_url = reverse_lazy('inventory:issue_consignment')
    form_title = _('ایجاد حواله امانی')
    receipt_variant = 'issue_consignment'
    list_url_name = 'inventory:issue_consignment'
    lock_url_name = 'inventory:issue_consignment_lock'

    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله امانی با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'department_unit']),
        ]


class IssueConsignmentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    model = models.IssueConsignment
    form_class = forms.IssueConsignmentForm
    formset_class = forms.IssueConsignmentLineFormSet
    success_url = reverse_lazy('inventory:issue_consignment')
    form_title = _('ویرایش حواله امانی')
    receipt_variant = 'issue_consignment'
    list_url_name = 'inventory:issue_consignment'
    lock_url_name = 'inventory:issue_consignment_lock'
    lock_redirect_url_name = 'inventory:issue_consignment'

    def form_valid(self, form):
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله امانی با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self):
        return [
            (_('Document Info'), ['document_code', 'document_date', 'department_unit']),
        ]


class ReceiptTemporaryLockView(DocumentLockView):
    model = models.ReceiptTemporary
    success_url_name = 'inventory:receipt_temporary'
    success_message = _('رسید موقت قفل شد و دیگر قابل ویرایش نیست.')


class ReceiptPermanentLockView(DocumentLockView):
    model = models.ReceiptPermanent
    success_url_name = 'inventory:receipt_permanent'
    success_message = _('رسید دائم قفل شد و دیگر قابل ویرایش نیست.')

    def after_lock(self, obj, request):
        # Generate serials for all lines with lot-tracked items
        lines = models.ReceiptPermanentLine.objects.filter(document=obj, is_enabled=1)
        total_created = 0
        for line in lines:
            try:
                created = serial_service.generate_receipt_line_serials(line, user=request.user)
                total_created += created
            except serial_service.SerialTrackingError as exc:
                messages.error(request, str(exc))
        if total_created > 0:
            messages.info(
                request,
                _('%(count)s serial numbers were generated for this receipt.') % {'count': total_created},
            )


class ReceiptConsignmentLockView(DocumentLockView):
    model = models.ReceiptConsignment
    success_url_name = 'inventory:receipt_consignment'
    success_message = _('رسید امانی قفل شد و دیگر قابل ویرایش نیست.')


class IssuePermanentLockView(DocumentLockView):
    model = models.IssuePermanent
    success_url_name = 'inventory:issue_permanent'
    success_message = _('حواله دائم قفل شد و دیگر قابل ویرایش نیست.')

    def before_lock(self, obj, request):
        # Validate serials for all lines with lot-tracked items
        lines = models.IssuePermanentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            if line.item and line.item.has_lot_tracking == 1:
                try:
                    required = int(Decimal(line.quantity))
                except (InvalidOperation, TypeError):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                if Decimal(line.quantity) != Decimal(required):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                selected = line.serials.count()
                if selected != required:
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، پیش از قفل کردن باید %(expected)s سریال انتخاب شود (الان %(selected)s عدد ثبت شده است).')
                        % {'item': line.item.name, 'expected': required, 'selected': selected}
                    )
                    return False
        return True

    def after_lock(self, obj, request):
        # Finalize serials for all lines
        lines = models.IssuePermanentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            try:
                serial_service.finalize_issue_line_serials(line, user=request.user)
            except serial_service.SerialTrackingError as exc:
                messages.error(request, str(exc))


class IssueConsumptionLockView(DocumentLockView):
    model = models.IssueConsumption
    success_url_name = 'inventory:issue_consumption'
    success_message = _('حواله مصرفی قفل شد و دیگر قابل ویرایش نیست.')

    def before_lock(self, obj, request):
        # Validate serials for all lines with lot-tracked items
        lines = models.IssueConsumptionLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            if line.item and line.item.has_lot_tracking == 1:
                try:
                    required = int(Decimal(line.quantity))
                except (InvalidOperation, TypeError):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                if Decimal(line.quantity) != Decimal(required):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                selected = line.serials.count()
                if selected != required:
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، پیش از قفل کردن باید %(expected)s سریال انتخاب شود (الان %(selected)s عدد ثبت شده است).')
                        % {'item': line.item.name, 'expected': required, 'selected': selected}
                    )
                    return False
        return True

    def after_lock(self, obj, request):
        # Finalize serials for all lines
        lines = models.IssueConsumptionLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            try:
                serial_service.finalize_issue_line_serials(line, user=request.user)
            except serial_service.SerialTrackingError as exc:
                messages.error(request, str(exc))


class IssueConsignmentLockView(DocumentLockView):
    model = models.IssueConsignment
    success_url_name = 'inventory:issue_consignment'
    success_message = _('حواله امانی قفل شد و دیگر قابل ویرایش نیست.')

    def before_lock(self, obj, request):
        # Validate serials for all lines with lot-tracked items
        lines = models.IssueConsignmentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            if line.item and line.item.has_lot_tracking == 1:
                try:
                    required = int(Decimal(line.quantity))
                except (InvalidOperation, TypeError):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                if Decimal(line.quantity) != Decimal(required):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                selected = line.serials.count()
                if selected != required:
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، پیش از قفل کردن باید %(expected)s سریال انتخاب شود (الان %(selected)s عدد ثبت شده است).')
                        % {'item': line.item.name, 'expected': required, 'selected': selected}
                    )
                    return False
        return True

    def after_lock(self, obj, request):
        # Finalize serials for all lines
        lines = models.IssueConsignmentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            try:
                serial_service.finalize_issue_line_serials(line, user=request.user)
            except serial_service.SerialTrackingError as exc:
                messages.error(request, str(exc))


class StocktakingDeficitLockView(DocumentLockView):
    model = models.StocktakingDeficit
    success_url_name = 'inventory:stocktaking_deficit'
    success_message = _('سند کسری شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


class StocktakingSurplusLockView(DocumentLockView):
    model = models.StocktakingSurplus
    success_url_name = 'inventory:stocktaking_surplus'
    success_message = _('سند مازاد شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


class StocktakingRecordLockView(DocumentLockView):
    model = models.StocktakingRecord
    success_url_name = 'inventory:stocktaking_records'
    success_message = _('گزارش نهایی شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


# Issue Views
class IssuePermanentListView(InventoryBaseView, ListView):
    model = models.IssuePermanent
    template_name = 'inventory/issue_permanent.html'
    context_object_name = 'issues'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:issue_permanent_create')
        context['edit_url_name'] = 'inventory:issue_permanent_edit'
        context['lock_url_name'] = 'inventory:issue_permanent_lock'
        context['create_label'] = _('Permanent Issue')
        context['serial_url_name'] = 'inventory:issue_permanent_serials'
        return context


class IssueConsumptionListView(InventoryBaseView, ListView):
    model = models.IssueConsumption
    template_name = 'inventory/issue_consumption.html'
    context_object_name = 'issues'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:issue_consumption_create')
        context['edit_url_name'] = 'inventory:issue_consumption_edit'
        context['lock_url_name'] = 'inventory:issue_consumption_lock'
        context['create_label'] = _('Consumption Issue')
        context['serial_url_name'] = 'inventory:issue_consumption_serials'
        return context


class IssueConsignmentListView(InventoryBaseView, ListView):
    model = models.IssueConsignment
    template_name = 'inventory/issue_consignment.html'
    context_object_name = 'issues'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:issue_consignment_create')
        context['edit_url_name'] = 'inventory:issue_consignment_edit'
        context['lock_url_name'] = 'inventory:issue_consignment_lock'
        context['create_label'] = _('Consignment Issue')
        context['serial_url_name'] = 'inventory:issue_consignment_serials'
        return context


# Stocktaking Views
class StocktakingDeficitCreateView(StocktakingFormMixin, CreateView):
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    form_title = _('ایجاد سند کسری انبارگردانی')
    list_url_name = 'inventory:stocktaking_deficit'
    lock_url_name = 'inventory:stocktaking_deficit_lock'

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند کسری انبارگردانی با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingDeficitUpdateView(DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    form_title = _('ویرایش سند کسری انبارگردانی')
    list_url_name = 'inventory:stocktaking_deficit'
    lock_url_name = 'inventory:stocktaking_deficit_lock'

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند کسری انبارگردانی با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingSurplusCreateView(StocktakingFormMixin, CreateView):
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    form_title = _('ایجاد سند مازاد انبارگردانی')
    list_url_name = 'inventory:stocktaking_surplus'
    lock_url_name = 'inventory:stocktaking_surplus_lock'

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند مازاد انبارگردانی با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingSurplusUpdateView(DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    form_title = _('ویرایش سند مازاد انبارگردانی')
    list_url_name = 'inventory:stocktaking_surplus'
    lock_url_name = 'inventory:stocktaking_surplus_lock'

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند مازاد انبارگردانی با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingRecordCreateView(StocktakingFormMixin, CreateView):
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    form_title = _('ایجاد سند نهایی انبارگردانی')
    list_url_name = 'inventory:stocktaking_records'
    lock_url_name = 'inventory:stocktaking_record_lock'

    def form_valid(self, form):
        company_id = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند نهایی انبارگردانی با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approval_status', 'approved_at', 'approver', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]


class StocktakingRecordUpdateView(DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    form_title = _('ویرایش سند نهایی انبارگردانی')
    list_url_name = 'inventory:stocktaking_records'
    lock_url_name = 'inventory:stocktaking_record_lock'

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند نهایی انبارگردانی با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self):
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approval_status', 'approved_at', 'approver', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]


class StocktakingDeficitListView(InventoryBaseView, ListView):
    model = models.StocktakingDeficit
    template_name = 'inventory/stocktaking_deficit.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:stocktaking_deficit_create')
        context['edit_url_name'] = 'inventory:stocktaking_deficit_edit'
        context['lock_url_name'] = 'inventory:stocktaking_deficit_lock'
        return context


class StocktakingSurplusListView(InventoryBaseView, ListView):
    model = models.StocktakingSurplus
    template_name = 'inventory/stocktaking_surplus.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:stocktaking_surplus_create')
        context['edit_url_name'] = 'inventory:stocktaking_surplus_edit'
        context['lock_url_name'] = 'inventory:stocktaking_surplus_lock'
        return context


class StocktakingRecordListView(InventoryBaseView, ListView):
    model = models.StocktakingRecord
    template_name = 'inventory/stocktaking_records.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:stocktaking_record_create')
        context['edit_url_name'] = 'inventory:stocktaking_record_edit'
        context['lock_url_name'] = 'inventory:stocktaking_record_lock'
        return context


# Warehouse Request Views
# Inventory Balance View
class InventoryBalanceView(InventoryBaseView, TemplateView):
    """
    Display current inventory balances calculated from stocktaking baseline
    plus subsequent receipts and issues.
    """
    template_name = 'inventory/inventory_balance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        warehouse_id = self.request.GET.get('warehouse_id')
        item_type_id = self.request.GET.get('item_type_id')
        item_category_id = self.request.GET.get('item_category_id')
        as_of_date = self.request.GET.get('as_of_date')
        
        # Parse date
        if as_of_date:
            try:
                as_of_date = date.fromisoformat(as_of_date)
            except ValueError:
                as_of_date = None
        
        # Get warehouse and filter options for UI
        context['warehouses'] = models.Warehouse.objects.filter(is_enabled=1).order_by('name')
        context['item_types'] = models.ItemType.objects.filter(is_enabled=1).order_by('name')
        context['item_categories'] = models.ItemCategory.objects.filter(is_enabled=1).order_by('name')
        
        # Selected filters
        context['selected_warehouse_id'] = warehouse_id
        context['selected_item_type_id'] = item_type_id
        context['selected_item_category_id'] = item_category_id
        context['as_of_date'] = as_of_date or date.today()
        
        # Calculate balances if warehouse is selected
        if warehouse_id:
            try:
                # Get company_id from session
                company_id = self.request.session.get('active_company_id')
                if not company_id:
                    company_id = self.request.user.usercompanyaccess_set.first().company_id if self.request.user.usercompanyaccess_set.exists() else 1
                
                balances = inventory_balance.calculate_warehouse_balances(
                    company_id=company_id,
                    warehouse_id=int(warehouse_id),
                    as_of_date=as_of_date,
                    item_type_id=int(item_type_id) if item_type_id else None,
                    item_category_id=int(item_category_id) if item_category_id else None,
                )
                context['balances'] = balances
                context['total_items'] = len(balances)
                context['total_balance_value'] = sum(b['current_balance'] for b in balances)
            except Exception as e:
                context['error'] = str(e)
                context['balances'] = []
        else:
            context['balances'] = []
        
        return context


class InventoryBalanceAPIView(InventoryBaseView, TemplateView):
    """
    JSON API endpoint for inventory balance calculation.
    """
    def get(self, request, *args, **kwargs):
        warehouse_id = request.GET.get('warehouse_id')
        item_id = request.GET.get('item_id')
        as_of_date = request.GET.get('as_of_date')
        
        if not warehouse_id or not item_id:
            return JsonResponse({'error': 'warehouse_id and item_id are required'}, status=400)
        
        # Parse date
        if as_of_date:
            try:
                as_of_date = date.fromisoformat(as_of_date)
            except ValueError:
                as_of_date = None
        
        try:
            # Get company from session
            company_id = request.session.get('active_company_id')
            if not company_id:
                company_id = request.user.usercompanyaccess_set.first().company_id if request.user.usercompanyaccess_set.exists() else 1
            
            balance = inventory_balance.calculate_item_balance(
                company_id=company_id,
                warehouse_id=int(warehouse_id),
                item_id=int(item_id),
                as_of_date=as_of_date
            )
            
            return JsonResponse(balance)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# Create/Update/Delete Views for Master Data

# ItemType CRUD
class ItemTypeCreateView(InventoryBaseView, CreateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    template_name = 'inventory/itemtype_form.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Item Type created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Type')
        return context


class ItemTypeUpdateView(InventoryBaseView, UpdateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    template_name = 'inventory/itemtype_form.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Type updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Item Type')
        return context


class ItemTypeDeleteView(InventoryBaseView, DeleteView):
    model = models.ItemType
    template_name = 'inventory/itemtype_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Item Type deleted successfully.'))
        return super().delete(request, *args, **kwargs)


# ItemCategory CRUD
class ItemCategoryCreateView(InventoryBaseView, CreateView):
    model = models.ItemCategory
    form_class = forms.ItemCategoryForm
    template_name = 'inventory/itemcategory_form.html'
    success_url = reverse_lazy('inventory:item_categories')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Item Category created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Category')
        return context
    


class ItemCategoryUpdateView(InventoryBaseView, UpdateView):
    model = models.ItemCategory
    form_class = forms.ItemCategoryForm
    template_name = 'inventory/itemcategory_form.html'
    success_url = reverse_lazy('inventory:item_categories')
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Category updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Item Category')
        return context
    


class ItemCategoryDeleteView(InventoryBaseView, DeleteView):
    model = models.ItemCategory
    template_name = 'inventory/itemcategory_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_categories')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Item Category deleted successfully.'))
        return super().delete(request, *args, **kwargs)


# ItemSubcategory CRUD
class ItemSubcategoryListView(InventoryBaseView, ListView):
    model = models.ItemSubcategory
    template_name = 'inventory/item_subcategories.html'
    context_object_name = 'item_subcategories'
    paginate_by = 50


class ItemSubcategoryCreateView(InventoryBaseView, CreateView):
    model = models.ItemSubcategory
    form_class = forms.ItemSubcategoryForm
    template_name = 'inventory/itemsubcategory_form.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Item Subcategory created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Subcategory')
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            form.fields['category'].queryset = models.ItemCategory.objects.filter(company_id=company_id, is_enabled=1)
        return form


class ItemSubcategoryUpdateView(InventoryBaseView, UpdateView):
    model = models.ItemSubcategory
    form_class = forms.ItemSubcategoryForm
    template_name = 'inventory/itemsubcategory_form.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Subcategory updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Item Subcategory')
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            form.fields['category'].queryset = models.ItemCategory.objects.filter(company_id=company_id, is_enabled=1)
        return form


class ItemSubcategoryDeleteView(InventoryBaseView, DeleteView):
    model = models.ItemSubcategory
    template_name = 'inventory/itemsubcategory_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Item Subcategory deleted successfully.'))
        return super().delete(request, *args, **kwargs)


# Warehouse CRUD
class WarehouseCreateView(InventoryBaseView, CreateView):
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Warehouse created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Warehouse')
        return context


class WarehouseUpdateView(InventoryBaseView, UpdateView):
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Warehouse updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Warehouse')
        return context


class WarehouseDeleteView(InventoryBaseView, DeleteView):
    model = models.Warehouse
    template_name = 'inventory/warehouse_confirm_delete.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Warehouse deleted successfully.'))
        return super().delete(request, *args, **kwargs)


# ============================================================================
# Line-based Serial Assignment Views (Multi-line support)
# ============================================================================

class IssueLineSerialAssignmentBaseView(FeaturePermissionRequiredMixin, FormView):
    """Base view for assigning serials to a specific issue line."""
    template_name = 'inventory/issue_serial_assignment.html'
    form_class = forms.IssueLineSerialAssignmentForm
    line_model = None
    document_model = None
    feature_code = None
    serial_url_name = ''
    list_url_name = ''
    edit_url_name = ''
    lock_url_name = ''

    def dispatch(self, request, *args, **kwargs):
        self.document = self.get_document()
        self.line = self.get_line()
        if self.line.item and self.line.item.has_lot_tracking != 1:
            messages.info(request, _('این کالا نیازی به سریال ندارد.'))
            return HttpResponseRedirect(reverse(self.edit_url_name, args=[self.document.pk]))
        if getattr(self.document, 'is_locked', 0):
            messages.info(request, _('برای سند قفل‌شده امکان تغییر سریال وجود ندارد.'))
            return HttpResponseRedirect(reverse(self.list_url_name))
        return super().dispatch(request, *args, **kwargs)

    def get_document(self):
        queryset = self.document_model.objects.all()
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(self.document_model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))

    def get_line(self):
        queryset = self.line_model.objects.filter(document=self.document)
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(self.line_model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('line_id'))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['line'] = self.line
        return kwargs

    def form_valid(self, form):
        form.save(user=self.request.user)
        messages.success(self.request, _('سریال‌های ردیف با موفقیت ذخیره شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(self.edit_url_name, args=[self.document.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['line'] = self.line
        context['document'] = self.document
        context['list_url'] = reverse(self.list_url_name)
        context['edit_url'] = reverse(self.edit_url_name, args=[self.document.pk])
        context['lock_url'] = reverse(self.lock_url_name, args=[self.document.pk]) if self.lock_url_name else None
        try:
            required = int(Decimal(self.line.quantity))
        except (InvalidOperation, TypeError):
            required = None
        context['required_serials'] = required
        context['selected_serials_count'] = self.line.serials.count()
        available_queryset = context['form'].fields['serials'].queryset
        context['available_serials_count'] = available_queryset.count()
        context['available_serials'] = available_queryset
        return context


class IssuePermanentLineSerialAssignmentView(IssueLineSerialAssignmentBaseView):
    line_model = models.IssuePermanentLine
    document_model = models.IssuePermanent
    feature_code = 'inventory.issues.permanent'
    serial_url_name = 'inventory:issue_permanent_line_serials'
    list_url_name = 'inventory:issue_permanent'
    edit_url_name = 'inventory:issue_permanent_edit'
    lock_url_name = 'inventory:issue_permanent_lock'


class IssueConsumptionLineSerialAssignmentView(IssueLineSerialAssignmentBaseView):
    line_model = models.IssueConsumptionLine
    document_model = models.IssueConsumption
    feature_code = 'inventory.issues.consumption'
    serial_url_name = 'inventory:issue_consumption_line_serials'
    list_url_name = 'inventory:issue_consumption'
    edit_url_name = 'inventory:issue_consumption_edit'
    lock_url_name = 'inventory:issue_consumption_lock'


class IssueConsignmentLineSerialAssignmentView(IssueLineSerialAssignmentBaseView):
    line_model = models.IssueConsignmentLine
    document_model = models.IssueConsignment
    feature_code = 'inventory.issues.consignment'
    serial_url_name = 'inventory:issue_consignment_line_serials'
    list_url_name = 'inventory:issue_consignment'
    edit_url_name = 'inventory:issue_consignment_edit'
    lock_url_name = 'inventory:issue_consignment_lock'


class ReceiptSerialAssignmentBaseView(FeaturePermissionRequiredMixin, View):
    template_name = 'inventory/receipt_serial_assignment.html'
    model = None
    feature_code = None
    serial_url_name = ''
    list_url_name = ''
    edit_url_name = ''
    lock_url_name = ''

    def dispatch(self, request, *args, **kwargs):
        self.receipt = self.get_receipt()
        if self.receipt.item and self.receipt.item.has_lot_tracking != 1:
            messages.info(request, _('این کالا نیازی به سریال ندارد.'))
            return HttpResponseRedirect(reverse(self.list_url_name))
        return super().dispatch(request, *args, **kwargs)

    def get_receipt(self):
        queryset = self.model.objects.all()
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(self.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))

    def get_required_serials(self):
        try:
            return int(Decimal(self.receipt.quantity))
        except (InvalidOperation, TypeError):
            return None

    def get_context_data(self):
        required = self.get_required_serials()
        serials = self.receipt.serials.order_by('serial_code')
        context = {
            'receipt': self.receipt,
            'serials': serials,
            'required_serials': required,
            'serials_count': serials.count(),
            'list_url': reverse(self.list_url_name),
            'edit_url': reverse(self.edit_url_name, args=[self.receipt.pk]),
            'lock_url': reverse(self.lock_url_name, args=[self.receipt.pk]) if self.lock_url_name else None,
            'can_generate': not getattr(self.receipt, 'is_locked', 0),
            'missing_serials': max(required - serials.count(), 0) if required is not None else None,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if getattr(self.receipt, 'is_locked', 0):
            messages.info(request, _('رسید قفل شده و امکان تولید سریال جدید وجود ندارد.'))
            return HttpResponseRedirect(self.get_success_url())

        try:
            created = serial_service.generate_receipt_serials(self.receipt, user=request.user)
        except serial_service.SerialTrackingError as exc:
            messages.error(request, str(exc))
        else:
            if created:
                messages.success(request, _('%(count)s سریال جدید ایجاد شد.') % {'count': created})
            else:
                messages.info(request, _('سریال جدیدی برای ایجاد وجود نداشت.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(self.serial_url_name, args=[self.receipt.pk])


class ReceiptPermanentSerialAssignmentView(ReceiptSerialAssignmentBaseView):
    model = models.ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    serial_url_name = 'inventory:receipt_permanent_serials'
    list_url_name = 'inventory:receipt_permanent'
    edit_url_name = 'inventory:receipt_permanent_edit'
    lock_url_name = 'inventory:receipt_permanent_lock'


class ReceiptConsignmentSerialAssignmentView(ReceiptSerialAssignmentBaseView):
    model = models.ReceiptConsignment
    feature_code = 'inventory.receipts.consignment'
    serial_url_name = 'inventory:receipt_consignment_serials'
    list_url_name = 'inventory:receipt_consignment'
    edit_url_name = 'inventory:receipt_consignment_edit'
    lock_url_name = 'inventory:receipt_consignment_lock'


# ============================================================================
# Line-based Receipt Serial Assignment Views (Multi-line support)
# ============================================================================

class ReceiptLineSerialAssignmentBaseView(FeaturePermissionRequiredMixin, View):
    """Base view for managing serials for a specific receipt line."""
    template_name = 'inventory/receipt_serial_assignment.html'
    line_model = None
    document_model = None
    feature_code = None
    serial_url_name = ''
    list_url_name = ''
    edit_url_name = ''
    lock_url_name = ''

    def dispatch(self, request, *args, **kwargs):
        self.document = self.get_document()
        self.line = self.get_line()
        if self.line.item and self.line.item.has_lot_tracking != 1:
            messages.info(request, _('این کالا نیازی به سریال ندارد.'))
            return HttpResponseRedirect(reverse(self.edit_url_name, args=[self.document.pk]))
        return super().dispatch(request, *args, **kwargs)

    def get_document(self):
        queryset = self.document_model.objects.all()
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(self.document_model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))

    def get_line(self):
        queryset = self.line_model.objects.filter(document=self.document)
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(self.line_model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('line_id'))

    def get_required_serials(self):
        try:
            return int(Decimal(self.line.quantity))
        except (InvalidOperation, TypeError):
            return None

    def get_context_data(self):
        required = self.get_required_serials()
        serials = self.line.serials.order_by('serial_code')
        context = {
            'line': self.line,
            'document': self.document,
            'serials': serials,
            'required_serials': required,
            'serials_count': serials.count(),
            'list_url': reverse(self.list_url_name),
            'edit_url': reverse(self.edit_url_name, args=[self.document.pk]),
            'lock_url': reverse(self.lock_url_name, args=[self.document.pk]) if self.lock_url_name else None,
            'can_generate': not getattr(self.document, 'is_locked', 0),
            'missing_serials': max(required - serials.count(), 0) if required is not None else None,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if getattr(self.document, 'is_locked', 0):
            messages.info(request, _('رسید قفل شده و امکان تولید سریال جدید وجود ندارد.'))
            return HttpResponseRedirect(self.get_success_url())

        try:
            created = serial_service.generate_receipt_line_serials(self.line, user=request.user)
        except serial_service.SerialTrackingError as exc:
            messages.error(request, str(exc))
        else:
            if created:
                messages.success(request, _('%(count)s سریال جدید ایجاد شد.') % {'count': created})
            else:
                messages.info(request, _('سریال جدیدی برای ایجاد وجود نداشت.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(self.edit_url_name, args=[self.document.pk])


class ReceiptPermanentLineSerialAssignmentView(ReceiptLineSerialAssignmentBaseView):
    line_model = models.ReceiptPermanentLine
    document_model = models.ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    serial_url_name = 'inventory:receipt_permanent_line_serials'
    list_url_name = 'inventory:receipt_permanent'
    edit_url_name = 'inventory:receipt_permanent_edit'
    lock_url_name = 'inventory:receipt_permanent_lock'


class ReceiptConsignmentLineSerialAssignmentView(ReceiptLineSerialAssignmentBaseView):
    line_model = models.ReceiptConsignmentLine
    document_model = models.ReceiptConsignment
    feature_code = 'inventory.receipts.consignment'
    serial_url_name = 'inventory:receipt_consignment_line_serials'
    list_url_name = 'inventory:receipt_consignment'
    edit_url_name = 'inventory:receipt_consignment_edit'
    lock_url_name = 'inventory:receipt_consignment_lock'
