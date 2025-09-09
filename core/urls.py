from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('features/', views.FeaturesView.as_view(), name='features'),
    path('export/', views.ExportDataView.as_view(), name='export'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]