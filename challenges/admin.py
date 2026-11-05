from django.contrib import admin
from .models import ChallengeCategory, Challenge, ChallengeReport, ChallengeBookmark


@admin.register(ChallengeCategory)
class ChallengeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon_class']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'priority', 'creator', 'is_flagged', 'moderation_status', 'creation_date']
    list_filter = ['status', 'priority', 'moderation_status', 'is_flagged', 'category', 'creation_date']
    search_fields = ['title', 'description', 'location', 'affected_community', 'creator__username']
    prepopulated_fields = {'slug': ('title',)}
    actions = ['approve_challenges', 'flag_for_review']

    @admin.action(description='Approve selected challenges')
    def approve_challenges(self, request, queryset):
        queryset.update(moderation_status='approved', is_flagged=False)

    @admin.action(description='Flag selected challenges for review')
    def flag_for_review(self, request, queryset):
        queryset.update(moderation_status='under_review', is_flagged=True)


@admin.register(ChallengeReport)
class ChallengeReportAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'reported_by', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved', 'created_at']
    search_fields = ['challenge__title', 'reported_by__username', 'details']


@admin.register(ChallengeBookmark)
class ChallengeBookmarkAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'user', 'created_at']
