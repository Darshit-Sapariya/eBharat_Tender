from django.contrib import admin
from .models import Funding, FundingApplication

@admin.register(Funding)
class FundingAdmin(admin.ModelAdmin):
    list_display = ('title', 'tender', 'interest_rate', 'max_amount', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('tender',)

@admin.register(FundingApplication)
class FundingApplicationAdmin(admin.ModelAdmin):
    list_display = ('bidder', 'funding', 'tender', 'amount_requested', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('bidder__username', 'funding__title', 'tender__title')
    actions = ['approve_funding', 'reject_funding']

    @admin.action(description="Approve selected funding applications")
    def approve_funding(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description="Reject selected funding applications")
    def reject_funding(self, request, queryset):
        queryset.update(status='rejected')
