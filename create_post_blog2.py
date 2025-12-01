import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from blog.models import Post

User = get_user_model()

username = 'admin'
email = 'admin@example.com'
password = 'admin123'

# Ensure admin user exists
user, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"Created user '{username}' with password '{password}'")
else:
    print(f"Found existing user '{username}'")

# Create or get post
title = 'Blog 2'
content = 'Second Post Content!'
post, created = Post.objects.get_or_create(title=title, defaults={'content': content, 'author': user})
if created:
    print(f"Created post: {post.title} (id={post.id})")
else:
    print(f"Post already exists: {post.title} (id={post.id})")

# List current posts
print('\nAll posts:')
for p in Post.objects.all():
    print(f"- {p.title} by {p.author.username} (id={p.id})")
