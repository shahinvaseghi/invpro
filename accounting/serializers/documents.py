"""
Serializers for Accounting Document models.
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ..models import AccountingDocument, AccountingDocumentLine, DocumentAttachment


class AccountingDocumentLineSerializer(serializers.ModelSerializer):
    """Serializer for Accounting Document Line."""
    gl_account_code = serializers.CharField(source='gl_account.account_code', read_only=True)
    gl_account_name = serializers.CharField(source='gl_account.account_name', read_only=True)
    sub_account_code = serializers.CharField(source='sub_account.account_code', read_only=True, allow_null=True)
    sub_account_name = serializers.CharField(source='sub_account.account_name', read_only=True, allow_null=True)
    tafsili_account_code = serializers.CharField(source='tafsili_account.account_code', read_only=True, allow_null=True)
    tafsili_account_name = serializers.CharField(source='tafsili_account.account_name', read_only=True, allow_null=True)
    
    class Meta:
        model = AccountingDocumentLine
        fields = [
            'id',
            'document',
            'line_number',
            'gl_account',
            'gl_account_code',
            'gl_account_name',
            'sub_account',
            'sub_account_code',
            'sub_account_name',
            'tafsili_account',
            'tafsili_account_code',
            'tafsili_account_name',
            'description',
            'debit',
            'credit',
            'sort_order',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccountingDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Accounting Document."""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = AccountingDocumentLineSerializer(many=True, read_only=True)
    fiscal_year_name = serializers.CharField(source='fiscal_year.year_name', read_only=True)
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = AccountingDocument
        fields = [
            'id',
            'document_number',
            'document_code',
            'document_date',
            'document_type',
            'document_type_display',
            'fiscal_year',
            'fiscal_year_name',
            'period',
            'description',
            'reference_number',
            'reference_type',
            'reference_id',
            'total_debit',
            'total_credit',
            'status',
            'status_display',
            'posted_at',
            'posted_by',
            'posted_by_username',
            'locked_at',
            'locked_by',
            'reversed_document',
            'attachment_count',
            'items',
            'notes',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'document_number',
            'total_debit',
            'total_credit',
            'posted_at',
            'locked_at',
            'attachment_count',
            'created_at',
            'updated_at',
        ]
    
    def validate(self, data):
        """Validate document totals."""
        # Total validation will be done in model's clean() method
        return data


class DocumentAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Document Attachment."""
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True, allow_null=True)
    document_number_display = serializers.CharField(source='document.document_number', read_only=True, allow_null=True)
    
    class Meta:
        model = DocumentAttachment
        fields = [
            'id',
            'document',
            'document_number',
            'document_number_display',
            'file',
            'file_type',
            'file_type_display',
            'file_name',
            'file_size',
            'file_size_display',
            'mime_type',
            'description',
            'uploaded_by',
            'uploaded_by_username',
            'uploaded_at',
            'company',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'file_name',
            'file_size',
            'mime_type',
            'uploaded_by',
            'uploaded_at',
            'created_at',
            'updated_at',
        ]

