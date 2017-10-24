# custom settings for production environment
import sys

from .base import *  # NOQA

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Required when DEBUG = False
ALLOWED_HOSTS = get_setting("ALLOWED_HOSTS")  # NOQA: F405

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
