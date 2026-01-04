from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(SimpleHistoryAdmin, BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'institution', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'institution']
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = BaseUserAdmin.fieldsets[0:3] + (
        (_('Informations professionnelles'), {
            'fields': ('bio', 'profile_picture', 'institution', 'department', 'research_interests', 'website', 'orcid_id')
        }),
        (_('Réseau social'), {
            'fields': ('followers',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Informations additionnelles'), {
            'fields': ('email', 'first_name', 'last_name', 'institution')
        }),
    )

