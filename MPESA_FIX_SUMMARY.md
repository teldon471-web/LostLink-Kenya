# M-PESA STK Push Integration - Fixes Applied

## Overview
Fixed critical issues in your M-PESA STK Push payment integration in Django. All fixes ensure proper authentication, payload validation, callback handling, and error logging.

---

## Issues Found and Fixed

### 1. **Hardcoded Values in STK Push Payload** ❌ → ✅
**File:** `users/mpesa.py`

**Problem:**
```python
"Password": MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjUxMjA2MTM1MDIy,  # ❌ Not a string!
"Timestamp": 20251206135022,  # ❌ Hardcoded value
"Amount": int(100),  # ❌ Hardcoded amount
```

**Fix Applied:**
```python
password_string = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
password = base64.b64encode(password_string.encode()).decode()  # ✅ Dynamically generated

payload = {
    "Password": password,  # ✅ Uses dynamically generated password
    "Timestamp": timestamp,  # ✅ Current timestamp
    "Amount": int(amount),  # ✅ Parameter from function
    # ... other fields
}
```

**Impact:** Password is now correctly generated for each transaction based on current timestamp.

---

### 2. **Missing Error Handling in OAuth** ❌ → ✅
**File:** `users/mpesa.py` - `get_access_token()` function

**Problem:**
```python
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(...))
    return response.json()["access_token"]  # ❌ No error handling!
```

**Fix Applied:**
```python
def get_access_token():
    """Generate access token with comprehensive error handling"""
    try:
        # ... request code ...
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()  # ✅ Raise on HTTP errors
        
        access_token = response.json().get("access_token")
        if not access_token:  # ✅ Validate response
            raise ValueError("No access_token in OAuth response")
            
        logger.info("✅ M-PESA access token generated successfully")
        return access_token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ OAuth request failed: {str(e)}")
        raise Exception(f"Failed to get access token: {str(e)}")
```

**Impact:** Failures in OAuth are now caught, logged, and reported with clear messages.

---

### 3. **Poor Callback Parsing** ❌ → ✅
**File:** `users/views.py` - `mpesa_callback()` function

**Problem:**
```python
@csrf_exempt
def mpesa_callback(request):
    try:
        data = json.loads(request.body)
        result_code = data["Body"]["stkCallback"]["ResultCode"]
        
        if result_code == 0:
            # ❌ Hardcoded index [4] for phone number - fragile!
            phone = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
            # ❌ Expects post_id as string, not parsed from account reference
            post_id = int(data["Body"]["stkCallback"]["AccountReference"])
```

**Fix Applied:**
```python
@csrf_exempt
def mpesa_callback(request):
    """Handle M-PESA STK Push callback with robust parsing"""
    try:
        data = json.loads(request.body)
        
        stk_callback = data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        
        if result_code == 0:
            # ✅ Dynamic metadata parsing
            callback_metadata = stk_callback.get("CallbackMetadata", {})
            items = callback_metadata.get("Item", [])
            
            metadata = {}
            for item in items:
                metadata[item.get("Name")] = item.get("Value")  # ✅ Name-based extraction
            
            # ✅ Extract values from named metadata
            amount = metadata.get("Amount")
            mpesa_receipt = metadata.get("MpesaReceiptNumber", "")
            phone = metadata.get("PhoneNumber")
            account_reference = metadata.get("AccountReference", "")
            
            # ✅ Parse AccountReference: "POST_<post_id>_<user_id>"
            ref_parts = account_reference.split("_")
            if len(ref_parts) >= 3 and ref_parts[0] == "POST":
                post_id = int(ref_parts[1])
                user_id = int(ref_parts[2])
```

**Impact:** Callback parsing is now robust, handles missing fields gracefully, and uses semantic names instead of array indices.

---

### 4. **Insufficient Payment Recording Logic** ❌ → ✅
**File:** `users/views.py` - Payment recording logic

**Problem:**
```python
# ❌ Tries to find user by phone number alone
profile = Profile.objects.get(phone_number=str(phone))
post = Post.objects.get(pk=post_id)

# ❌ Silent failures with pass statements
except Profile.DoesNotExist:
    pass  # No logging, no indication
except Post.DoesNotExist:
    pass
```

**Fix Applied:**
```python
# ✅ Use user_id from AccountReference
user = Profile.objects.get(user__pk=user_id).user
post = Post.objects.get(pk=post_id)

# ✅ Record payment with update_or_create
payment_access, created = PaymentAccess.objects.update_or_create(
    user=user,
    post=post,
    defaults={
        "paid": True,
        # Optional: can store transaction metadata
        # "mpesa_receipt": mpesa_receipt,
        # "transaction_date": transaction_date,
    }
)

status = "Created" if created else "Updated"
logger.info(f"✅ Payment recorded - {status} PaymentAccess for user {user_id}, post {post_id}")

# ✅ Log failures instead of silently passing
except Profile.DoesNotExist:
    logger.warning(f"⚠️ User with ID {user_id} not found")
except Post.DoesNotExist:
    logger.warning(f"⚠️ Post with ID {post_id} not found")
```

**Impact:** Payments are now reliably recorded, and failures are logged for debugging.

---

### 5. **No Logging for Debugging** ❌ → ✅
**File:** `users/mpesa.py`, `users/views.py`

**Problem:**
No logging was present, making it impossible to debug payment issues.

**Fix Applied:**
```python
import logging
logger = logging.getLogger(__name__)

# Throughout the code:
logger.info("✅ M-PESA access token generated successfully")
logger.info(f"📱 Sending STK Push for {phone_number}, amount: {amount} KES")
logger.info(f"✅ STK Push sent successfully. CheckoutRequestID: {result.get('CheckoutRequestID')}")
logger.warning(f"⚠️ STK Push returned code {response_code}")
logger.error(f"❌ STK Push request failed: {str(e)}")
logger.info(f"📨 M-PESA Callback received: {json.dumps(data, indent=2)}")
logger.info(f"✅ Payment recorded - Created PaymentAccess for user {user_id}")
```

**Impact:** All payment operations are now logged with emoji indicators for easy tracking.

---

### 6. **Weak Error Handling in pay_post View** ❌ → ✅
**File:** `users/views.py` - `pay_post()` function

**Problem:**
```python
@login_required
def pay_post(request, pk):
    post = Post.objects.get(pk=pk)  # ❌ No get_object_or_404
    amount = 100
    
    if request.method == "POST":
        phone = request.user.profile.phone_number  # ❌ No validation
        stk_push_payment(phone, amount, post.pk, request.user)  # ❌ No error handling
        return render(request, "payment/waiting.html", {"post": post})
```

**Fix Applied:**
```python
@login_required
def pay_post(request, pk):
    """Display payment form and trigger STK Push payment."""
    post = get_object_or_404(Post, pk=pk)  # ✅ Use get_object_or_404
    amount = 100
    
    if request.method == "POST":
        # ✅ Validate phone number exists
        if not request.user.profile.phone_number:
            messages.error(request, "Please add your phone number in your profile.")
            return redirect('profile')
        
        try:
            # ✅ Capture STK Push response
            phone = request.user.profile.phone_number
            response = stk_push_payment(phone, amount, post.pk, request.user)
            
            # ✅ Check response code
            response_code = response.get("ResponseCode", "1")
            if response_code == "0":
                messages.success(request, "Payment prompt sent! Check your phone.")
                return render(request, "payment/waiting.html", {"post": post})
            else:
                error_msg = response.get("ResponseDescription", "Payment request failed")
                messages.error(request, f"Payment request failed: {error_msg}")
                return render(request, "payment/pay_post.html", {"post": post})
        
        except Exception as e:
            # ✅ Catch and display errors
            logger.error(f"❌ Error during payment: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "payment/pay_post.html", {"post": post})
```

**Impact:** Users now get proper error messages if payment fails, and invalid requests are prevented.

---

## Configuration Reference

### Required Settings in `myproject/settings.py`

```python
# M-PESA OAuth Credentials (Sandbox)
MPESA_CONSUMER_KEY = "Fbo27K75S3jVWLOMbWGiaAsaZ8KKXm7wIrAIGcN9mAPo1xuw"
MPESA_CONSUMER_SECRET = "CaD07mJGrhA95WlAy2qalLw6siNljQSr50AhOCicEs6LwIMd33ygulcxe4w2IU7t"

# M-PESA Business Configuration
MPESA_SHORTCODE = "174379"
MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

# API Endpoints
MPESA_STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
MPESA_CALLBACK = "https://yourdomain.com/mpesa/callback/"  # Update for production

# Fixed pricing
MPESA_FIXED_PRICE = 100
```

**For Production:**
- Replace `MPESA_CONSUMER_KEY` and `MPESA_CONSUMER_SECRET` with live credentials
- Change `MPESA_STK_URL` to: `https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest`
- Update `MPESA_CALLBACK` to your production domain

---

## Payment Flow (Updated)

### 1. User Initiates Payment
```
User clicks "Pay Now" → POST to /post/<id>/pay/
↓
✅ Validate phone number exists
✅ Trigger STK Push (stk_push_payment)
↓
Display "Waiting for payment..." screen
```

### 2. STK Push Request
```
stk_push_payment() called
↓
✅ get_access_token() - OAuth authentication
✅ Generate timestamp
✅ Generate password: base64(SHORTCODE + PASSKEY + TIMESTAMP)
✅ Build payload with dynamic values
✅ Send POST to Safaricom STK endpoint
↓
Return response with CheckoutRequestID
```

### 3. Callback Processing
```
User completes/cancels payment on phone
↓
Safaricom sends callback to /mpesa/callback/ endpoint
↓
✅ Parse callback JSON
✅ Extract metadata (Amount, Receipt, Phone, etc.)
✅ Parse AccountReference: "POST_<post_id>_<user_id>"
✅ Record payment in PaymentAccess table
✅ Log all transaction details
↓
Return success response to Safaricom
```

---

## Testing the Integration

### 1. Test OAuth
```bash
curl -X GET "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" \
  -u "Fbo27K75S3jVWLOMbWGiaAsaZ8KKXm7wIrAIGcN9mAPo1xuw:CaD07mJGrhA95WlAy2qalLw6siNljQSr50AhOCicEs6LwIMd33ygulcxe4w2IU7t"
```

### 2. Test STK Push (Manual)
```python
from users.mpesa import stk_push_payment
from django.contrib.auth.models import User

user = User.objects.first()
response = stk_push_payment("254712345678", 100, 1, user)
print(response)
```

### 3. Monitor Logs
```bash
# Django logs payment operations
python manage.py runserver  # Watch console output

# Or in production:
tail -f logs/django.log | grep MPESA
```

---

## Common Issues & Fixes

### Issue: "Invalid password"
**Cause:** Password not properly base64 encoded
**Fix:** Ensure `base64.b64encode()` is used correctly ✅ (Already applied)

### Issue: "CallbackRequestID not found"
**Cause:** Callback endpoint not receiving requests from Safaricom
**Fix:** 
1. Ensure `MPESA_CALLBACK` URL is publicly accessible
2. For sandbox testing, use ngrok or similar tunneling tool
3. Verify URL is in settings: `MPESA_CALLBACK = "https://yourdomain.com/mpesa/callback/"`

### Issue: "Payment recorded but user can't view post"
**Cause:** `PaymentAccess.paid` not checked properly in views
**Fix:** Already implemented in `post_detail()` view ✅

### Issue: "Logs not showing"
**Cause:** Logging not configured
**Fix:** Add to settings.py:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'payment.log',
        },
    },
    'loggers': {
        'users.mpesa': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'users.views': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## Files Modified

1. ✅ `users/mpesa.py` - OAuth, STK Push, error handling
2. ✅ `users/views.py` - pay_post(), mpesa_callback(), logging
3. ✅ `users/urls.py` - Callback URL endpoint (already correct)
4. ✅ `myproject/settings.py` - M-PESA configuration (already correct)

---

## Summary of Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Password Generation** | Hardcoded invalid string | Dynamically generated from timestamp |
| **Error Handling** | None (would crash) | Comprehensive try/except with logging |
| **Callback Parsing** | Fragile array indexing | Robust dictionary-based parsing |
| **Debugging** | Silent failures | Detailed logging with emoji indicators |
| **User Feedback** | None | Messages for success/failure/errors |
| **Payment Recording** | Lookup by phone only | Lookup by user_id from AccountReference |

---

## Next Steps

1. **Test locally** with Safaricom sandbox credentials
2. **Monitor logs** during payment testing
3. **Update MPESA_CALLBACK** in settings when deploying to production
4. **Test production credentials** when ready to go live
5. **Monitor payment logs** regularly for issues

---

*Generated: December 6, 2025*
