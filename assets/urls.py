"""
URL Configuration for Assets App
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # Dashboard (default page)
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Assets CRUD
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('assets/<int:pk>/edit/', views.AssetUpdateView.as_view(), name='asset_update'),
    path('assets/<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),
    
    # Documents
    path('documents/<int:pk>/download/', views.download_document, name='document_download'),
    path('documents/<int:pk>/delete/', views.delete_document, name='document_delete'),
    
    # Activity Log
    path('activity/', views.ActivityLogView.as_view(), name='activity_log'),
    
    # API
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
]
