from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Child, Invitation

class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone', 'avatar', 'birth_date', 'is_verified')
        }),
    )

class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'birth_date', 'age_in_years', 'owner', 'created_at']
    list_filter = ['birth_date', 'created_at']
    search_fields = ['name', 'owner__username']
    filter_horizontal = ['family_members']

class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'child', 'invited_by', 'role', 'is_accepted', 'created_at']
    list_filter = ['role', 'is_accepted', 'created_at']
    search_fields = ['email', 'child__name']

admin.site.register(User, UserAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(Invitation, InvitationAdmin)