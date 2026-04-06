"""
ASGI config for smartStudy_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartStudy_backend.settings')
django.setup()

django_asgi_app = get_asgi_application()

async def lifespan(scope, receive, send):
    message = {"type": ""}
    try:
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                break
    except Exception as e:
        if message["type"] == "lifespan.startup":
            await send({"type": "lifespan.startup.failed", "message": str(e)})
        else:
            await send({"type": "lifespan.shutdown.failed", "message": str(e)})

from channels.routing import ProtocolTypeRouter

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "lifespan": lifespan,
})
