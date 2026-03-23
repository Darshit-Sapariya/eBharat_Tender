from django.db import models

from tenders.models import Tenderss
from django.contrib.auth.models import User

# Create your models here.
class TenderApplication(models.Model):

    # ================= BASIC RELATION =================
    tender = models.ForeignKey(Tenderss, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)

    # ================= COMPANY DETAILS =================
    company_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=50)
    registered_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    gst_document = models.FileField(upload_to='tender_documents/gst/')

    # ================= AUTHORIZED BIDDER DETAILS =================
    bidder_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100)
    official_email = models.EmailField()
    mobile_number = models.CharField(max_length=15)

    # ================= FINANCIAL DETAILS =================
    financial_statement = models.FileField(upload_to='tender_documents/financial_statements/')

    # ================= BIDDING DETAILS =================
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    technical_document = models.FileField(upload_to='tender_documents/technical/')
    financial_document = models.FileField(upload_to='tender_documents/financial/')
    other_document = models.FileField(upload_to='tender_documents/other/', blank=True, null=True)

    # ================= STATUS & REVIEW =================
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('awarded', '🏆 Awarded'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remark = models.TextField(blank=True, null=True)

    # ================= PAYMENT DETAILS (EMD) =================
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    # ================= TIMESTAMP =================
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.tender.title}"