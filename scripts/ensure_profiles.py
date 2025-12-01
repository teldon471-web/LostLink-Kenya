import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','myproject.settings')
import django
django.setup()
from django.contrib.auth.models import User
from users.models import Profile
created=0
for u in User.objects.all():
    p, c = Profile.objects.get_or_create(user=u)
    if c:
        created+=1
print('Profiles ensured for', User.objects.count(), 'users; created', created)
