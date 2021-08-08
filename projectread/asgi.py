"""
ASGI config for projectread project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

deployment_env = os.environ.get("DEPLOYMENT_ENV")
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", f"projectread.settings.{deployment_env}"
)

application = get_asgi_application()
