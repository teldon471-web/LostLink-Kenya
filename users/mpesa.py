# mpesa.py
"""
M-PESA STK Push Payment Integration Module

This module handles:
- OAuth authentication with Safaricom API
- STK Push payment requests
- Callback response processing
- Transaction logging and validation
"""

import requests
import base64
import logging
from datetime import datetime
from django.conf import settings
from requests.auth import HTTPBasicAuth
from .models import PaymentAccess

# Configure logging for payment debugging
logger = logging.getLogger(__name__)


def get_access_token():
    """
    Generate access token from Safaricom OAuth endpoint.
    
    This token is required for all subsequent M-PESA API calls.
    Uses HTTP Basic Authentication with consumer credentials.
    
    Returns:
        str: Access token for API authorization
        
    Raises:
        Exception: If OAuth request fails or returns invalid response
    """
    try:
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        # Authenticate using credentials from Django settings
        auth = HTTPBasicAuth(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET
        )
        
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        access_token = response.json().get("access_token")
        if not access_token:
            raise ValueError("No access_token in OAuth response")
            
        logger.info("✅ M-PESA access token generated successfully")
        return access_token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ OAuth request failed: {str(e)}")
        raise Exception(f"Failed to get access token: {str(e)}")
    except (KeyError, ValueError) as e:
        logger.error(f"❌ Invalid OAuth response: {str(e)}")
        raise Exception(f"Invalid OAuth response: {str(e)}")


def stk_push_payment(phone, amount, post_id, user):
    """
    Trigger M-PESA STK Push payment prompt.
    
    Sends a payment request to Safaricom which displays a prompt on the
    customer's phone to enter their M-PESA PIN. Payment is processed
    asynchronously via callback URL.
    
    Args:
        phone (str): Customer phone number in format 254XXXXXXXXX or +254XXXXXXXXX
        amount (int): Amount to charge in KES
        post_id (int): ID of the post being purchased (for reference)
        user (User): Django User object making the payment
    
    Returns:
        dict: Response from Safaricom containing:
            - ResponseCode: "0" for success, other codes for errors
            - ResponseDescription: Human-readable message
            - CheckoutRequestID: Transaction reference ID
            
    Raises:
        Exception: If access token generation fails or STK request fails
    """
    try:
        # Step 1: Get access token
        access_token = get_access_token()
        
        # Step 2: Generate timestamp for password encoding
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Step 3: Generate password by encoding: SHORTCODE + PASSKEY + TIMESTAMP
        # This password is required by Safaricom for STK Push requests
        password_string = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
        password = base64.b64encode(password_string.encode()).decode()
        
        # Step 4: Normalize phone number (remove + if present)
        phone_number = phone.replace("+", "").strip()
        
        # Validate phone number format
        if len(phone_number) < 12:
            raise ValueError(f"Invalid phone number format: {phone}")
        
        # Step 5: Build STK Push payload with all required fields
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,  # Base64 encoded password
            "Timestamp": timestamp,  # YYYYMMDDHHMMSS format
            "TransactionType": "CustomerPayBillOnline",  # Payment type
            "Amount": int(amount),  # Must be integer
            "PartyA": int(phone_number),  # Customer's phone number
            "PartyB": int(settings.MPESA_SHORTCODE),  # Business short code
            "PhoneNumber": int(phone_number),  # Phone number for STK display
            "CallBackURL": settings.MPESA_CALLBACK,  # Webhook for transaction result
            "AccountReference": f"POST_{post_id}_{user.id}",  # Reference info
            "TransactionDesc": f"Payment for post access"  # Transaction description
        }
        
        # Step 6: Set authorization headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Step 7: Send STK Push request to Safaricom
        logger.info(f"📱 Sending STK Push for {phone_number}, amount: {amount} KES")
        response = requests.post(
            settings.MPESA_STK_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Step 8: Validate response from Safaricom
        response_code = result.get("ResponseCode")
        if response_code == "0":
            logger.info(f"✅ STK Push sent successfully. CheckoutRequestID: {result.get('CheckoutRequestID')}")
        else:
            logger.warning(f"⚠️ STK Push returned code {response_code}: {result.get('ResponseDescription')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ STK Push request failed: {str(e)}")
        raise Exception(f"STK Push request failed: {str(e)}")
    except (ValueError, KeyError) as e:
        logger.error(f"❌ Invalid payload or settings: {str(e)}")
        raise Exception(f"Invalid payload: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in STK Push: {str(e)}")
        raise



