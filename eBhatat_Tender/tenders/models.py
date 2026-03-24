from django.db import models
from django.contrib.auth.models import User

class Tenderss(models.Model):

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
        ('awarded', 'Awarded'),
    )

    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField()

    estimated_value = models.DecimalField(max_digits=15, decimal_places=2)
    emd_amount = models.DecimalField(max_digits=15, decimal_places=2)

    publish_date = models.DateField()
    closing_date = models.DateField()
    pre_bid_meeting = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    document = models.FileField(upload_to='tender_documents/')

    tender_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.tender_id:
            from django.utils import timezone
            year = timezone.localdate().year
            last_tender = Tenderss.objects.filter(tender_id__startswith=f"EBT-{year}").order_by("-id").first()
            if last_tender and last_tender.tender_id:
                try:
                    last_id = int(last_tender.tender_id.split("-")[-1])
                    new_id = last_id + 1
                except ValueError:
                    new_id = 1
            else:
                new_id = 1
            self.tender_id = f"EBT-{year}-{new_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tender_id} - {self.title}" if self.tender_id else self.title