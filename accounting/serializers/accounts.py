"""
Serializers for Account models (GL, Sub, Tafsili).
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ..models import Account, TafsiliHierarchy


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model (all levels)."""
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    account_level_display = serializers.CharField(source='get_account_level_display', read_only=True)
    normal_balance_display = serializers.CharField(source='get_normal_balance_display', read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id',
            'account_code',
            'account_name',
            'account_name_en',
            'account_type',
            'account_type_display',
            'account_level',
            'account_level_display',
            'normal_balance',
            'normal_balance_display',
            'opening_balance',
            'current_balance',
            'description',
            'is_enabled',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'current_balance', 'created_at', 'updated_at']


class GLAccountSerializer(serializers.ModelSerializer):
    """Serializer for GL Accounts (level 1)."""
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    normal_balance_display = serializers.CharField(source='get_normal_balance_display', read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id',
            'account_code',
            'account_name',
            'account_name_en',
            'account_type',
            'account_type_display',
            'normal_balance',
            'normal_balance_display',
            'opening_balance',
            'current_balance',
            'description',
            'is_enabled',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'account_level', 'current_balance', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure account_level is 1."""
        data['account_level'] = 1
        return data


class SubAccountSerializer(serializers.ModelSerializer):
    """Serializer for Sub Accounts (level 2)."""
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    normal_balance_display = serializers.CharField(source='get_normal_balance_display', read_only=True)
    gl_accounts = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Account.objects.filter(account_level=1),
        required=True,
        help_text=_("List of GL account IDs this sub account belongs to"),
    )
    
    class Meta:
        model = Account
        fields = [
            'id',
            'account_code',
            'account_name',
            'account_name_en',
            'account_type',
            'account_type_display',
            'normal_balance',
            'normal_balance_display',
            'opening_balance',
            'current_balance',
            'description',
            'is_enabled',
            'gl_accounts',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'account_level', 'current_balance', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure account_level is 2 and validate gl_accounts."""
        data['account_level'] = 2
        gl_accounts = data.get('gl_accounts', [])
        if not gl_accounts:
            raise serializers.ValidationError({
                'gl_accounts': _('At least one GL account must be selected.')
            })
        # Inherit account_type and normal_balance from first GL account
        if gl_accounts:
            first_gl = gl_accounts[0]
            if 'account_type' not in data:
                data['account_type'] = first_gl.account_type
            if 'normal_balance' not in data:
                data['normal_balance'] = first_gl.normal_balance
        return data


class TafsiliAccountSerializer(serializers.ModelSerializer):
    """Serializer for Tafsili Accounts (level 3)."""
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    normal_balance_display = serializers.CharField(source='get_normal_balance_display', read_only=True)
    sub_accounts = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Account.objects.filter(account_level=2),
        required=False,
        help_text=_("List of Sub account IDs this tafsili account belongs to"),
    )
    
    class Meta:
        model = Account
        fields = [
            'id',
            'account_code',
            'account_name',
            'account_name_en',
            'account_type',
            'account_type_display',
            'normal_balance',
            'normal_balance_display',
            'opening_balance',
            'current_balance',
            'description',
            'is_enabled',
            'sub_accounts',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'account_level', 'current_balance', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure account_level is 3."""
        data['account_level'] = 3
        return data


class TafsiliHierarchySerializer(serializers.ModelSerializer):
    """Serializer for Tafsili Hierarchy (multi-level tafsili)."""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    tafsili_account_name = serializers.CharField(source='tafsili_account.account_name', read_only=True)
    full_path = serializers.CharField(read_only=True)
    
    class Meta:
        model = TafsiliHierarchy
        fields = [
            'id',
            'code',
            'name',
            'name_en',
            'parent',
            'parent_name',
            'tafsili_account',
            'tafsili_account_name',
            'level',
            'sort_order',
            'description',
            'is_enabled',
            'full_path',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'level', 'full_path', 'created_at', 'updated_at']

