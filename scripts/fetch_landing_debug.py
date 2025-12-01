import os, sys
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','myproject.settings')
import django
django.setup()
from django.conf import settings
settings.DEBUG = True
from django.test import Client
c = Client()
resp = c.get('/blog/landing/')
print('STATUS', resp.status_code)
print('\n---- RESPONSE (truncated 4000 chars) ----\n')
print(resp.content.decode('utf-8','replace')[:4000])
