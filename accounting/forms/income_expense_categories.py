"""
Forms for Income/Expense Category management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import IncomeExpenseCategory


class IncomeExpenseCategoryForm(forms.ModelForm):
    """Form for creating/editing income/expense categories."""
    
    class Meta:
        model = IncomeExpenseCategory
        fields = [
            'category_type',
            'category_name',
            'category_name_en',
            'description',
            'is_enabled',
        ]
        widgets = {
            'category_type': forms.Select(attrs={'class': 'form-control'}),
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'category_type': _('نوع دسته‌بندی'),
            'category_name': _('نام دسته‌بندی'),
            'category_name_en': _('نام دسته‌بندی (انگلیسی)'),
            'description': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
        help_texts = {
            'category_type': _('نوع دسته‌بندی: درآمد یا هزینه'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if company_id:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass

