#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.mail import send_mail
import smtplib

print("=" * 60)
print("Gmail SMTP Configuration Test")
print("=" * 60)

# Check environment variables
email_user = os.environ.get('EMAIL_USER')
email_pass = os.environ.get('EMAIL_PASS')

print(f"\n[*] EMAIL_USER: {email_user}")
print(f"[*] EMAIL_PASS: {'SET' if email_pass else 'NOT SET'}")
print(f"[*] EMAIL_PASS length: {len(email_pass) if email_pass else 0}")

# Check Django settings
from django.conf import settings
print(f"\n[*] EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"[*] EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"[*] EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"[*] EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"[*] EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"[*] EMAIL_HOST_PASSWORD: {'SET' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")

# Test connection
print("\n" + "=" * 60)
print("Testing SMTP Connection...")
print("=" * 60)

try:
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    print(f"[+] Connected to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    
    server.starttls()
    print("[+] Started TLS")
    
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print(f"[+] Logged in as {settings.EMAIL_HOST_USER}")
    
    server.quit()
    print("[+] Connection successful!")
    
except Exception as e:
    print(f"[-] Error: {type(e).__name__}: {e}")
    sys.exit(1)

# Test sending email
print("\n" + "=" * 60)
print("Testing Email Send...")
print("=" * 60)

try:
    result = send_mail(
        'Test Email from Django',
        'This is a test email to verify Gmail SMTP is working properly.\n\nIf you received this, your email configuration is correct!',
        email_user,
        [email_user],
        fail_silently=False,
    )
    print(f"[+] Email sent successfully!")
    print(f"[+] Result: {result} (1 = 1 email sent)")
except Exception as e:
    print(f"[-] Error sending email: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! Check your email inbox.")
print("=" * 60)
