from django.contrib import admin
from .models import Tenderss

@admin.register(Tenderss)
class TenderssAdmin(admin.ModelAdmin):
    list_display = ('tender_id', 'title', 'category', 'status', 'closing_date', 'estimated_value')
    list_filter = ('status', 'category')
    search_fields = ('tender_id', 'title', 'department')
