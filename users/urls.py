"""
URL configuration for the users app
Handles user registration, profile, and payment endpoints
"""
from django.urls import path
from . import views

urlpatterns = [
    # User authentication and profile
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Payment endpoints
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/pay/', views.pay_post, name='pay_post'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]
