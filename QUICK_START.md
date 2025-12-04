# Quick Start Guide - LostLink-Kenya Payment Integration

## What Was Fixed

Your Django project had several critical issues preventing M-Pesa payments from working:

### ✅ Issues Resolved

1. **Circular Imports** - Fixed self-referential imports in `users/models.py`
2. **Missing URL Configuration** - Created `users/urls.py` with payment endpoints
3. **Missing Model Field** - Added `phone_number` to Profile model (required for M-Pesa)
4. **M-Pesa Settings Typo** - Fixed `MPESA_PASS_KEY` → `MPESA_PASSKEY`
5. **Hardcoded Values** - Fixed `mpesa.py` to use dynamic values and settings
6. **CSRF Issues** - Added `@csrf_exempt` to callback endpoint
7. **Database Migrations** - Generated and applied migration for phone_number field
8. **URL Routing** - Reorganized main `urls.py` to prevent conflicts

---

## Running the Project

### 1. Install Dependencies (if not already done)
```bash
pip install -r requirements.txt
```

### 2. Apply Migrations
```bash
python manage.py migrate
```

### 3. Create Admin User (if not already done)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
- **Home**: http://localhost:8000/
- **Register**: http://localhost:8000/register/
- **Blog Posts**: http://localhost:8000/blog/
- **Admin Panel**: http://localhost:8000/admin/

---

## Payment Flow - How It Works Now

1. **User Registration**
   - Register at `/register/`
   - Add phone number at `/profile/` (format: 254748542544)

2. **Create/View Post**
   - Create post at `/blog/post/new/`
   - View post at `/blog/post/<id>/`

3. **Trigger Payment**
   - Click "Pay to View" button
   - See payment form at `/post/<id>/pay/`
   - Submit form to trigger M-Pesa STK Push

4. **M-Pesa Payment**
   - User receives M-Pesa popup on phone
   - Enters PIN to complete payment
   - M-Pesa sends callback to `/mpesa/callback/`

5. **Access Content**
   - Payment recorded in `PaymentAccess` database table
   - User can now view full post content

---

## Payment URLs Available

All payment-related endpoints are now accessible:

```
GET  /post/<id>/          → View post (with payment check)
GET  /post/<id>/pay/      → Show payment form
POST /post/<id>/pay/      → Trigger M-Pesa STK Push
POST /mpesa/callback/     → Handle M-Pesa payment callback
```

---

## Database Tables

Your project now has these key tables:

- **users_profile** - User profiles with phone_number field
- **users_paymentaccess** - Payment records (user paid to view post)
- **blog_post** - Blog posts

When a user pays for a post:
- A record is created in `users_paymentaccess`
- `paid = True` is set after M-Pesa confirmation
- User can view the full post content

---

## Testing the Payment

To test the complete flow:

1. **Register User**
   ```
   Navigate to http://localhost:8000/register/
   ```

2. **Add Phone Number**
   ```
   Go to http://localhost:8000/profile/
   Add phone number: 254748542544 (or any test number)
   ```

3. **Create Test Post**
   ```
   Go to http://localhost:8000/blog/post/new/
   Create a test post
   ```

4. **Trigger Payment**
   ```
   Visit the post page
   Click "Pay to View"
   Submit payment form to test M-Pesa integration
   ```

5. **Verify in Database**
   ```bash
   python manage.py shell
   from users.models import PaymentAccess
   PaymentAccess.objects.all()  # See payment records
   ```

---

## Key Files Modified

| File | Change |
|------|--------|
| `users/models.py` | Added phone_number field, fixed imports |
| `users/views.py` | Fixed imports, secured callback |
| `users/mpesa.py` | Fixed hardcoded values, use settings |
| `users/urls.py` | **NEW** - Payment route configuration |
| `myproject/urls.py` | Reorganized, include users.urls |
| `myproject/settings.py` | Fixed MPESA_PASSKEY typo |
| `users/migrations/0003_...` | **NEW** - phone_number field migration |

---

## M-Pesa Credentials (Sandbox)

Currently configured for **Safaricom Sandbox** testing:

- Shortcode: `174379`
- Consumer Key: `Fbo27K75...` (test key)
- Consumer Secret: `CaD07mJ...` (test key)
- Passkey: `bfb279f9...` (test key)

⚠️ **For Production**: Replace credentials in `myproject/settings.py` with live M-Pesa API keys

---

## Common Issues & Fixes

### "ModuleNotFoundError: No module named 'users.urls'"
- ✅ Fixed - `users/urls.py` created and included in main urls.py

### "AttributeError: module 'users.models' cannot import name 'PaymentAccess'"
- ✅ Fixed - Removed circular imports from models.py

### "Callback not processing payments"
- ✅ Fixed - Added `@csrf_exempt` decorator to callback view

### "phone_number field not found"
- ✅ Fixed - Generated migration 0003_profile_phone_number and applied it

### Payment page not accessible at `/post/<id>/pay/`
- ✅ Fixed - Properly configured URL routing through users app

---

## Next Steps

1. ✅ All files are fixed and ready
2. ✅ Migrations are applied
3. ✅ Run the server and test the payment flow
4. ✅ For production, update M-Pesa credentials
5. ✅ For production, change MPESA_CALLBACK to your actual domain

---

## Support

If you encounter any issues:

1. Check Django logs: `python manage.py runserver`
2. Verify database: `python manage.py dbshell`
3. Run system check: `python manage.py check`
4. Check payment records: `python manage.py shell` → `from users.models import PaymentAccess; PaymentAccess.objects.all()`

For detailed documentation, see: `PAYMENT_FIX_DOCUMENTATION.md`

