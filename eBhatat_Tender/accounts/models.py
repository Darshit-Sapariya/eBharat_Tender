from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
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

    full_name = models.CharField(max_length=150)
    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)
    mobile = models.CharField(max_length=15)
    address = models.TextField()

    gov_id_type = models.CharField(max_length=50)
    gov_id_number = models.CharField(max_length=50)
    gov_id_upload = models.FileField(upload_to='gov_id/')

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    admin_remark = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# 🔹 AUTO CREATE PROFILE (except superuser)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)    