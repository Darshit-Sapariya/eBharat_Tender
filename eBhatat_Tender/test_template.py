import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eBhatat_Tender.settings')
django.setup()

from django.template import Template, Context

try:
    t = Template("{% load socialaccount %}{% provider_login_url 'google' %}")
    print(t.render(Context({})))
except Exception as e:
    import traceback
    traceback.print_exc()
