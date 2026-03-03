from django.contrib import admin

from bids.models import TenderApplication

# Register your models here.


admin.site.register(TenderApplication),
admin.site.site_header = "eBhatat Tender Admin"
admin.site.site_title = "eBhatat Tender Admin Portal"   
admin.site.index_title = "Welcome to eBhatat Tender Admin Portal"
