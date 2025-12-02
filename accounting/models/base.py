"""
Base models and mixins for accounting module.
"""
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shared.models import (
    ActivatableModel,
    CompanyScopedModel,
    LockableModel,
    MetadataModel,
    SortableModel,
    TimeStampedModel,
    ENABLED_FLAG_CHOICES,
)

from inventory.utils.codes import generate_sequential_code


POSITIVE_DECIMAL = MinValueValidator(Decimal("0"))


def get_fiscal_year_from_date(company_id: int, document_date) -> 'FiscalYear':
    """
    Get fiscal year for a given company and date.
    Returns the enabled fiscal year that contains the document_date.
    """
    from .fiscal_years import FiscalYear
    try:
        return FiscalYear.objects.get(
            company_id=company_id,
            start_date__lte=document_date,
            end_date__gte=document_date,
            is_enabled=1
        )
    except FiscalYear.DoesNotExist:
        return None
    except FiscalYear.MultipleObjectsReturned:
        # If multiple fiscal years match, return the most recent one
        return FiscalYear.objects.filter(
            company_id=company_id,
            start_date__lte=document_date,
            end_date__gte=document_date,
            is_enabled=1
        ).order_by('-start_date').first()


class AccountingBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    """Base model for all accounting models."""
    class Meta:
        abstract = True


class FiscalYearMixin(models.Model):
    """
    Mixin to auto-populate fiscal_year_id from document_date.
    Use this mixin for models that have document_date and need fiscal_year_id.
    """
    fiscal_year = models.ForeignKey(
        'FiscalYear',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_set',
        null=True,
        blank=True,
        help_text=_("Fiscal year for this document (auto-populated from document_date)"),
    )
    
    class Meta:
        abstract = True
    
    def get_document_date_field_name(self):
        """
        Override this method if document_date field has a different name.
        Default: 'document_date'
        """
        return 'document_date'
    
    def save(self, *args, **kwargs):
        """Auto-populate fiscal_year_id from document_date."""
        if not self.fiscal_year_id:
            date_field_name = self.get_document_date_field_name()
            document_date = getattr(self, date_field_name, None)
            
            if document_date and self.company_id:
                fiscal_year = get_fiscal_year_from_date(
                    company_id=self.company_id,
                    document_date=document_date
                )
                if fiscal_year:
                    self.fiscal_year = fiscal_year
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate that document_date is within fiscal_year range."""
        from django.core.exceptions import ValidationError
        
        date_field_name = self.get_document_date_field_name()
        document_date = getattr(self, date_field_name, None)
        
        if document_date and self.fiscal_year:
            if document_date < self.fiscal_year.start_date:
                raise ValidationError(
                    _("Document date (%(date)s) is before fiscal year start date (%(start)s).") % {
                        'date': document_date,
                        'start': self.fiscal_year.start_date,
                    }
                )
            if document_date > self.fiscal_year.end_date:
                raise ValidationError(
                    _("Document date (%(date)s) is after fiscal year end date (%(end)s).") % {
                        'date': document_date,
                        'end': self.fiscal_year.end_date,
                    }
                )
        
        super().clean()


class AccountingSortableModel(AccountingBaseModel, SortableModel):
    """Base model for sortable accounting entities."""
    class Meta:
        abstract = True


class AccountingDocumentBase(AccountingBaseModel, LockableModel, FiscalYearMixin):
    """Base model for accounting documents."""
    document_code = models.CharField(max_length=30, blank=True, editable=False)
    document_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True

