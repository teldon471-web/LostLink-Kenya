from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import json
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import PaymentAccess, Profile
from blog.models import Post
from .mpesa import stk_push_payment


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

class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Your account has been created! You can now log in.')
        return response

class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        # Ensure profile exists
        if not hasattr(request.user, 'profile'):
            Profile.objects.get_or_create(user=request.user)
            
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Ensure profile exists
        if not hasattr(request.user, 'profile'):
            Profile.objects.get_or_create(user=request.user)

        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
            
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
        return render(request, self.template_name, context)
@login_required
def post_detail(request, pk):
    post = Post.objects.get(pk=pk)
    paid = PaymentAccess.objects.filter(user=request.user, post=post, paid=True).exists()

    if request.GET.get("view") == "1" and not paid:
        return redirect("pay_post", pk=post.pk)

    return render(request, "post_detail.html", {"post": post, "paid": paid})

@login_required
def pay_post(request, pk):
    post = Post.objects.get(pk=pk)
    amount = 100  # fixed price

    if request.method == "POST":
        phone = request.user.profile.phone_number
        stk_push_payment(phone, amount, post.pk, request.user)
        return render(request, "payment/waiting.html", {"post": post})

    return render(request, "payment/pay_post.html", {"post": post, "amount": amount})

@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa callback for STK Push payments
    Safaricom sends payment status to this endpoint
    """
    try:
        data = json.loads(request.body)
        result_code = data["Body"]["stkCallback"]["ResultCode"]
        
        # Only process successful payments (result code 0)
        if result_code == 0:
            phone = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
            post_id = int(data["Body"]["stkCallback"]["AccountReference"])
            
            # Update payment status in database
            try:
                profile = Profile.objects.get(phone_number=str(phone))
                post = Post.objects.get(pk=post_id)
                PaymentAccess.objects.update_or_create(
                    user=profile.user, 
                    post=post, 
                    defaults={"paid": True}
                )
            except Profile.DoesNotExist:
                pass  # Phone number not found, payment not recorded
            except Post.DoesNotExist:
                pass  # Post not found, payment not recorded
    
    except (json.JSONDecodeError, KeyError) as e:
        pass  # Invalid callback format, ignore
    
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

