"""
WSGI config for projectread project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

deployment_env = os.environ.get("DEPLOYMENT_ENV")
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", f"projectread.settings.{deployment_env}"
)

application = get_wsgi_application()
