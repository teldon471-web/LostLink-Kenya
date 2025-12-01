import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Post

# Get or create admin user
admin_user = User.objects.get(username='admin')

# Create some test posts
Post.objects.all().delete()
Post.objects.create(
    title='Welcome to My Blog',
    content='This is the first post on my new Django blog.',
    author=admin_user
)
Post.objects.create(
    title='Django Models',
    content='Learn how to create and manage models in Django.',
    author=admin_user
)

print(f'Created {Post.objects.count()} posts')
print('Posts:')
for post in Post.objects.all():
    print(f'  - {post.title} by {post.author.username}')
