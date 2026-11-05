from django.contrib import admin
from .models import OrganizationProfile, PartnershipRequest, SponsoredChallenge


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ['official_name', 'org_type', 'user', 'headquarters', 'verified', 'created_at']
    list_filter = ['org_type', 'verified', 'created_at']
    search_fields = ['official_name', 'focus_areas', 'user__username']


@admin.register(PartnershipRequest)
class PartnershipRequestAdmin(admin.ModelAdmin):
    list_display = ['organization', 'challenge', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['organization__username', 'challenge__title', 'offered_support']


@admin.register(SponsoredChallenge)
class SponsoredChallengeAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'sponsor', 'grant_amount', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'currency', 'created_at']
    search_fields = ['challenge__title', 'sponsor__username']
