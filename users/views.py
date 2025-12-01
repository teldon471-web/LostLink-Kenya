from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


class CustomLogoutView(View):
    """Custom logout view that logs out user and redirects to login"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You can now log in.')
            return redirect('login')
        # if form is invalid, fall through and re-render template with errors
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required(login_url='login')
def profile(request):
    # Ensure user has a profile (in case of existing users without one)
    profile, created = request.user.profile if hasattr(request.user, 'profile') else None, False
    if not profile:
        from .models import Profile
        profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)
