import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eBhatat_Tender.settings')
django.setup()

from tenders.models import Tenderss

tenders = Tenderss.objects.filter(tender_id__isnull=True)
print(f"Found {tenders.count()} tenders without ID.")

for t in tenders:
    t.save()
    print(f"Generated ID: {t.tender_id} for {t.title}")
