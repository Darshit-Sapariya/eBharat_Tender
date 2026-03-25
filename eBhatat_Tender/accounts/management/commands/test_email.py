from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.test import RequestFactory

class Command(BaseCommand):
    help = 'Test the welcome email signal'

    def handle(self, *args, **options):
        self.stdout.write("Testing Welcome Email Signal...")
        
        username = "testuser_google_789"
        email = "testgoogle3@example.com"
        
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
        self.stdout.write(f"Triggering user_signed_up for {username}...")
        user_signed_up.send(sender=User, request=request, user=user)
        self.stdout.write(self.style.SUCCESS("Signal triggered. Check console output above for email content."))
