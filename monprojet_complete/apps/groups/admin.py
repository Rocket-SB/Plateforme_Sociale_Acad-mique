from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Groupe, GroupMembership, GroupInvitation, GroupMessage


@admin.register(Groupe)
class GroupeAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'creator', 'visibility', 'member_count', 'post_count', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['admins']
    readonly_fields = ['created_at', 'member_count', 'post_count']


@admin.register(GroupMembership)
class GroupMembershipAdmin(SimpleHistoryAdmin):
    list_display = ['user', 'group', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'group__name']

@admin.register(GroupInvitation)
class GroupInvitationAdmin(SimpleHistoryAdmin):
    list_display = ('group', 'invitee', 'email', 'invited_by', 'status', 'created_at')
    list_filter = ('status', 'group')
    search_fields = ('group__name', 'invitee__username', 'email')
    autocomplete_fields = ('group', 'invitee', 'invited_by')

@admin.register(GroupMessage)
class GroupMessageAdmin(SimpleHistoryAdmin):
    list_display = ('group', 'sender', 'created_at')
    list_filter = ('group',)
    search_fields = ('group__name', 'sender__username', 'content')
    autocomplete_fields = ('group', 'sender')

