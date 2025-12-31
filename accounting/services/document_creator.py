"""
Document creation service.
This service creates documents based on automation step definitions.
"""
from typing import Any, Dict, Optional
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from accounting.models.automation import (
    AutomationDocumentStep,
    AutomationDocumentLine,
    AutomationExecutionLog,
)
from accounting.models.documents import AccountingDocument, AccountingDocumentLine
from accounting.models.accounts import Account
from accounting.models.cost_centers import CostCenter
from accounting.utils.template_parser import TemplateParser


class DocumentCreator:
    """
    Service for creating documents from automation steps.
    
    Supports:
    - Accounting documents
    - Warehouse expense documents
    - Treasury documents
    """
    
    def __init__(self):
        self.template_parser = TemplateParser()
    
    def create_document(
        self,
        step: AutomationDocumentStep,
        variables: Dict[str, Any],
        trigger_document: Any,
        execution_log: AutomationExecutionLog
    ) -> Optional[Any]:
        """
        Create a document based on step definition.
        
        Args:
            step: The document step definition
            variables: Extracted variables
            trigger_document: The trigger document
            execution_log: The execution log
        
        Returns:
            Created document instance or None
        """
        if step.document_type == 'accounting_document':
            return self._create_accounting_document(step, variables, trigger_document, execution_log)
        elif step.document_type == 'warehouse_expense':
            return self._create_warehouse_expense_document(step, variables, trigger_document, execution_log)
        elif step.document_type in ['treasury_receive', 'treasury_pay', 'treasury_transfer']:
            return self._create_treasury_document(step, variables, trigger_document, execution_log)
        else:
            raise ValueError(f"Unsupported document type: {step.document_type}")
    
    def _create_accounting_document(
        self,
        step: AutomationDocumentStep,
        variables: Dict[str, Any],
        trigger_document: Any,
        execution_log: AutomationExecutionLog
    ) -> AccountingDocument:
        """Create an accounting document."""
        # Parse header config
        header_data = self._parse_header_config(step.header_config, variables, trigger_document)
        
        # Create document
        document = AccountingDocument.objects.create(
            company=step.company,
            document_date=header_data.get('date', timezone.now().date()),
            document_type='AUTOMATIC',
            description=header_data.get('description', ''),
            reference_number=header_data.get('reference_number', ''),
            reference_type=header_data.get('reference_type', 'AUTOMATION'),
            reference_id=trigger_document.id,
            status='DRAFT',
            created_by=getattr(trigger_document, 'created_by', None),
        )
        
        # Create lines
        lines = step.lines.filter(is_active=True).order_by('line_number')
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for line_def in lines:
            # Check line execution condition
            if line_def.execution_condition:
                # Evaluate condition (placeholder)
                # In full implementation, this would use ConditionEvaluator
                pass
            
            # Create line
            line = self._create_accounting_document_line(
                line_def,
                variables,
                document
            )
            
            if line:
                total_debit += line.debit
                total_credit += line.credit
        
        # Update document totals
        document.total_debit = total_debit
        document.total_credit = total_credit
        document.save()
        
        return document
    
    def _create_accounting_document_line(
        self,
        line_def: AutomationDocumentLine,
        variables: Dict[str, Any],
        document: AccountingDocument
    ) -> Optional[AccountingDocumentLine]:
        """Create a single accounting document line."""
        # Get debit account
        debit_account = self._get_account(
            line_def.debit_account_type,
            line_def.debit_account,
            line_def.debit_account_variable,
            variables
        )
        
        if not debit_account:
            return None
        
        # Get credit account
        credit_account = self._get_account(
            line_def.credit_account_type,
            line_def.credit_account,
            line_def.credit_account_variable,
            variables
        )
        
        if not credit_account:
            return None
        
        # Get amount
        amount = self._get_amount(
            line_def.amount_type,
            line_def.amount_value,
            line_def.amount_variable,
            line_def.amount_expression,
            variables
        )
        
        if amount is None or amount <= 0:
            return None
        
        # Determine debit/credit
        debit = Decimal('0.00')
        credit = Decimal('0.00')
        
        # For accounting documents, we need to determine which is debit and which is credit
        # This is a simplified version - actual implementation would need
        # to check account types and normal balances
        debit = amount
        credit = Decimal('0.00')
        
        # Get tafsili accounts
        debit_tafsili = self._get_tafsili(
            line_def.debit_tafsili_type,
            line_def.debit_tafsili,
            line_def.debit_tafsili_variable,
            variables
        )
        
        credit_tafsili = self._get_tafsili(
            line_def.credit_tafsili_type,
            line_def.credit_tafsili,
            line_def.credit_tafsili_variable,
            variables
        )
        
        # Get cost center
        cost_center = self._get_cost_center(
            line_def.cost_center_type,
            line_def.cost_center,
            line_def.cost_center_variable,
            variables
        )
        
        # Get description
        description = self._get_description(
            line_def.description_type,
            line_def.description_value,
            line_def.description_expression,
            variables
        )
        
        # Create line
        line = AccountingDocumentLine.objects.create(
            company=document.company,
            document=document,
            line_number=line_def.line_number,
            gl_account=debit_account if debit_account.account_level == 1 else None,
            sub_account=debit_account if debit_account.account_level == 2 else None,
            tafsili_account=debit_tafsili or (debit_account if debit_account.account_level == 3 else None),
            description=description,
            debit=debit,
            credit=credit,
            sort_order=line_def.line_number,
        )
        
        return line
    
    def _get_account(
        self,
        account_type: str,
        static_account: Optional[Account],
        account_variable: Optional[str],
        variables: Dict[str, Any]
    ) -> Optional[Account]:
        """Get account based on type."""
        if account_type == 'static':
            return static_account
        elif account_type == 'variable':
            if account_variable:
                account_value = variables.get(account_variable)
                if isinstance(account_value, Account):
                    return account_value
                elif isinstance(account_value, int):
                    return Account.objects.filter(id=account_value).first()
        return None
    
    def _get_tafsili(
        self,
        tafsili_type: str,
        static_tafsili: Optional[Account],
        tafsili_variable: Optional[str],
        variables: Dict[str, Any]
    ) -> Optional[Account]:
        """Get tafsili account based on type."""
        if tafsili_type == 'none':
            return None
        elif tafsili_type == 'static':
            return static_tafsili
        elif tafsili_type == 'variable':
            if tafsili_variable:
                tafsili_value = variables.get(tafsili_variable)
                if isinstance(tafsili_value, Account):
                    return tafsili_value
                elif isinstance(tafsili_value, int):
                    return Account.objects.filter(id=tafsili_value, account_level=3).first()
        return None
    
    def _get_cost_center(
        self,
        cost_center_type: str,
        static_cost_center: Optional[CostCenter],
        cost_center_variable: Optional[str],
        variables: Dict[str, Any]
    ) -> Optional[CostCenter]:
        """Get cost center based on type."""
        if cost_center_type == 'none':
            return None
        elif cost_center_type == 'static':
            return static_cost_center
        elif cost_center_type == 'variable':
            if cost_center_variable:
                cost_center_value = variables.get(cost_center_variable)
                if isinstance(cost_center_value, CostCenter):
                    return cost_center_value
                elif isinstance(cost_center_value, int):
                    return CostCenter.objects.filter(id=cost_center_value).first()
        return None
    
    def _get_amount(
        self,
        amount_type: str,
        static_amount: Optional[Decimal],
        amount_variable: Optional[str],
        amount_expression: Optional[str],
        variables: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Get amount based on type."""
        if amount_type == 'static':
            return static_amount
        elif amount_type == 'variable':
            if amount_variable:
                value = variables.get(amount_variable)
                if value is not None:
                    return Decimal(str(value))
        elif amount_type == 'computed':
            if amount_expression:
                # Parse and evaluate expression
                # This is a placeholder - full implementation would need expression parser
                return Decimal('0.00')
        return None
    
    def _get_description(
        self,
        description_type: str,
        static_description: Optional[str],
        description_expression: Optional[str],
        variables: Dict[str, Any]
    ) -> str:
        """Get description based on type."""
        if description_type == 'static':
            return static_description or ''
        elif description_type == 'computed':
            if description_expression:
                # Parse template and substitute variables
                return self.template_parser.parse(description_expression, variables)
        return ''
    
    def _parse_header_config(
        self,
        header_config: Dict,
        variables: Dict[str, Any],
        trigger_document: Any
    ) -> Dict[str, Any]:
        """Parse header configuration and return header data."""
        header_data = {}
        
        for field_name, field_config in header_config.items():
            field_type = field_config.get('type')
            field_value = field_config.get('value')
            
            if field_type == 'static':
                header_data[field_name] = field_value
            elif field_type == 'variable':
                if field_value:
                    header_data[field_name] = variables.get(field_value)
            elif field_type == 'computed':
                if field_value:
                    # Parse template
                    header_data[field_name] = self.template_parser.parse(field_value, variables)
        
        return header_data
    
    def _create_warehouse_expense_document(
        self,
        step: AutomationDocumentStep,
        variables: Dict[str, Any],
        trigger_document: Any,
        execution_log: AutomationExecutionLog
    ) -> Any:
        """Create a warehouse expense document."""
        # Placeholder - implement when warehouse expense model is available
        raise NotImplementedError("Warehouse expense document creation not yet implemented")
    
    def _create_treasury_document(
        self,
        step: AutomationDocumentStep,
        variables: Dict[str, Any],
        trigger_document: Any,
        execution_log: AutomationExecutionLog
    ) -> Any:
        """Create a treasury document."""
        # Placeholder - implement when treasury document models are available
        raise NotImplementedError("Treasury document creation not yet implemented")

