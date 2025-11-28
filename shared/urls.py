"""
URL configuration for shared module.
"""
from django.urls import path
from . import views
from .views.auth import mark_notification_read, mark_notification_unread
from .views.notifications import NotificationListView

app_name = 'shared'

urlpatterns = [
    path('companies/', views.CompanyListView.as_view(), name='companies'),
    path('companies/create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),
    path('companies/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    path('units/', views.CompanyUnitListView.as_view(), name='company_units'),
    path('units/create/', views.CompanyUnitCreateView.as_view(), name='company_unit_create'),
    path('units/<int:pk>/edit/', views.CompanyUnitUpdateView.as_view(), name='company_unit_edit'),
    path('units/<int:pk>/delete/', views.CompanyUnitDeleteView.as_view(), name='company_unit_delete'),
    path('users/', views.UserListView.as_view(), name='users'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path('groups/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/edit/', views.GroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),
    path('access-levels/', views.AccessLevelListView.as_view(), name='access_levels'),
    path('access-levels/create/', views.AccessLevelCreateView.as_view(), name='access_level_create'),
    path('access-levels/<int:pk>/edit/', views.AccessLevelUpdateView.as_view(), name='access_level_edit'),
    path('access-levels/<int:pk>/delete/', views.AccessLevelDeleteView.as_view(), name='access_level_delete'),
    path('smtp-servers/', views.SMTPServerListView.as_view(), name='smtp_servers'),
    path('smtp-servers/create/', views.SMTPServerCreateView.as_view(), name='smtp_server_create'),
    path('smtp-servers/<int:pk>/edit/', views.SMTPServerUpdateView.as_view(), name='smtp_server_edit'),
    path('smtp-servers/<int:pk>/delete/', views.SMTPServerDeleteView.as_view(), name='smtp_server_delete'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('mark-notification-read/', mark_notification_read, name='mark_notification_read'),
    path('mark-notification-unread/', mark_notification_unread, name='mark_notification_unread'),
]

