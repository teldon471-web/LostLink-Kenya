# mpesa.py
import requests
import base64
from datetime import datetime
from django.conf import settings
from requests.auth import HTTPBasicAuth
from .models import PaymentAccess

# 1️⃣ Get access token from Safaricom
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    return response.json()["access_token"]

# 2️⃣ Trigger STK Push payment
def stk_push_payment(phone, amount, post_id, user):
    """
    Trigger Mpesa STK Push payment
    
    Args:
        phone: Customer phone number (format: 254...)
        amount: Amount to charge
        post_id: ID of the post being purchased
        user: Django User object
    
    Returns:
        Response JSON from Safaricom API
    """
    access_token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Generate password using shortcode + passkey + timestamp
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": int(phone.replace("+", "")),  # Remove + if present
        "PartyB": int(settings.MPESA_SHORTCODE),
        "PhoneNumber": int(phone.replace("+", "")),  # Remove + if present
        "CallBackURL": settings.MPESA_CALLBACK,
        "AccountReference": str(post_id),
        "TransactionDesc": "Pay to view post"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(settings.MPESA_STK_URL, json=payload, headers=headers)
    return response.json()



