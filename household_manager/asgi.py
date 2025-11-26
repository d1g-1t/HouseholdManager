import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "household_manager.settings")

django_asgi_app = get_asgi_application()

from apps.expenses.routing import websocket_urlpatterns as expense_ws_patterns
from apps.notifications.routing import websocket_urlpatterns as notification_ws_patterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                expense_ws_patterns + notification_ws_patterns
            )
        )
    ),
})
