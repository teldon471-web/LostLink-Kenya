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
import logging
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import PaymentAccess, Profile
from blog.models import Post
from .mpesa import stk_push_payment

# Configure logging
logger = logging.getLogger(__name__)


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
    """
    Display post details.
    Requires payment of 100 KES to view contact/author information.
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user has already paid for this post
    payment_access = PaymentAccess.objects.filter(
        user=request.user,
        post=post,
        paid=True
    ).exists()
    
    # If user has not paid, redirect to payment page
    if not payment_access:
        return redirect("pay_post", pk=post.pk)
    
    # User has paid - show full details
    return render(request, "blog/post_detail.html", {"post": post, "paid": True})

@login_required
def pay_post(request, pk):
    """
    Display payment form and trigger STK Push payment.
    
    GET: Show payment form with post details and amount
    POST: Trigger M-PESA STK Push and show waiting screen
    """
    post = get_object_or_404(Post, pk=pk)
    amount = 100  # Fixed price for accessing post
    
    if request.method == "POST":
        # Verify user has phone number set
        if not request.user.profile.phone_number:
            messages.error(request, "Please add your phone number in your profile to proceed with payment.")
            return redirect('profile')
        
        try:
            # Trigger STK Push payment
            phone = request.user.profile.phone_number
            response = stk_push_payment(phone, amount, post.pk, request.user)
            
            # Check response from Safaricom
            response_code = response.get("ResponseCode", "1")
            if response_code == "0":
                logger.info(f"✅ STK Push sent successfully for user {request.user.id}")
                messages.success(request, "Payment prompt sent! Check your phone to complete the payment.")
                return render(request, "users/waiting.html", {"post": post, "amount": amount})
            else:
                error_msg = response.get("ResponseDescription", "Payment request failed")
                logger.warning(f"⚠️ STK Push failed: {error_msg}")
                messages.error(request, f"Payment request failed: {error_msg}")
                return render(request, "users/pay_post.html", {"post": post, "amount": amount})
                
        except Exception as e:
            logger.error(f"❌ Error during payment: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "users/pay_post.html", {"post": post, "amount": amount})
    
    # GET request - show payment form
    return render(request, "users/pay_post.html", {"post": post, "amount": amount})

@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa STK Push callback from Safaricom.
    
    Safaricom sends payment status to this endpoint asynchronously.
    Callback structure:
    {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "...",
                "CheckoutRequestID": "...",
                "ResultCode": 0,  # 0 = Success
                "ResultDesc": "The service request has been processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 100.0},
                        {"Name": "MpesaReceiptNumber", "Value": "ABC123..."},
                        {"Name": "TransactionDate", "Value": 20250206135022},
                        {"Name": "PhoneNumber", "Value": 254712345678},
                        {"Name": "AccountReference", "Value": "POST_123_45"}
                    ]
                }
            }
        }
    }
    
    Returns:
        JsonResponse: Acknowledges receipt of callback to Safaricom
    """
    try:
        # Parse incoming JSON from Safaricom
        data = json.loads(request.body)
        logger.info(f"📨 M-PESA Callback received: {json.dumps(data, indent=2)}")
        
        # Extract callback data
        stk_callback = data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        
        # Only process successful payments (ResultCode = 0)
        if result_code == 0:
            logger.info("✅ Payment successful, processing transaction...")
            
            # Extract metadata from callback response
            callback_metadata = stk_callback.get("CallbackMetadata", {})
            items = callback_metadata.get("Item", [])
            
            # Extract values from metadata items
            metadata = {}
            for item in items:
                metadata[item.get("Name")] = item.get("Value")
            
            # Extract payment details
            amount = metadata.get("Amount")
            mpesa_receipt = metadata.get("MpesaReceiptNumber", "")
            transaction_date = metadata.get("TransactionDate")
            phone = metadata.get("PhoneNumber")
            account_reference = metadata.get("AccountReference", "")
            
            logger.info(f"💰 Payment Details - Amount: {amount}, Phone: {phone}, Receipt: {mpesa_receipt}")
            
            # Parse AccountReference to get post_id and user_id
            # Format: POST_<post_id>_<user_id>
            try:
                ref_parts = account_reference.split("_")
                if len(ref_parts) >= 3 and ref_parts[0] == "POST":
                    post_id = int(ref_parts[1])
                    user_id = int(ref_parts[2])
                    
                    # Retrieve post and user
                    try:
                        post = Post.objects.get(pk=post_id)
                        user = Profile.objects.get(user__pk=user_id).user
                        
                        # Record successful payment
                        payment_access, created = PaymentAccess.objects.update_or_create(
                            user=user,
                            post=post,
                            defaults={
                                "paid": True,
                                # Optional: Add fields to store transaction info
                                # "mpesa_receipt": mpesa_receipt,
                                # "transaction_date": transaction_date,
                                # "amount": amount
                            }
                        )
                        
                        status = "Created" if created else "Updated"
                        logger.info(f"✅ Payment recorded - {status} PaymentAccess for user {user_id}, post {post_id}")
                        
                    except Post.DoesNotExist:
                        logger.warning(f"⚠️ Post with ID {post_id} not found")
                    except Profile.DoesNotExist:
                        logger.warning(f"⚠️ User with ID {user_id} not found")
                        
            except (ValueError, IndexError) as e:
                logger.error(f"❌ Could not parse AccountReference '{account_reference}': {str(e)}")
        
        else:
            # Payment failed
            result_desc = stk_callback.get("ResultDesc", "Unknown error")
            logger.warning(f"⚠️ Payment failed - ResultCode: {result_code}, Description: {result_desc}")
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in callback: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in callback handler: {str(e)}", exc_info=True)
    
    # Always return success to Safaricom to acknowledge receipt
    # Returning error could cause Safaricom to retry the callback multiple times
    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Callback received and processed"
    })

