"""
Base view classes for QC module.
"""
from typing import Dict, Any, Optional
from django.contrib.auth.mixins import LoginRequiredMixin


class QCBaseView(LoginRequiredMixin):
    """Base view with common context for QC module."""
    login_url = '/admin/login/'
    
    def get_queryset(self):
        """Filter queryset by active company."""
        queryset = super().get_queryset()
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if company_id and hasattr(queryset.model, 'company'):
            queryset = queryset.filter(company_id=company_id)
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'qc'
        return context

