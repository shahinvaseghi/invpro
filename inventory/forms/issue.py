"""
Issue forms for inventory module.

This module contains forms for:
- Permanent Issues (with line items)
- Consumption Issues (with line items)
- Consignment Issues (with line items)
- Serial Assignment for Issues
"""
from collections import deque
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any

from django import forms
from django.forms import inlineformset_factory
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from inventory.models import (
    Item,
    ItemUnit,
    Warehouse,
    ItemSerial,
    IssuePermanent,
    IssueConsumption,
    IssueConsignment,
    IssuePermanentLine,
    IssueConsumptionLine,
    IssueConsignmentLine,
    ReceiptConsignment,
)
from inventory.services import serials as serial_service
from inventory import inventory_balance
from shared.models import CompanyUnit
from inventory.forms.base import (
    UNIT_CHOICES,
    IssueBaseForm,
    generate_document_code,
    BaseLineFormSet,
)

# WorkLine moved to production module
from shared.utils.modules import get_work_line_model
WorkLine = get_work_line_model()


class IssuePermanentForm(forms.ModelForm):
    """Header-only form for permanent issue documents with multi-line support."""

    department_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Organizational Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which company unit received this issue.'),
    )

    class Meta:
        model = IssuePermanent
        fields = [
            'document_code',
            'document_date',
            'department_unit',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
        }

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required and hidden (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
            self.fields['document_code'].widget = forms.HiddenInput()
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            self.fields['document_date'].widget = forms.HiddenInput()
            # Set initial value to today if creating new
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id and 'department_unit' in self.fields:
            self.fields['department_unit'].queryset = CompanyUnit.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('name')
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"

    def clean_document_code(self) -> str:
        """Auto-generate document_code if not provided."""
        document_code = self.cleaned_data.get('document_code')
        if not document_code:
            # Will be generated in save()
            return ''
        return document_code
    
    def clean_document_date(self):
        """Auto-generate document_date if not provided."""
        document_date = self.cleaned_data.get('document_date')
        if not document_date:
            # Will be generated in save()
            return timezone.now().date()
        return document_date
    
    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Set default values for document_code and document_date if not provided
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        return cleaned_data
    
    def save(self, commit: bool = True):
        """Save form instance."""
        instance = super().save(commit=False)
        
        # Ensure company_id is set
        if not instance.company_id and self.company_id:
            instance.company_id = self.company_id
        
        if not instance.document_code:
            instance.document_code = generate_document_code(IssuePermanent, instance.company_id, "ISP")
        if not instance.document_date:
            instance.document_date = timezone.now().date()

        department_unit = self.cleaned_data.get('department_unit')
        if department_unit:
            instance.department_unit = department_unit
            instance.department_unit_code = department_unit.public_code
        else:
            instance.department_unit = None
            instance.department_unit_code = ''
        
        if commit:
            instance.save()
        return instance


class IssueConsumptionForm(forms.ModelForm):
    """Header-only form for consumption issue documents with multi-line support."""

    class Meta:
        model = IssueConsumption
        fields = [
            'document_code',
            'document_date',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),  # Hidden, auto-generated
        }

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            # Set initial value for document_date
            if not self.instance.pk:
                self.fields['document_date'].initial = timezone.now().date()
    
    def clean_document_date(self):
        """Clean and provide default value for document_date."""
        date_value = self.cleaned_data.get('document_date')
        if not date_value:
            date_value = timezone.now().date()
        return date_value
    
    def clean_document_code(self) -> str:
        """Clean and provide default value for document_code."""
        code_value = self.cleaned_data.get('document_code')
        if not code_value:
            code_value = ''
        return code_value

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Set default values for document_code and document_date if not provided
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        return cleaned_data
    
    def save(self, commit: bool = True):
        """Save form instance."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(IssueConsumption, instance.company_id, "ISU")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        
        if commit:
            instance.save()
        return instance


class IssueConsignmentForm(forms.ModelForm):
    """Header-only form for consignment issue documents with multi-line support."""

    department_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Organizational Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which company unit received this consignment.'),
    )

    class Meta:
        model = IssueConsignment
        fields = [
            'document_code',
            'document_date',
            'department_unit',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
        }

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            # Set initial value for document_date
            if not self.instance.pk:
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id and 'department_unit' in self.fields:
            self.fields['department_unit'].queryset = CompanyUnit.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('name')
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
    
    def clean_document_date(self):
        """Clean and provide default value for document_date."""
        date_value = self.cleaned_data.get('document_date')
        if not date_value:
            date_value = timezone.now().date()
        return date_value
    
    def clean_document_code(self) -> str:
        """Clean and provide default value for document_code."""
        code_value = self.cleaned_data.get('document_code')
        if not code_value:
            code_value = ''
        return code_value

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Set default values for document_code and document_date if not provided
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        return cleaned_data
    
    def save(self, commit: bool = True):
        """Save form instance."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(IssueConsignment, instance.company_id, "ICN")
        if not instance.document_date:
            instance.document_date = timezone.now().date()

        department_unit = self.cleaned_data.get('department_unit')
        if department_unit:
            instance.department_unit = department_unit
            instance.department_unit_code = department_unit.public_code
        else:
            instance.department_unit = None
            instance.department_unit_code = ''
        
        if commit:
            instance.save()
        return instance


class IssueLineSerialAssignmentForm(forms.Form):
    """Form for assigning serials to a specific issue line."""
    
    serials = forms.ModelMultipleChoiceField(
        queryset=ItemSerial.objects.none(),
        required=False,
        label=_('Serial Numbers'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'serial-checkboxes'}),
    )

    def __init__(self, line, *args, **kwargs):
        """Initialize form with available serials."""
        super().__init__(*args, **kwargs)
        self.line = line
        self.company_id = line.company_id

        if line.item and line.item.has_lot_tracking == 1:
            # Base queryset: same company, same item, same warehouse
            queryset = ItemSerial.objects.filter(
                company_id=self.company_id,
                item=line.item,
                current_warehouse=line.warehouse,
            )
            # Only show:
            # 1. AVAILABLE serials (not yet assigned to any issue)
            # 2. RESERVED serials that belong to THIS specific line (allow editing)
            # Exclude: ISSUED, CONSUMED, DAMAGED, RETURNED serials (already issued)
            # Exclude: RESERVED serials that belong to other lines
            line_class_name = line.__class__.__name__
            line_pk = line.pk
            
            # Available serials OR reserved serials for this specific line
            status_filter = (
                Q(current_status=ItemSerial.Status.AVAILABLE) |
                Q(
                    current_status=ItemSerial.Status.RESERVED,
                    current_document_type=line_class_name,
                    current_document_id=line_pk,
                )
            )
            # Exclude already-issued/consumed/damaged/returned serials
            excluded_statuses = [
                ItemSerial.Status.ISSUED,
                ItemSerial.Status.CONSUMED,
                ItemSerial.Status.DAMAGED,
                ItemSerial.Status.RETURNED,
            ]
            status_filter = status_filter & ~Q(current_status__in=excluded_statuses)
            
            self.fields['serials'].queryset = queryset.filter(status_filter).order_by('serial_code')
            self.initial['serials'] = line.serials.values_list('pk', flat=True)
            try:
                required = int(Decimal(line.quantity))
            except (InvalidOperation, TypeError):
                required = None
            if required is not None:
                self.fields['serials'].help_text = _('%(count)s serial(s) required for this line.') % {'count': required}
        else:
            self.fields['serials'].help_text = _('This item does not require serial tracking.')
            self.fields['serials'].widget = forms.HiddenInput()

    def clean_serials(self) -> list:
        """Validate serial numbers."""
        serials = self.cleaned_data.get('serials')
        item = getattr(self.line, 'item', None)
        if not item or item.has_lot_tracking != 1:
            return ItemSerial.objects.none()

        try:
            required = int(Decimal(self.line.quantity))
        except (InvalidOperation, TypeError):
            raise forms.ValidationError(_('Quantity must be a whole number before assigning serials.'))

        if Decimal(self.line.quantity) != Decimal(required):
            raise forms.ValidationError(_('Quantity must be a whole number before assigning serials.'))

        selected = list(serials)
        if len(selected) != required:
            raise forms.ValidationError(
                _('You must select exactly %(count)s serial(s). Currently %(current)s selected.')
                % {'count': required, 'current': len(selected)}
            )

        invalid = [serial for serial in selected if serial.item_id != item.id]
        if invalid:
            raise forms.ValidationError(_('Selected serials do not belong to the requested item.'))

        return serials

    def save(self, user=None):
        """Save serial assignments."""
        line = self.line
        if line.item and line.item.has_lot_tracking == 1:
            previous_serial_ids = set(line.serials.values_list('id', flat=True))
            selected_serials = list(self.cleaned_data.get('serials'))
            line.serials.set(selected_serials)
            serial_service.sync_issue_line_serials(line, previous_serial_ids, user=user)
        else:
            line.serials.clear()
        return line


# ============================================================================
# Line Forms and Formsets (Multi-line support)
# ============================================================================

class IssueLineBaseForm(forms.ModelForm):
    """Base form for issue line items."""
    
    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        self._unit_factor = Decimal('1')
        self._entered_unit_value = None
        self._entered_quantity_value = None
        
        if self.company_id:
            if 'item' in self.fields:
                # For existing instances, include the current item even if disabled
                queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1)
                if getattr(self.instance, 'pk', None) and getattr(self.instance, 'item_id', None):
                    # Include the current item even if it's disabled
                    queryset = Item.objects.filter(
                        company_id=self.company_id
                    ).filter(
                        Q(is_enabled=1) | Q(pk=self.instance.item_id)
                    )
                self.fields['item'].queryset = queryset.order_by('name')
                self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
            
            if 'warehouse' in self.fields:
                # First, try to get item to set warehouse queryset based on allowed warehouses
                item = None
                if getattr(self.instance, 'item_id', None):
                    try:
                        item = Item.objects.filter(pk=self.instance.item_id, company_id=self.company_id).first()
                    except Exception:
                        pass
                
                if item:
                    # Set warehouse queryset based on item's allowed warehouses
                    self._set_warehouse_queryset(item=item)
                else:
                    # Fallback: For existing instances, include the current warehouse even if disabled
                    queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
                    if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                        # Include the current warehouse even if it's disabled
                        queryset = Warehouse.objects.filter(
                            company_id=self.company_id
                        ).filter(
                            Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                        )
                    self.fields['warehouse'].queryset = queryset.order_by('name')
                    self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
        
        # Set unit choices - this must be done before restoring initial values
        self._set_unit_choices()
        
        # Restore entered values if editing
        if not self.is_bound and getattr(self.instance, 'pk', None):
            # Get item first to set unit choices properly
            # Use item_id to avoid RelatedObjectDoesNotExist if document is missing
            item_id = getattr(self.instance, 'item_id', None)
            item = None
            if item_id:
                # Check if document exists before accessing item (to avoid RelatedObjectDoesNotExist)
                document_id = getattr(self.instance, 'document_id', None)
                if document_id:
                    try:
                        # Try to get item directly by item_id to avoid accessing through instance
                        item = Item.objects.filter(pk=item_id, company_id=self.company_id).first()
                        if not item:
                            # Fallback: try to access through instance
                            item = getattr(self.instance, 'item', None)
                    except Exception:
                        pass
                else:
                    # Try to get item directly by item_id
                    try:
                        item = Item.objects.filter(pk=item_id, company_id=self.company_id).first()
                    except Exception:
                        pass
            
            if item and 'unit' in self.fields:
                # Set unit choices based on item
                self._set_unit_choices(item=item)
            
            # Set warehouse queryset based on item (for existing instances)
            if item and 'warehouse' in self.fields:
                self._set_warehouse_queryset(item=item)
            
            # Get unit value from entered_unit or unit (prioritize entered_unit for display)
            entry_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
            if 'unit' in self.fields and entry_unit:
                # Ensure the unit is in choices, if not add it
                unit_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in unit_choices]
                if entry_unit not in unit_codes:
                    # Add current unit to choices if not present
                    self.fields['unit'].choices = unit_choices + [(entry_unit, entry_unit)]
                
                # Django ChoiceField uses instance.field for display when editing
                # So we need to set instance.unit to the entered_unit for proper display
                if hasattr(self.instance, 'unit'):
                    # Store the original unit if we're changing it
                    if not hasattr(self.instance, '_original_unit'):
                        self.instance._original_unit = self.instance.unit
                    # Set unit to entered_unit for display purposes
                    self.instance.unit = entry_unit
                
                # Also set initial as backup
                self.initial['unit'] = entry_unit
            
            if 'quantity' in self.fields and getattr(self.instance, 'entered_quantity', None) is not None:
                self.initial['quantity'] = self.instance.entered_quantity
    
    def clean_item(self) -> Optional[Item]:
        """Clean item and update unit and warehouse choices."""
        item = self.cleaned_data.get('item')
        
        # Update unit choices immediately after item is cleaned
        # This ensures choices are set before unit validation
        if item:
            self._set_unit_choices(item=item)
            # Also update warehouse queryset based on allowed warehouses
            self._set_warehouse_queryset(item=item)
        
        return item
    
    def _get_item_allowed_warehouses(self, item: Optional[Item]) -> list:
        """Get list of allowed warehouses for an item."""
        if not item:
            return []
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]
        # IMPORTANT: If no warehouses configured, this means the item CANNOT be received anywhere
        # Only return warehouses if explicitly configured
        # This enforces strict warehouse restrictions
        return [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]
    
    def _set_warehouse_queryset(self, item: Optional[Item] = None) -> None:
        """Set warehouse field queryset based on selected item's allowed warehouses."""
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        
        # If item not provided, try to resolve it
        if item is None:
            item = self._resolve_item()
        
        if item:
            allowed_ids = [int(option['value']) for option in self._get_item_allowed_warehouses(item)]
            if allowed_ids:
                # Only show allowed warehouses
                # For existing instances, include the current warehouse even if disabled
                queryset = Warehouse.objects.filter(pk__in=allowed_ids, is_enabled=1)
                if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                    # Include the current warehouse even if it's disabled
                    queryset = Warehouse.objects.filter(
                        pk__in=allowed_ids
                    ).filter(
                        Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                    )
                warehouse_field.queryset = queryset.order_by('name')
                return
            else:
                # No warehouses configured - show empty queryset (will show error in validation)
                # But include current warehouse if editing
                if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                    warehouse_field.queryset = Warehouse.objects.filter(pk=self.instance.warehouse_id)
                else:
                    warehouse_field.queryset = Warehouse.objects.none()
                return
        
        # Fallback: show all warehouses in company if no item selected
        # For existing instances, include the current warehouse even if disabled
        queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
        if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
            # Include the current warehouse even if it's disabled
            queryset = Warehouse.objects.filter(
                company_id=self.company_id
            ).filter(
                Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
            )
        warehouse_field.queryset = queryset.order_by('name')
        if self.company_id:
            # For existing instances, include the current warehouse even if disabled
            queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
            if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                # Include the current warehouse even if it's disabled
                queryset = Warehouse.objects.filter(
                    company_id=self.company_id
                ).filter(
                    Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                )
            warehouse_field.queryset = queryset.order_by('name')
    
    def clean_warehouse(self) -> Optional[Warehouse]:
        """Validate warehouse against item's allowed warehouses."""
        warehouse = self.cleaned_data.get('warehouse')
        item = self.cleaned_data.get('item')
        
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    raise forms.ValidationError(
                        _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.')
                    )
            else:
                # No warehouses configured for this item - this is an error
                raise forms.ValidationError(
                    _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.')
                )
        
        return warehouse
    
    def clean_unit(self) -> str:
        """Validate unit and update choices based on selected item."""
        unit = self.cleaned_data.get('unit')
        
        # Get item from cleaned_data (it should already be cleaned by clean_item)
        item = self.cleaned_data.get('item')
        
        # If no item is selected, don't validate unit (allow empty)
        if not item:
            return unit
        
        # Update unit choices again (in case clean_item wasn't called or item changed)
        self._set_unit_choices(item=item)
        
        # Now validate unit against allowed units
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        allowed.add(item.default_unit)
        
        # Also check current choices in the field
        unit_field = self.fields.get('unit')
        if unit_field:
            choice_values = {choice[0] for choice in unit_field.choices if choice[0]}
            allowed.update(choice_values)
        
        # If unit is provided and not in allowed list, raise error
        if unit and unit not in allowed:
            raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        
        return unit
    
    def _resolve_item(self, candidate: Any = None) -> Optional[Item]:
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        # Check form data (POST)
        if self.data:
            item_key = None
            for key in self.data.keys():
                if key.endswith('-item'):
                    item_key = key
                    break
            if item_key:
                try:
                    item_id = self.data.get(item_key)
                    if item_id:
                        return Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        # Check instance (for edit mode)
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        # Check initial data (for new forms with pre-selected item)
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None
    
    def _get_item_allowed_units(self, item: Optional[Item]) -> list:
        """Get list of allowed units for an item."""
        if not item:
            return []
        codes = []
        
        def add(code: str) -> None:
            if code and code not in codes:
                codes.append(code)
        
        # Add default and primary units (always add both, even if same or None)
        add(item.default_unit)
        add(item.primary_unit)
        
        # Add units from ItemUnit conversions
        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]
    
    def _set_unit_choices(self, item: Optional[Item] = None) -> None:
        """Set unit field choices based on selected item."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        
        # If item not provided, try to resolve it
        if item is None:
            item = self._resolve_item()
        
        # Get current unit from instance if editing
        current_unit = None
        if not self.is_bound and getattr(self.instance, 'pk', None):
            current_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
        
        # Also get unit from cleaned_data if available (for validation)
        if not current_unit and hasattr(self, 'cleaned_data'):
            current_unit = self.cleaned_data.get('unit')
        
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            allowed_codes = [code for code, _ in allowed]
            
            # Add current unit if editing and it's not in allowed list
            if current_unit and current_unit not in allowed_codes:
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                allowed.append((current_unit, label_map.get(current_unit, current_unit)))
            
            # If no units found, add default_unit as fallback
            if not allowed and item.default_unit:
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                allowed.append((item.default_unit, label_map.get(item.default_unit, item.default_unit)))
            
            unit_field.choices = [placeholder] + allowed
        else:
            # No item selected, but if editing and have current_unit, add it
            if current_unit:
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                unit_field.choices = [placeholder, (current_unit, label_map.get(current_unit, current_unit))]
            else:
                unit_field.choices = [placeholder]
    
    def _get_unit_factor(self, item: Item, unit_code: str) -> Decimal:
        """Calculate conversion factor from unit_code to item's default_unit."""
        default_unit = item.default_unit
        if not unit_code or unit_code == default_unit:
            return Decimal('1')
        
        graph = {}
        for conversion in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            from_qty = conversion.from_quantity
            to_qty = conversion.to_quantity
            if from_qty in (None, 0) or to_qty in (None, 0):
                continue
            graph.setdefault(conversion.from_unit, []).append((conversion.to_unit, to_qty / from_qty))
            graph.setdefault(conversion.to_unit, []).append((conversion.from_unit, from_qty / to_qty))
        
        visited = set()
        queue = deque([(unit_code, Decimal('1'))])
        while queue:
            unit, factor = queue.popleft()
            if unit == default_unit:
                return factor
            if unit in visited:
                continue
            visited.add(unit)
            for neighbor, ratio in graph.get(unit, []):
                queue.append((neighbor, factor * ratio))
        
        return Decimal('1')
    
    def _validate_unit(self, cleaned_data: Dict[str, Any]) -> None:
        """Validate unit and calculate conversion factor."""
        self._unit_factor = Decimal('1')
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        unit = cleaned_data.get('unit') or item.default_unit
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        allowed.add(item.default_unit)
        if unit not in allowed:
            self.add_error('unit', _('Selected unit is not configured for this item.'))
        factor = self._get_unit_factor(item, unit)
        self._unit_factor = factor
        self._entered_unit_value = unit
        cleaned_data['unit'] = item.default_unit
    
    def _normalize_quantity(self, cleaned_data: Dict[str, Any]) -> None:
        """Normalize quantity to base unit and save entered value."""
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        quantity = cleaned_data.get('quantity')
        if not item or quantity in (None, ''):
            return
        factor = getattr(self, '_unit_factor', Decimal('1'))
        if not isinstance(quantity, Decimal):
            try:
                quantity = Decimal(str(quantity))
            except (InvalidOperation, TypeError):
                return
        self._entered_quantity_value = quantity
        cleaned_data['quantity'] = quantity * factor
        cleaned_data['unit'] = item.default_unit
        self.instance.unit = item.default_unit
        self.instance.quantity = cleaned_data['quantity']
    
    def clean(self) -> Dict[str, Any]:
        """Validate and normalize form data."""
        cleaned_data = super().clean()
        
        # Check if form is empty (for inline formsets, empty forms should be skipped)
        item = cleaned_data.get('item')
        if not item:
            # If this is an empty form in a formset, mark all fields as empty
            # Django will skip it during save()
            return cleaned_data
        
        # Validate warehouse against item's allowed warehouses
        warehouse = cleaned_data.get('warehouse')
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    self.add_error('warehouse', _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.'))
            else:
                # No warehouses configured for this item - this is an error
                self.add_error('warehouse', _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.'))
        
        self._validate_unit(cleaned_data)
        self._normalize_quantity(cleaned_data)
        
        # Validate inventory balance for issue forms (only for IssueLineBaseForm subclasses)
        if warehouse and item and self.company_id and hasattr(self, '_normalize_quantity'):
            # Only validate if this is an issue form (not receipt)
            # Check if this form is for an issue by checking the model
            from inventory.models import IssuePermanentLine, IssueConsumptionLine, IssueConsignmentLine
            if isinstance(self.instance, (IssuePermanentLine, IssueConsumptionLine, IssueConsignmentLine)) or \
               (hasattr(self, 'Meta') and hasattr(self.Meta, 'model') and 
                issubclass(self.Meta.model, (IssuePermanentLine, IssueConsumptionLine, IssueConsignmentLine))):
                quantity = cleaned_data.get('quantity')
                if quantity:
                    try:
                        from inventory import inventory_balance
                        
                        # Calculate current balance
                        balance_info = inventory_balance.calculate_item_balance(
                            company_id=self.company_id,
                            warehouse_id=warehouse.id,
                            item_id=item.id,
                            as_of_date=timezone.now().date()
                        )
                        
                        current_balance = Decimal(str(balance_info['current_balance']))
                        issue_quantity = Decimal(str(quantity))
                        
                        # If editing, add back the old quantity (if it exists)
                        if self.instance.pk:
                            old_quantity = Decimal(str(self.instance.quantity or 0))
                            available_balance = current_balance + old_quantity
                        else:
                            available_balance = current_balance
                        
                        # Check if we have enough inventory
                        if issue_quantity > available_balance:
                            self.add_error(
                                'quantity',
                                _('موجودی کافی نیست. موجودی فعلی: %(balance)s، مقدار درخواستی: %(requested)s') % {
                                    'balance': available_balance,
                                    'requested': issue_quantity
                                }
                            )
                    except Exception:
                        # If balance calculation fails, don't block the form
                        # (might be due to missing stocktaking baseline)
                        pass
        
        return cleaned_data
    
    def save(self, commit: bool = True):
        """Save form instance with entered values."""
        instance = super().save(commit=False)
        
        # Save entered unit and quantity
        entered_unit = self._entered_unit_value or getattr(instance, 'entered_unit', '') or instance.unit
        instance.entered_unit = entered_unit
        if self._entered_quantity_value is not None:
            instance.entered_quantity = self._entered_quantity_value
        elif instance.entered_quantity is None:
            instance.entered_quantity = instance.quantity
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssuePermanentLineForm(IssueLineBaseForm):
    """Form for permanent issue line items."""
    
    destination_type = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('واحد کاری'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('واحد کاری که این حواله را دریافت می‌کند.'),
    )
    
    class Meta:
        model = IssuePermanentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'destination_type', 'destination_id', 'destination_code', 'reason_code',
            'unit_price', 'currency', 'tax_amount', 'discount_amount', 'total_amount',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'destination_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination_code': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, company_id=company_id, **kwargs)
        self._update_destination_type_queryset()
    
    def _update_destination_type_queryset(self) -> None:
        """Update destination_type (CompanyUnit) queryset after company_id is set."""
        if self.company_id and 'destination_type' in self.fields:
            self.fields['destination_type'].queryset = CompanyUnit.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('name')
            self.fields['destination_type'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            self.fields['destination_type'].empty_label = _("--- انتخاب کنید ---")
            
            # If editing and instance has destination_type, try to find matching CompanyUnit
            if not self.is_bound and getattr(self.instance, 'pk', None):
                if self.instance.destination_type == 'company_unit' and self.instance.destination_id:
                    # If destination_type is 'company_unit', use destination_id
                    try:
                        company_unit = CompanyUnit.objects.get(
                            company_id=self.company_id,
                            id=self.instance.destination_id
                        )
                        self.initial['destination_type'] = company_unit.id
                    except CompanyUnit.DoesNotExist:
                        pass
                elif self.instance.destination_type and not self.instance.destination_id:
                    # Try to find CompanyUnit by code (for old data)
                    try:
                        company_unit = CompanyUnit.objects.get(
                            company_id=self.company_id,
                            public_code=self.instance.destination_type
                        )
                        self.initial['destination_type'] = company_unit.id
                    except CompanyUnit.DoesNotExist:
                        pass
    
    def clean_destination_type(self) -> Optional[CompanyUnit]:
        """Validate destination_type (CompanyUnit)."""
        company_unit = self.cleaned_data.get('destination_type')
        # Store company_unit for later use in save()
        self._destination_company_unit = company_unit
        return company_unit
    
    def save(self, commit: bool = True):
        """Save with destination_type handling."""
        instance = super().save(commit=False)
        
        # Handle destination_type (CompanyUnit)
        company_unit = getattr(self, '_destination_company_unit', None)
        if company_unit is None:
            # Try to get from cleaned_data if _destination_company_unit not set
            company_unit = self.cleaned_data.get('destination_type')
        
        if company_unit and isinstance(company_unit, CompanyUnit):
            instance.destination_type = 'company_unit'
            instance.destination_id = company_unit.id
            instance.destination_code = company_unit.public_code
        else:
            # Set default empty value if not provided
            instance.destination_type = ''
            instance.destination_id = None
            instance.destination_code = ''
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssueConsumptionLineForm(IssueLineBaseForm):
    """Form for consumption issue line items."""
    
    destination_type_choice = forms.ChoiceField(
        choices=[
            ('', _('--- انتخاب کنید ---')),
            ('company_unit', _('واحد کاری (Company Unit)')),
        ],
        required=False,
        label=_('نوع مقصد'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_destination_type_choice'}),
        help_text=_('ابتدا نوع مقصد را انتخاب کنید.'),
    )
    
    destination_company_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('واحد کاری'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_destination_company_unit'}),
    )
    
    destination_work_line = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__ if WorkLine is available
        required=False,
        label=_('خط کاری'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_destination_work_line'}),
    )
    
    work_line = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__ if WorkLine is available
        required=False,
        label=_('Work Line'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = IssueConsumptionLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'destination_type_choice', 'destination_company_unit', 'destination_work_line',  # Destination fields
            'consumption_type', 'work_line',  # consumption_type is hidden, managed by destination_type_choice
            'reference_document_type', 'reference_document_id', 'reference_document_code',
            'production_transfer_id', 'production_transfer_code',
            'unit_cost', 'total_cost', 'cost_center_code',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'consumption_type': forms.HiddenInput(),  # Hidden, set automatically based on destination_type_choice
            'work_line': forms.Select(attrs={'class': 'form-control'}),
            'reference_document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_document_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference_document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'production_transfer_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'production_transfer_code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'cost_center_code': forms.HiddenInput(),  # Hidden, used internally for company_unit storage
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, company_id=company_id, **kwargs)
        # Update querysets if company_id is available
        self._update_querysets_after_company_id()
    
    def _update_querysets_after_company_id(self) -> None:
        """Update querysets after company_id is set (called from BaseLineFormSet)."""
        if not self.company_id:
            return
        
        # Add work_line option to destination_type_choice if production module is installed
        if WorkLine and 'destination_type_choice' in self.fields:
            # Add work_line option to choices dynamically
            current_choices = list(self.fields['destination_type_choice'].choices)
            work_line_choice = ('work_line', _('خط کاری (Work Line)'))
            if work_line_choice not in current_choices:
                # Insert before the last empty choice
                if current_choices and current_choices[-1][0] == '':
                    current_choices.insert(-1, work_line_choice)
                else:
                    current_choices.append(work_line_choice)
                self.fields['destination_type_choice'].choices = current_choices
        
        # Set work_line queryset (only if production module is installed)
        if 'work_line' in self.fields and WorkLine:
            self.fields['work_line'].queryset = WorkLine.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('warehouse__name', 'name')
            self.fields['work_line'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name} ({obj.warehouse.name if obj.warehouse else ''})"
        elif 'work_line' in self.fields:
            # If production module is not installed, hide work_line field
            self.fields['work_line'].widget = forms.HiddenInput()
            self.fields['work_line'].required = False
        
        # Set destination_company_unit queryset
        if 'destination_company_unit' in self.fields:
            self.fields['destination_company_unit'].queryset = CompanyUnit.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('name')
            self.fields['destination_company_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            self.fields['destination_company_unit'].empty_label = _("--- انتخاب کنید ---")
        
        # Set destination_work_line queryset (only if production module is installed)
        if 'destination_work_line' in self.fields and WorkLine:
            self.fields['destination_work_line'].queryset = WorkLine.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).select_related('warehouse').order_by('warehouse__name', 'name')
            self.fields['destination_work_line'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name} ({obj.warehouse.name if obj.warehouse else ''})"
            self.fields['destination_work_line'].empty_label = _("--- انتخاب کنید ---")
        elif 'destination_work_line' in self.fields:
            # If production module is not installed, hide destination_work_line field
            self.fields['destination_work_line'].widget = forms.HiddenInput()
            self.fields['destination_work_line'].required = False
        
        # If editing, set initial values based on consumption_type
        if not self.is_bound and getattr(self.instance, 'pk', None):
            dest_type = getattr(self.instance, 'consumption_type', None)
            # Set consumption_type initial value (hidden field)
            if dest_type:
                self.initial['consumption_type'] = dest_type
            
            if dest_type == 'company_unit':
                # Try to get company unit from cost_center_code (where we stored it)
                if hasattr(self.instance, 'cost_center_code') and self.instance.cost_center_code:
                    try:
                        unit = CompanyUnit.objects.get(
                            company_id=self.company_id,
                            public_code=self.instance.cost_center_code
                        )
                        self.initial['destination_type_choice'] = 'company_unit'
                        self.initial['destination_company_unit'] = unit.id
                        # Show the company unit field container (JavaScript will handle display)
                    except CompanyUnit.DoesNotExist:
                        pass
            elif dest_type == 'work_line' and self.instance.work_line and WorkLine:
                self.initial['destination_type_choice'] = 'work_line'
                self.initial['destination_work_line'] = self.instance.work_line.id
                # Show the work line field container (JavaScript will handle display)
    
    def clean(self) -> Dict[str, Any]:
        """Validate destination selection."""
        cleaned_data = super().clean()
        dest_type_choice = cleaned_data.get('destination_type_choice')
        dest_company_unit = cleaned_data.get('destination_company_unit')
        dest_work_line = cleaned_data.get('destination_work_line')
        
        # Check if item is selected (required for validation)
        item = cleaned_data.get('item')
        if not item:
            # If no item, skip destination validation (form will be skipped anyway)
            return cleaned_data
        
        # Require destination_type_choice to be selected
        if not dest_type_choice:
            self.add_error('destination_type_choice', _('Please select a destination type.'))
            return cleaned_data
        
        # Validate based on selected destination type
        if dest_type_choice == 'company_unit':
            if not dest_company_unit:
                self.add_error('destination_company_unit', _('Please select a company unit.'))
        elif dest_type_choice == 'work_line':
            if not WorkLine:
                # Production module not installed, work_line option not available
                self.add_error('destination_type_choice', _('Work line option is not available. Production module is not installed.'))
            elif not dest_work_line:
                self.add_error('destination_work_line', _('Please select a work line.'))
        
        return cleaned_data
    
    def save(self, commit: bool = True):
        """Save with destination handling."""
        instance = super().save(commit=False)
        
        dest_type_choice = self.cleaned_data.get('destination_type_choice')
        dest_company_unit = self.cleaned_data.get('destination_company_unit')
        dest_work_line = self.cleaned_data.get('destination_work_line')
        
        # Set destination based on choice
        if dest_type_choice == 'company_unit' and dest_company_unit:
            instance.consumption_type = 'company_unit'
            # For company_unit, we store the unit ID in a way we can retrieve it later
            # Since IssueConsumptionLine doesn't have destination_id, we can store it in cost_center_code as temporary solution
            # Or we need to check if model has these fields
            instance.work_line = None
            # Store company unit code in cost_center_code for now (or we could add destination fields to model)
            if hasattr(instance, 'cost_center_code'):
                instance.cost_center_code = dest_company_unit.public_code
        elif dest_type_choice == 'work_line' and dest_work_line and WorkLine:
            instance.consumption_type = 'work_line'
            instance.work_line = dest_work_line
            if hasattr(instance, 'cost_center_code') and instance.cost_center_code:
                # Clear cost_center_code if it was used for company_unit
                try:
                    CompanyUnit.objects.get(public_code=instance.cost_center_code)
                    instance.cost_center_code = ''
                except CompanyUnit.DoesNotExist:
                    pass
        else:
            # If no choice made, this should have been caught by validation
            # But if we reach here, it means validation didn't catch it
            # This should not happen, but we need to handle it
            # Don't save if consumption_type is not set (validation should prevent this)
            if not getattr(instance, 'consumption_type', None) and not instance.pk:
                # This is a new instance without consumption_type - validation should have caught this
                # We'll let the database constraint catch it if validation didn't
                pass
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssueConsignmentLineForm(IssueLineBaseForm):
    """Form for consignment issue line items."""
    
    consignment_receipt = forms.ModelChoiceField(
        queryset=ReceiptConsignment.objects.none(),
        required=False,
        label=_('Consignment Receipt'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which consignment receipt this issue is related to.'),
    )
    
    destination_type = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('واحد کاری'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('واحد کاری که این حواله را دریافت می‌کند.'),
    )
    
    class Meta:
        model = IssueConsignmentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'consignment_receipt',
            'destination_type', 'destination_id', 'destination_code', 'reason_code',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'destination_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination_code': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, company_id=company_id, **kwargs)
        self._update_destination_type_queryset()
    
    def _update_destination_type_queryset(self) -> None:
        """Update destination_type (CompanyUnit) queryset after company_id is set."""
        if self.company_id:
            if 'consignment_receipt' in self.fields:
                self.fields['consignment_receipt'].queryset = ReceiptConsignment.objects.filter(
                    company_id=self.company_id
                ).order_by('-document_date', 'document_code')
                self.fields['consignment_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
            
            # Set destination_type (CompanyUnit) queryset
            if 'destination_type' in self.fields:
                self.fields['destination_type'].queryset = CompanyUnit.objects.filter(
                    company_id=self.company_id, is_enabled=1
                ).order_by('name')
                self.fields['destination_type'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
                self.fields['destination_type'].empty_label = _("--- انتخاب کنید ---")
                
                # If editing and instance has destination_type, try to find matching CompanyUnit
                if not self.is_bound and getattr(self.instance, 'pk', None):
                    if self.instance.destination_type == 'company_unit' and self.instance.destination_id:
                        try:
                            company_unit = CompanyUnit.objects.get(
                                company_id=self.company_id,
                                id=self.instance.destination_id
                            )
                            self.initial['destination_type'] = company_unit.id
                        except CompanyUnit.DoesNotExist:
                            pass
                    elif self.instance.destination_type and not self.instance.destination_id:
                        try:
                            company_unit = CompanyUnit.objects.get(
                                company_id=self.company_id,
                                public_code=self.instance.destination_type
                            )
                            self.initial['destination_type'] = company_unit.id
                        except CompanyUnit.DoesNotExist:
                            pass
    
    def clean_destination_type(self) -> Optional[CompanyUnit]:
        """Validate destination_type (CompanyUnit)."""
        company_unit = self.cleaned_data.get('destination_type')
        self._destination_company_unit = company_unit
        return company_unit
    
    def save(self, commit: bool = True):
        """Save with destination_type handling."""
        instance = super().save(commit=False)
        
        # Handle destination_type (CompanyUnit)
        company_unit = getattr(self, '_destination_company_unit', None)
        if company_unit is None:
            # Try to get from cleaned_data if _destination_company_unit not set
            company_unit = self.cleaned_data.get('destination_type')
        
        if company_unit and isinstance(company_unit, CompanyUnit):
            instance.destination_type = 'company_unit'
            instance.destination_id = company_unit.id
            instance.destination_code = company_unit.public_code
        else:
            instance.destination_type = ''
            instance.destination_id = None
            instance.destination_code = ''
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


# Create formsets
IssuePermanentLineFormSet = inlineformset_factory(
    IssuePermanent,
    IssuePermanentLine,
    form=IssuePermanentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

IssueConsumptionLineFormSet = inlineformset_factory(
    IssueConsumption,
    IssueConsumptionLine,
    form=IssueConsumptionLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

IssueConsignmentLineFormSet = inlineformset_factory(
    IssueConsignment,
    IssueConsignmentLine,
    form=IssueConsignmentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

