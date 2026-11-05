from django.contrib import admin
from .models import SolutionProposal, SolutionVote, DiscussionComment


@admin.register(SolutionProposal)
class SolutionProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'challenge', 'author', 'status', 'upvotes_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'summary', 'author__username', 'challenge__title']


@admin.register(SolutionVote)
class SolutionVoteAdmin(admin.ModelAdmin):
    list_display = ['proposal', 'user', 'created_at']
    search_fields = ['user__username', 'proposal__title']


@admin.register(DiscussionComment)
class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'challenge', 'proposal', 'created_at']
    search_fields = ['content', 'author__username']
