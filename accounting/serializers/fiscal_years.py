"""
Serializers for Fiscal Year and Period models.
"""
from rest_framework import serializers
from ..models import FiscalYear, Period


class PeriodSerializer(serializers.ModelSerializer):
    """Serializer for Period model."""
    fiscal_year_name = serializers.CharField(source='fiscal_year.fiscal_year_name', read_only=True)
    is_closed_display = serializers.CharField(source='get_is_closed_display', read_only=True)
    
    class Meta:
        model = Period
        fields = [
            'id',
            'fiscal_year',
            'fiscal_year_name',
            'period_code',
            'period_name',
            'start_date',
            'end_date',
            'is_closed',
            'is_closed_display',
            'closed_at',
            'closed_by',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'closed_at', 'created_at', 'updated_at']


class FiscalYearSerializer(serializers.ModelSerializer):
    """Serializer for Fiscal Year model."""
    periods = PeriodSerializer(many=True, read_only=True)
    is_current_display = serializers.CharField(source='get_is_current_display', read_only=True)
    is_closed_display = serializers.CharField(source='get_is_closed_display', read_only=True)
    
    class Meta:
        model = FiscalYear
        fields = [
            'id',
            'fiscal_year_code',
            'fiscal_year_name',
            'start_date',
            'end_date',
            'is_current',
            'is_current_display',
            'is_closed',
            'is_closed_display',
            'closed_at',
            'closed_by',
            'periods',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'closed_at', 'created_at', 'updated_at']

