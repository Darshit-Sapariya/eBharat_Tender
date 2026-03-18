import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eBhatat_Tender.settings')
django.setup()

from django.template import Template, Context
from django.contrib.auth.models import User, AnonymousUser

# Create a user without a profile
user, _ = User.objects.get_or_create(username='testuser')
# Delete the profile if it was auto-created
if hasattr(user, 'userprofile'):
    user.userprofile.delete()

# Test superuser without profile
su = User.objects.filter(is_superuser=True).first()
if su and hasattr(su, 'userprofile'):
    su.userprofile.delete()

# The template giving error
t = Template('{% if user.userprofile.profile_pic %}yes{% else %}no{% endif %}')

try:
    print('Testing testuser:', t.render(Context({'user': user})))
except Exception as e:
    print(f"Error testuser: {type(e).__name__}: {e}")

try:
    if su:
        print('Testing superuser:', t.render(Context({'user': su})))
except Exception as e:
    print(f"Error superuser: {type(e).__name__}: {e}")

try:
    print('Testing Anonymous:', t.render(Context({'user': AnonymousUser()})))
except Exception as e:
    print(f"Error Anonymous: {type(e).__name__}: {e}")
