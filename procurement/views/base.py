"""
Base views and mixins for procurement module.
"""
from typing import Optional, Dict, Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _


class ProcurementBaseView(LoginRequiredMixin):
    """Base view with common context for procurement module."""
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        """Add common context variables."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'procurement'
        return context

