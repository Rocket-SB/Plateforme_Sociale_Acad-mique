from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    # Group Management
    path('', views.group_list, name='list'),
    path('create/', views.group_create, name='create'),
    path('<int:group_id>/', views.group_detail, name='detail'),
    path('<int:group_id>/join/', views.group_join, name='join'),
    path('<int:group_id>/leave/', views.group_leave, name='leave'),
    
    # Invitation Management (for private groups)
    path('<int:group_id>/request-invite/', views.request_group_invite, name='request_invite'),
    path('invitation/<int:invitation_id>/accept/', views.accept_invite_request, name='accept_invite'),
    path('invitation/<int:invitation_id>/decline/', views.decline_invite_request, name='decline_invite'),
    
    # Invite-only group invitations (for admins)
    path('<int:group_id>/send-invite/', views.send_group_invite, name='send_invite'),
    path('accept-invite/<str:code>/', views.accept_group_invite, name='accept_invite_link'),
    
    # Admin
    path('<int:group_id>/admin/', views.group_admin, name='admin'),
    path('<int:group_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    
    # Chat
    path('<int:group_id>/chat/', views.group_chat, name='chat'),

    path('<int:group_id>/send-invite/', views.send_group_invite, name='send_invite'),
]
