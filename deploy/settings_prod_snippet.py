"""
Production settings snippet for `myproject/settings.py`

Drop the relevant lines into the bottom of your production settings (or import them from a dedicated
`settings_prod.py` module). Adjust paths and secret-key handling as needed.

ASSUMPTIONS
- Project deployed to: /home/ubuntu/myproject
- Domain(s): lostlinkkenya.com, www.lostlinkkenya.com
- A reverse proxy (nginx) sets X-Forwarded-Proto to "https" when terminating TLS
- Use environment variables for SECRET_KEY and other secrets

USAGE
- Set DEBUG = False
- Ensure SECRET_KEY is loaded from a secure env var
- Run `python manage.py collectstatic` into STATIC_ROOT
- Restart gunicorn and nginx after changes

"""

# SECURITY
DEBUG = False

ALLOWED_HOSTS = [
    'lostlinkkenya.com',
    'www.lostlinkkenya.com',
]

# If certbot / nginx terminate TLS, trust the proxy header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Ensure cookies are only sent over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Redirect all HTTP to HTTPS
SECURE_SSL_REDIRECT = True

# Hardenings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF trusted origins for Django >= 4.0
CSRF_TRUSTED_ORIGINS = [
    'https://lostlinkkenya.com',
    'https://www.lostlinkkenya.com',
]

# Static & media paths used on the server (ensure these match your nginx config)
STATIC_ROOT = '/home/ubuntu/myproject/staticfiles'
MEDIA_ROOT = '/home/ubuntu/myproject/media'

# Logging: simple file logger for errors (append to existing LOGGING config or merge as needed)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/ubuntu/myproject/logs/django.error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Reminder: keep SECRET_KEY out of source. Example (preferred):
# import os
# SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# Optionally: configure allowed hosts dynamically from env var
# import os
# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'lostlinkkenya.com,www.lostlinkkenya.com').split(',')
