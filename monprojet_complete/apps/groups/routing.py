from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/groups/<int:group_id>/chat/', consumers.GroupChatConsumer.as_asgi()),
]
