from django.test import TestCase
from django.utils import timezone
from .models import ActionLog
from django.contrib.auth.models import User
from datetime import timedelta

class TimezoneTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', is_staff=True, password='password')

    def test_audit_logs_today_ist_logic(self):
        # This test ensures that our filtering logic in the view (using localdate) 
        # matches how the database filters for the local date when USE_TZ=True.
        today = timezone.localdate()
        
        ActionLog.objects.create(
            admin_user=self.user,
            action_type="TEST",
            description="Test IST log",
            # No timestamp passed, defaults to timezone.now()
        )
        
        # This is what we now have in views.py
        audit_logs_today = ActionLog.objects.filter(timestamp__date=today).count()
        self.assertEqual(audit_logs_today, 1)
