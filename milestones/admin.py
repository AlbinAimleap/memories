from django.contrib import admin
from .models import MilestoneCategory, PredefinedMilestone, ChildMilestone, GrowthRecord

class PredefinedMilestoneInline(admin.TabularInline):
    model = PredefinedMilestone
    extra = 0

class MilestoneCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'color']
    inlines = [PredefinedMilestoneInline]

class PredefinedMilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'typical_age_months_min', 'typical_age_months_max', 'is_major']
    list_filter = ['category', 'is_major']
    ordering = ['category', 'order']

class ChildMilestoneAdmin(admin.ModelAdmin):
    list_display = ['child', 'title', 'achieved_date', 'age_at_achievement', 'is_custom']
    list_filter = ['is_custom', 'achieved_date', 'predefined_milestone__category']
    search_fields = ['child__name', 'custom_title', 'predefined_milestone__title']

class GrowthRecordAdmin(admin.ModelAdmin):
    list_display = ['child', 'measurement_type', 'value', 'measurement_date', 'age_at_measurement']
    list_filter = ['measurement_type', 'measurement_date']
    search_fields = ['child__name']

admin.site.register(MilestoneCategory, MilestoneCategoryAdmin)
admin.site.register(PredefinedMilestone, PredefinedMilestoneAdmin)
admin.site.register(ChildMilestone, ChildMilestoneAdmin)
admin.site.register(GrowthRecord, GrowthRecordAdmin)