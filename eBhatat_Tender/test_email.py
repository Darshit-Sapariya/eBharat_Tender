import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eBhatat_Tender.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import traceback

print(f"Testing SMTP Configuration...")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

if not settings.EMAIL_HOST_USER:
    print("WARNING: EMAIL_HOST_USER is missing or empty in .env!")

try:
    print("Attempting to send an email over SMTP...")
    sent = send_mail(
        'eBharat Tender - SMTP Test', 
        'This is an automated test from the eBharat System verifying SMTP functionality is working correctly.', 
        settings.EMAIL_HOST_USER, 
        [settings.EMAIL_HOST_USER], 
        fail_silently=False
    )
    if sent:
        print('SUCCESS: Email successfully sent over SMTP!')
    else:
        print('FAILED: send_mail returned 0 (No emails sent).')
except Exception as e:
    print(f'ERROR: {type(e).__name__} - {e}')
    traceback.print_exc()
