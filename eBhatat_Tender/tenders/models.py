from django.db import models
from django.contrib.auth.models import User

class Tenderss(models.Model):

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    )

    CATEGORY_CHOICES = (
        ('Infrastructure', 'Infrastructure'),
        ('Construction', 'Construction'),
        ('Road & Highway', 'Road & Highway'),
        ('Water Supply', 'Water Supply'),
        ('IT & Software', 'IT & Software'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Energy & Power', 'Energy & Power'),
    )

    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField()

    estimated_value = models.DecimalField(max_digits=15, decimal_places=2)
    emd_amount = models.DecimalField(max_digits=15, decimal_places=2)

    publish_date = models.DateField()
    closing_date = models.DateField()
    pre_bid_meeting = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    document = models.FileField(upload_to='tender_documents/')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)