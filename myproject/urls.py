"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
import os
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views

# URL Configuration
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Blog app - main content
    path('', blog_views.LandingView.as_view(), name='root-landing'),
    path('blog/', include('blog.urls')),
    path('about/', blog_views.AboutView.as_view(), name='blog-about'),
    
    # Users app - authentication and payments
    path('', include('users.urls')),
    
    # Django auth views (password reset, login)
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]

# Serve media files during development.
# Always serve media files locally (Django only does this when DEBUG=True or explicitly configured).
# For production, configure your web server (nginx/Apache) to serve /media/ from MEDIA_ROOT.
if settings.DEBUG or os.environ.get('SERVE_MEDIA') == '1':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Also serve media in development even if DEBUG is not set (useful for local testing)
    # Remove this block for production
    import sys as _sys
    if any(arg in _sys.argv for arg in ['runserver', 'test', 'shell']):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)