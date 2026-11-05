from django.contrib import admin
from .models import ImpactReport


@admin.register(ImpactReport)
class ImpactReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'challenge', 'reported_by', 'beneficiaries_reached', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['title', 'summary', 'challenge__title', 'reported_by__username']
    actions = ['verify_reports']

    @admin.action(description='Mark selected reports as officially verified')
    def verify_reports(self, request, queryset):
        queryset.update(is_verified=True)
