from django.dispatch import receiver
from django.contrib.sites.shortcuts import get_current_site
from allauth.account.signals import user_signed_up
from .utils import send_ebharat_email
import logging

logger = logging.getLogger(__name__)

@receiver(user_signed_up)
def send_welcome_email_on_signup(request, user, **kwargs):
    """
    Sends a welcome email when a user signs up via Google (or manual).
    """
    try:
        full_name = user.get_full_name() or user.username
        email = user.email
        username = user.username
        
        current_site = get_current_site(request)
        
        logger.info(f"Sending welcome email to {email}")
        
        send_ebharat_email(
            subject="Welcome to eBharat Tender Portal",
            template_name="welcome_email.html",
            context={
                "full_name": full_name,
                "username": username,
                "email": email,
                "domain": current_site.domain,
            },
            recipient_list=[email]
        )
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
