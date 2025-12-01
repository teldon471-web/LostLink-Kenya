import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.mail import send_mail

print("Testing Gmail SMTP Configuration...")
print(f"EMAIL_USER: {os.environ.get('EMAIL_USER')}")
print(f"EMAIL_PASS: {'SET' if os.environ.get('EMAIL_PASS') else 'NOT SET'}")

try:
    result = send_mail(
        'Test Email from Django',
        'This is a test email from your Django app to verify Gmail SMTP is working.',
        os.environ.get('EMAIL_USER'),
        [os.environ.get('EMAIL_USER')],
        fail_silently=False,
    )
    print(f'\n✅ Email sent successfully! Result: {result}')
except Exception as e:
    print(f'\n❌ Error sending email: {type(e).__name__}: {e}')
