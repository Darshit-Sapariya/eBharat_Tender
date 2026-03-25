import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eBhatat_Tender.settings')
django.setup()

# Now import after setup
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.test import RequestFactory

def trigger_signal():
    print("Testing Welcome Email Signal...")
    
    # Create a dummy user
    username = "testuser_google_456"
    email = "testgoogle2@example.com"
    
    # Cleanup if exists
    User.objects.filter(username=username).delete()
    
    user = User.objects.create_user(
        username=username,
        email=email,
        first_name="Test",
        last_name="Google User"
    )
    
    # Create a dummy request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Trigger the signal
    print(f"Triggering user_signed_up for {username}...")
    user_signed_up.send(sender=User, request=request, user=user)
    print("Signal triggered. Check console output above for email content.")

if __name__ == "__main__":
    trigger_signal()
