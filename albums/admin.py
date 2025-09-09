from django.contrib import admin
from .models import Album, AlbumMemory

class AlbumMemoryInline(admin.TabularInline):
    model = AlbumMemory
    extra = 0

class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'child', 'created_by', 'memory_count', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['title', 'description', 'child__name']
    inlines = [AlbumMemoryInline]

class AlbumMemoryAdmin(admin.ModelAdmin):
    list_display = ['album', 'memory', 'order', 'added_by', 'added_at']
    list_filter = ['added_at']

admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumMemory, AlbumMemoryAdmin)