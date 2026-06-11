"""WSGI config for sistema_gestao project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_gestao.settings")

application = get_wsgi_application()
