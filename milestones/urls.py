from django.urls import path
from . import views

app_name = 'milestones'

urlpatterns = [
    path('', views.MilestoneListView.as_view(), name='list'),
    path('add/', views.AddMilestoneView.as_view(), name='add'),
    path('<int:pk>/edit/', views.EditMilestoneView.as_view(), name='edit'),
    path('growth/', views.GrowthChartView.as_view(), name='growth_chart'),
    path('growth/add/', views.AddGrowthRecordView.as_view(), name='add_growth'),
]