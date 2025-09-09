from django.urls import path
from . import views

app_name = 'ai_features'

urlpatterns = [
    path('stories/', views.BedtimeStoriesView.as_view(), name='stories'),
    path('stories/create/', views.CreateBedtimeStoryView.as_view(), name='create_story'),
    path('stories/<uuid:pk>/', views.BedtimeStoryDetailView.as_view(), name='story_detail'),
    path('generate-caption/', views.GenerateCaptionView.as_view(), name='generate_caption'),
    path('transcribe-audio/', views.TranscribeAudioView.as_view(), name='transcribe_audio'),
]