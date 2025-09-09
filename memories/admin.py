from django.contrib import admin
from .models import Memory, MemoryReaction, MemoryComment

class MemoryReactionInline(admin.TabularInline):
    model = MemoryReaction
    extra = 0

class MemoryCommentInline(admin.TabularInline):
    model = MemoryComment
    extra = 0

class MemoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'child', 'memory_type', 'created_by', 'memory_date', 'is_milestone']
    list_filter = ['memory_type', 'is_milestone', 'is_private', 'created_at']
    search_fields = ['title', 'content', 'child__name', 'created_by__username']
    inlines = [MemoryReactionInline, MemoryCommentInline]
    readonly_fields = ['id', 'created_at', 'updated_at']

class MemoryReactionAdmin(admin.ModelAdmin):
    list_display = ['memory', 'user', 'reaction', 'created_at']
    list_filter = ['reaction', 'created_at']

class MemoryCommentAdmin(admin.ModelAdmin):
    list_display = ['memory', 'user', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'memory__title']

admin.site.register(Memory, MemoryAdmin)
admin.site.register(MemoryReaction, MemoryReactionAdmin)
admin.site.register(MemoryComment, MemoryCommentAdmin)