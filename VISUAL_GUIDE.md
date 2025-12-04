# 🎯 VISUAL GUIDE - Payment Flow & Architecture

## Payment Processing Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REGISTRATION                         │
│  http://localhost:8000/register/                            │
│                                                              │
│  ✓ Create Django User account                              │
│  ✓ Set username, email, password                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   ADD PHONE NUMBER                           │
│  http://localhost:8000/profile/                            │
│                                                              │
│  ✓ Edit Profile                                            │
│  ✓ Add phone_number: 254748542544                          │
│  ✓ Save Profile                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  CREATE BLOG POST                            │
│  http://localhost:8000/blog/post/new/                      │
│                                                              │
│  ✓ Create Post about Lost/Found item                      │
│  ✓ Add title, content, image                              │
│  ✓ Save Post                                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  VIEW POST DETAILS                           │
│  http://localhost:8000/blog/post/<id>/                     │
│                                                              │
│  ✓ View post content                                       │
│  ✓ See "Pay to View Full Details" button                  │
│  ✓ Click button to proceed to payment                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                 PAYMENT INITIATION                           │
│  http://localhost:8000/post/<id>/pay/   [GET]             │
│                                                              │
│  ✓ views.pay_post() called                                │
│  ✓ Render payment_form.html template                      │
│  ✓ Show amount: KES 100                                   │
│  ✓ User submits payment form                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              TRIGGER M-PESA STK PUSH                        │
│  http://localhost:8000/post/<id>/pay/   [POST]            │
│                                                              │
│  ✓ views.pay_post() called                                │
│  ✓ Calls mpesa.stk_push_payment()                         │
│  ✓ Generates M-Pesa password (dynamic)                    │
│  ✓ Sends request to Safaricom API                        │
│  ✓ Returns checkoutRequestID                             │
│  ✓ User sees payment waiting page                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│            USER'S PHONE - MPESA POPUP                        │
│                                                              │
│  ┌──────────────────────────────┐                         │
│  │  STK PUSH NOTIFICATION        │                         │
│  ├──────────────────────────────┤                         │
│  │ Amount: KES 100               │                         │
│  │ Account: LostLink-Kenya       │                         │
│  │ Reference: post_id            │                         │
│  │                              │                         │
│  │  [Enter PIN]  [Cancel]       │                         │
│  └──────────────────────────────┘                         │
│                                                              │
│  ✓ User enters M-Pesa PIN                                 │
│  ✓ M-Pesa processes payment                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│         SAFARICOM SENDS CALLBACK                             │
│  POST http://localhost:8000/mpesa/callback/               │
│  (CSRF Exempt ✓)                                           │
│                                                              │
│  Headers:                                                   │
│  {                                                          │
│    "Body": {                                               │
│      "stkCallback": {                                      │
│        "MerchantRequestID": "xxx",                         │
│        "CheckoutRequestID": "yyy",                         │
│        "ResultCode": 0,         ← 0 = Success              │
│        "ResultDesc": "Success",                            │
│        "CallbackMetadata": {                               │
│          "Item": [                                         │
│            {...},                                          │
│            {...},                                          │
│            {...},                                          │
│            {...},                                          │
│            {"Value": "254748542544"}  ← Phone Number       │
│          ]                                                  │
│        },                                                   │
│        "AccountReference": "post_id"                       │
│      }                                                      │
│    }                                                        │
│  }                                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│            PROCESS CALLBACK - UPDATE DATABASE                │
│  views.mpesa_callback()                                     │
│                                                              │
│  ✓ Parse JSON payload                                      │
│  ✓ Check result_code == 0                                 │
│  ✓ Extract phone_number from Item[4]                      │
│  ✓ Extract post_id from AccountReference                 │
│  ✓ Find User profile by phone_number                      │
│  ✓ Find Post by post_id                                   │
│  ✓ Create/Update PaymentAccess record:                    │
│    {                                                        │
│      user_id: <user>,                                      │
│      post_id: <post>,                                      │
│      paid: True,        ← Payment confirmed!               │
│      created: <timestamp>                                   │
│    }                                                        │
│  ✓ Return JSON: {"ResultCode": 0, "ResultDesc": "Accepted"}│
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│             PAYMENT CONFIRMED - VIEW POST                    │
│  http://localhost:8000/post/<id>/  OR                       │
│  http://localhost:8000/blog/post/<id>/                     │
│                                                              │
│  ✓ views.post_detail() checks PaymentAccess:              │
│    paid = PaymentAccess.objects.filter(                    │
│      user=request.user,                                    │
│      post=post,                                            │
│      paid=True                                             │
│    ).exists()                                              │
│                                                              │
│  ✓ If paid=True:                                           │
│    - Show full post content                               │
│    - Pass paid=True to template                           │
│                                                              │
│  ✓ Template renders full post with all details           │
│  ✓ User can now access complete post information          │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema Diagram

```
┌──────────────────────────────────────────┐
│          Django User (Built-in)          │
├──────────────────────────────────────────┤
│ id (PK)                                  │
│ username                                 │
│ email                                    │
│ password                                 │
│ first_name                               │
│ last_name                                │
│ is_active                                │
│ is_staff                                 │
│ created_at                               │
└──────────────┬───────────────────────────┘
               │ One-to-One
               │ (user_id FK)
               │
               ▼
┌──────────────────────────────────────────┐
│         users_profile                    │
├──────────────────────────────────────────┤
│ id (PK)                                  │
│ user_id (FK) ──────► User.id            │
│ bio                                      │
│ location                                 │
│ phone_number (NEW!) ◀──────────────────┐ │
│ image                                    │
└──────────────┬───────────────────────────┘
               │
               │ One-to-Many
               │
               ▼
┌──────────────────────────────────────────┐
│      users_paymentaccess                 │
├──────────────────────────────────────────┤
│ id (PK)                                  │
│ user_id (FK) ──────► User.id            │
│ post_id (FK) ──────► blog_post.id       │
│ paid (Boolean)                           │
│ created (DateTime)                       │
│ Constraint: unique(user_id, post_id)    │
└──────────────────────────────────────────┘
               │
               │ Many-to-One
               │
               ▼
┌──────────────────────────────────────────┐
│         blog_post                        │
├──────────────────────────────────────────┤
│ id (PK)                                  │
│ title                                    │
│ content                                  │
│ item_type                                │
│ category                                 │
│ location                                 │
│ status                                   │
│ image                                    │
│ date_posted                              │
│ author_id (FK) ────► User.id            │
└──────────────────────────────────────────┘
```

**Key Relationship:**
- User → Profile (1:1)
- User → PaymentAccess (1:Many)
- Post → PaymentAccess (1:Many)
- Unique constraint: (user, post) prevents duplicate payments

---

## URL Routing Architecture

```
MAIN APPLICATION (http://localhost:8000)
│
├── /admin/
│   └── Django Admin Interface
│
├── /
│   └── blog_views.LandingView (Landing Page)
│
├── /blog/
│   ├── (via include('blog.urls'))
│   ├── POST List
│   ├── /post/new/
│   ├── /post/<id>/
│   ├── /post/<id>/update/
│   ├── /post/<id>/delete/
│   └── /user/<username>/
│
├── /about/
│   └── blog_views.AboutView (About Page)
│
├── / (users.urls included here)
│   ├── (via include('users.urls'))
│   ├── /register/
│   │   └── views.RegisterView
│   │       ↓ Registration page
│   │       POST → Create User & Profile
│   │
│   ├── /profile/
│   │   └── views.ProfileView (LoginRequired)
│   │       ↓ View/Edit User Profile
│   │       GET → Show form (add phone_number here!)
│   │       POST → Update Profile
│   │
│   ├── /logout/
│   │   └── views.CustomLogoutView
│   │       ↓ Logout current user
│   │
│   ├── /post/<int:pk>/
│   │   └── views.post_detail (LoginRequired)
│   │       ↓ View post details
│   │       GET → Check PaymentAccess
│   │       └─ If paid=True: Show full content
│   │       └─ If paid=False: Show locked content + pay button
│   │
│   ├── /post/<int:pk>/pay/
│   │   └── views.pay_post (LoginRequired)
│   │       ├─ GET → Show payment form
│   │       │        POST → Trigger M-Pesa STK
│   │       │        └─ stk_push_payment() called
│   │       │        └─ User enters PIN on phone
│   │       │        └─ Safaricom sends callback
│   │       │
│   │       └─ POST → Create PaymentAccess (paid=False)
│   │                 Trigger mpesa.stk_push_payment()
│   │                 Return to waiting.html
│   │
│   └── /mpesa/callback/
│       └── views.mpesa_callback (CSRF Exempt!)
│           ↓ Receive POST from Safaricom
│           ├─ Parse JSON payload
│           ├─ Verify result_code == 0
│           ├─ Extract phone & post_id
│           ├─ Update PaymentAccess (paid=True)
│           └─ Return JSON to Safaricom
│
├── /login/
│   └── auth_views.LoginView
│
├── /password-reset/
│   └── Password reset flow
│
└── /media/<path>/
    └── User uploads (profile pics, post images)
```

---

## M-Pesa Integration Flow

```
┌─────────────────────┐
│ LOCAL APPLICATION   │
└──────────┬──────────┘
           │
           │ 1. User submits payment form
           │
           ▼
┌─────────────────────┐
│ stk_push_payment()  │
│ users/mpesa.py      │
└──────────┬──────────┘
           │
           │ 2. Get access token
           │
           ▼
┌─────────────────────────────────────┐
│ Safaricom OAuth API (Sandbox)       │
│ /oauth/v1/generate                  │
│ (Authenticate with credentials)     │
└──────────┬──────────────────────────┘
           │
           │ Returns: access_token
           │
           ▼
┌─────────────────────────────────────┐
│ Generate Dynamic Password           │
│ base64(SHORTCODE+PASSKEY+TIMESTAMP) │
└──────────┬──────────────────────────┘
           │
           │ 3. Send STK Push request
           │ with dynamic values:
           │ - Password (generated)
           │ - Timestamp (now)
           │ - Amount (from param)
           │ - Phone (from param)
           │ - CallbackURL
           │
           ▼
┌─────────────────────────────────────┐
│ Safaricom STK Push API (Sandbox)   │
│ /mpesa/stkpush/v1/processrequest   │
└──────────┬──────────────────────────┘
           │
           │ Returns: CheckoutRequestID
           │ (Customer gets STK popup)
           │
           ▼
┌─────────────────────┐
│ USER'S PHONE        │
│ ┌───────────────┐  │
│ │  STK POPUP    │  │
│ │ Amount: 100   │  │
│ │ [PIN]         │  │
│ └───────────────┘  │
└─────────┬──────────┘
          │
          │ User enters PIN
          │ M-Pesa processes
          │ Payment successful
          │
          ▼
┌──────────────────────────────────────┐
│ Safaricom Callback Server            │
│ Prepares callback JSON               │
│ (result code 0 = success)            │
└──────────────┬───────────────────────┘
               │
               │ 4. POST Callback
               │
               ▼
┌──────────────────────────────────────┐
│ /mpesa/callback/                     │
│ views.mpesa_callback()               │
│ (CSRF Exempt)                        │
└──────────────┬───────────────────────┘
               │
               │ 5. Process callback
               │ - Parse JSON
               │ - Verify result_code
               │ - Get phone & post_id
               │
               ▼
┌──────────────────────────────────────┐
│ DATABASE                             │
│ users_paymentaccess                  │
│                                      │
│ UPDATE:                              │
│ SET paid=True                        │
│ WHERE user_id=X AND post_id=Y       │
└──────────────┬───────────────────────┘
               │
               │ 6. Return success
               │ {"ResultCode": 0}
               │
               ▼
┌──────────────────────────────────────┐
│ User can now view full post content  │
│ /post/<id>/ shows unlocked content   │
└──────────────────────────────────────┘
```

---

## Configuration Checklist

### ✅ Settings.py Configuration

```python
# M-Pesa Credentials (Update for production)
MPESA_CONSUMER_KEY = "..."
MPESA_CONSUMER_SECRET = "..."
MPESA_SHORTCODE = "174379"
MPESA_PASSKEY = "..."  # ✅ CORRECTED (was MPESA_PASS_KEY)
MPESA_STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
MPESA_CALLBACK = "https://yourdomain.com/mpesa/callback/"  # Update domain
```

### ✅ Database Setup

```bash
# Run migrations
python manage.py migrate

# Check PaymentAccess table
python manage.py dbshell
> .schema users_paymentaccess
> SELECT * FROM users_paymentaccess;
```

### ✅ URL Configuration

```python
# Main urls.py includes users.urls
urlpatterns = [
    ...
    path('', include('users.urls')),  # ✅ REQUIRED
    ...
]

# users.urls defines payment endpoints
# /post/<id>/
# /post/<id>/pay/
# /mpesa/callback/
```

### ✅ Views Configuration

```python
# views.pay_post()
# ✓ GET renders payment form
# ✓ POST triggers stk_push_payment()

# views.mpesa_callback()
# ✓ CSRF exempt (required!)
# ✓ Processes M-Pesa payload
# ✓ Updates PaymentAccess to paid=True

# views.post_detail()
# ✓ Checks PaymentAccess.paid
# ✓ Shows/hides content accordingly
```

---

## Testing Checklist

```
□ User registration works (/register/)
□ User profile editable (/profile/)
□ Phone number field exists and saves
□ Blog posts can be created (/blog/post/new/)
□ Payment form accessible (/post/<id>/pay/)
□ M-Pesa STK triggers on form submit
□ User receives STK popup on phone
□ User can complete payment with PIN
□ Callback endpoint receives data
□ PaymentAccess record created with paid=True
□ User can now view full post content
□ Payment history visible in admin
```

---

## Production Deployment Notes

```
1. Update MPESA_* settings with live credentials
2. Change MPESA_CALLBACK to production domain
3. Set DEBUG=False in settings
4. Use environment variables for secrets
5. Configure ALLOWED_HOSTS
6. Set up HTTPS/SSL
7. Test complete payment flow before launch
8. Monitor payment callback logs
9. Set up database backups
10. Configure web server to serve media files
```

