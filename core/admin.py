from django.contrib import admin
from .models import AppSettings, ExportJob

class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']

class ExportJobAdmin(admin.ModelAdmin):
    list_display = ['child', 'requested_by', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']

admin.site.register(AppSettings, AppSettingsAdmin)
admin.site.register(ExportJob, ExportJobAdmin)