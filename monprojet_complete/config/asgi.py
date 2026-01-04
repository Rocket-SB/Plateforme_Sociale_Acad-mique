"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.asgi import get_asgi_application
import apps.messaging.routing
import apps.notifications.routing
import apps.groups.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.messaging.routing.websocket_urlpatterns +
            apps.notifications.routing.websocket_urlpatterns +
            apps.groups.routing.websocket_urlpatterns
        )
    ),
})
