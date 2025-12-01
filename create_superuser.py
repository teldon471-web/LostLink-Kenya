import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
# Delete existing admin user if present
User.objects.filter(username='admin').delete()
# Create new superuser
user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print(f'Superuser created: username={user.username}, email={user.email}')
print('Password: admin123')
