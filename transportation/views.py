"""
Views for transportation module.
"""
from django.views.generic import TemplateView
from shared.mixins import FeaturePermissionRequiredMixin


class TransportationDashboardView(FeaturePermissionRequiredMixin, TemplateView):
    """Dashboard view for transportation module."""
    template_name = 'transportation/dashboard.html'
    feature_code = 'transportation.dashboard'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'transportation'
        context['page_title'] = 'حمل و نقل'
        return context

