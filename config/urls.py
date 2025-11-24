"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

from shared.views import custom_login, set_active_company

# Redirect admin login to custom login
def redirect_admin_login(request):
    return redirect('/login/')

urlpatterns = [
    path("admin/login/", redirect_admin_login),  # Redirect admin login to custom login
    path("admin/", admin.site.urls),
    path("login/", custom_login, name="login"),
    path("logout/", LogoutView.as_view(next_page='login'), name="logout"),
    path("i18n/setlang/", set_language, name="set_language"),
    path("shared/set-company/", set_active_company, name="set_active_company"),
]

urlpatterns += i18n_patterns(
    path("", include("ui.urls")),
    path("shared/", include("shared.urls")),
    path("inventory/", include("inventory.urls")),
    path("production/", include("production.urls")),
    path("qc/", include("qc.urls")),
    path("ticketing/", include("ticketing.urls")),
)
