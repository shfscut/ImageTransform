import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "markdownblog.settings")
import django

if django.VERSION >= (1, 7):
    django.setup()

from imageproxy.models import Student


Student.objects.all()