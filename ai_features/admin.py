from django.contrib import admin
from .models import BedtimeStory, AITask

class BedtimeStoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'child', 'created_by', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'created_at']
    search_fields = ['title', 'child__name', 'story_content']
    readonly_fields = ['id', 'created_at']

class AITaskAdmin(admin.ModelAdmin):
    list_display = ['task_type', 'status', 'created_by', 'created_at', 'completed_at']
    list_filter = ['task_type', 'status', 'created_at']
    readonly_fields = ['id', 'created_at', 'completed_at']

admin.site.register(BedtimeStory, BedtimeStoryAdmin)
admin.site.register(AITask, AITaskAdmin)