from django.urls import path
from . import views

app_name = 'albums'

urlpatterns = [
    path('', views.AlbumListView.as_view(), name='list'),
    path('create/', views.CreateAlbumView.as_view(), name='create'),
    path('<uuid:pk>/', views.AlbumDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.EditAlbumView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.DeleteAlbumView.as_view(), name='delete'),
    path('<uuid:pk>/add-memories/', views.AddMemoriesToAlbumView.as_view(), name='add_memories'),
]