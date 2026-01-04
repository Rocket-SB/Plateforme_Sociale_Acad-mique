from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.chat_interface, name='chat'),
    path('<int:conversation_id>/', views.chat_interface, name='chat_detail'),
    path('users/', views.user_list, name='user_list'),
    path('new/<int:user_id>/', views.new_conversation, name='new'),
    # path('inbox/', views.inbox, name='inbox'),
    # path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation'),
]
