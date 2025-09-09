from django.urls import path
from . import views

app_name = 'memories'

urlpatterns = [
    path('', views.MemoryListView.as_view(), name='list'),
    path('add/', views.AddMemoryView.as_view(), name='add'),
    path('<uuid:pk>/', views.MemoryDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.EditMemoryView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.DeleteMemoryView.as_view(), name='delete'),
    path('<uuid:pk>/react/', views.ReactToMemoryView.as_view(), name='react'),
    path('<uuid:pk>/comment/', views.AddCommentView.as_view(), name='comment'),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
]