from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class register(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)

class UserProfile(models.Model):

    ROLE_CHOICES = (
        ('creator', 'Tender Creator / Department'),
        ('bidder', 'Bidder / Vendor'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=150, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    gov_id_type = models.CharField(max_length=50, blank=True, null=True)
    gov_id_number = models.CharField(max_length=50, blank=True, null=True)
    gov_id_upload = models.FileField(upload_to='gov_id/', blank=True, null=True)

    designation = models.CharField(max_length=100, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    admin_remark = models.TextField(blank=True, null=True)

    @property
    def masked_id(self):
        if not self.gov_id_number:
            return ""
        # Mask all but the last 4 characters
        val = str(self.gov_id_number)
        return "*" * (len(val) - 4) + val[-4:] if len(val) > 4 else val

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"

class AdminRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.department_name} / {self.category_name}"

# 🔹 AUTO CREATE PROFILE 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Auto-approve superusers and staff
        status = 'approved' if (instance.is_superuser or instance.is_staff) else 'pending'
        UserProfile.objects.get_or_create(user=instance, defaults={'status': status})

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    tender = models.ForeignKey('tenders.Tenderss', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tender')

    def __str__(self):
        return f"{self.user.username} saved {self.tender.title}"