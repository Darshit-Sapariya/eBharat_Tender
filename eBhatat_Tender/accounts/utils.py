from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_ebharat_email(subject, template_name, context, recipient_list, attachments=None):
    """
    Sends a high-quality HTML email using a template.
    """
    # 1. Render the HTML content from the template
    html_content = render_to_string(f'emails/{template_name}', context)
    
    # 2. Create the plain-text alternative (mostly for accessibility)
    text_content = strip_tags(html_content)
    
    # 3. Create the email message
    email = EmailMultiAlternatives(
        subject=f"{subject} | eBharat Tender",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list
    )
    
    # 4. Attach the HTML version
    email.attach_alternative(html_content, "text/html")
    
    # 5. Attach any files
    if attachments:
        for attachment in attachments:
            email.attach(attachment['filename'], attachment['content'], attachment['mimetype'])
    
    # 5. Send the email
    try:
        email.send()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False
