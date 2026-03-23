from django.db import models
from django.contrib.auth.models import User
from tenders.models import Tenderss

class Funding(models.Model):
    tender = models.ForeignKey(Tenderss, on_delete=models.SET_NULL, null=True, blank=True, related_name='fundings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate in %")
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class FundingApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='funding_applications')
    funding = models.ForeignKey(Funding, on_delete=models.CASCADE)
    tender = models.ForeignKey(Tenderss, on_delete=models.CASCADE)
    amount_requested = models.DecimalField(max_digits=15, decimal_places=2)
    purpose = models.TextField()
    supporting_document = models.FileField(upload_to='funding_docs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    admin_remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.funding.title}"
