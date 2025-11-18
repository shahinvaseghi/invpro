"""
URL configuration for production module.
"""
from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('personnel/', views.PersonnelListView.as_view(), name='personnel'),
    path('personnel/create/', views.PersonCreateView.as_view(), name='person_create'),
    path('personnel/<int:pk>/edit/', views.PersonUpdateView.as_view(), name='person_edit'),
    path('personnel/<int:pk>/delete/', views.PersonDeleteView.as_view(), name='person_delete'),
    path('machines/', views.MachineListView.as_view(), name='machines'),
    path('machines/create/', views.MachineCreateView.as_view(), name='machine_create'),
    path('machines/<int:pk>/edit/', views.MachineUpdateView.as_view(), name='machine_edit'),
    path('machines/<int:pk>/delete/', views.MachineDeleteView.as_view(), name='machine_delete'),
]

