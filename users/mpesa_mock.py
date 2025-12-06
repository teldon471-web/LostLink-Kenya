# mpesa_mock.py
"""
Mock M-PESA module for local testing without internet connection.
Use this for development/testing. Switch to real mpesa.py for production.
"""

import logging
import json
from datetime import datetime
from django.conf import settings
from .models import PaymentAccess
from blog.models import Post
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def get_access_token():
    """
    Mock access token generator.
    Returns a fake token for testing.
    """
    logger.info("✅ [MOCK] Access token generated (mock - no internet needed)")
    return "mock_access_token_fake_xyz_123"


def stk_push_payment(phone, amount, post_id, user):
    """
    Mock STK Push payment handler.
    Simulates Safaricom response without making real API call.
    
    Args:
        phone: Customer phone number
        amount: Amount to charge
        post_id: ID of the post being purchased
        user: Django User object
    
    Returns:
        dict: Mock response from Safaricom
    """
    try:
        logger.info(f"📱 [MOCK] Sending STK Push for {phone}, amount: {amount} KES")
        
        # Simulate successful response
        response = {
            "MerchantRequestID": "mock_request_12345",
            "CheckoutRequestID": "ws_CO_MOCK_xyz_123456",
            "ResponseCode": "0",
            "ResponseDescription": "Success. Request accepted for processing (MOCK)",
            "CustomerMessage": "Success. Request accepted for processing (MOCK)"
        }
        
        logger.info(f"✅ [MOCK] STK Push response: {response}")
        
        # Auto-approve payment for testing (comment out for manual testing)
        # This allows you to test the payment flow without actually paying
        logger.info(f"✅ [MOCK] Auto-approving payment for testing purposes")
        try:
            post = Post.objects.get(pk=post_id)
            PaymentAccess.objects.update_or_create(
                user=user,
                post=post,
                defaults={"paid": True}
            )
            logger.info(f"✅ [MOCK] Payment recorded for user {user.id}, post {post_id}")
        except Post.DoesNotExist:
            logger.warning(f"⚠️ [MOCK] Post with ID {post_id} not found")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ [MOCK] Error in mock STK Push: {str(e)}")
        raise


def mock_callback_test(post_id, user_id):
    """
    Test function to simulate a Safaricom callback without internet.
    Useful for testing the callback handler.
    
    Usage:
        from users.mpesa_mock import mock_callback_test
        mock_callback_test(post_id=1, user_id=1)
    """
    try:
        post = Post.objects.get(pk=post_id)
        user = User.objects.get(pk=user_id)
        
        PaymentAccess.objects.update_or_create(
            user=user,
            post=post,
            defaults={"paid": True}
        )
        logger.info(f"✅ [MOCK] Test callback processed: user {user_id}, post {post_id}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"❌ [MOCK] Error in test callback: {str(e)}")
        raise


print("""
╔════════════════════════════════════════════════════════════════╗
║                   M-PESA MOCK MODULE LOADED                    ║
║                                                                 ║
║  This is a mock/test version of M-PESA integration.            ║
║  Use this for LOCAL DEVELOPMENT when you don't have internet.  ║
║                                                                 ║
║  For PRODUCTION, switch back to the real mpesa.py module.      ║
║                                                                 ║
║  To use this mock version:                                     ║
║  1. In users/views.py, change:                                 ║
║     from .mpesa import stk_push_payment                         ║
║  To:                                                            ║
║     from .mpesa_mock import stk_push_payment                    ║
║  2. Users can now test the payment flow locally                ║
║  3. Payments are auto-approved for testing                     ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
""")
