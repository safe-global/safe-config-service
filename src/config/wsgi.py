"""
WSGI config for safe_client_config_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# APM must be initialized before any Django import (required for patch() to work)
from apm import setup_tracing

setup_tracing()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
