from django.db import models
from django.conf import settings
from challenges.models import Challenge


class ProposalStatus(models.TextChoices):
    PROPOSED = 'proposed', 'Proposed'
    UNDER_REVIEW = 'under_review', 'Under Evaluation'
    ACCEPTED = 'accepted', 'Accepted for Implementation'
    IMPLEMENTED = 'implemented', 'Implemented'
    ARCHIVED = 'archived', 'Archived'


class SolutionProposal(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='proposals'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solution_proposals'
    )
    title = models.CharField(max_length=255)
    summary = models.TextField(
        help_text="A concise overview of the proposed solution."
    )
    detailed_plan = models.TextField(
        help_text="Step-by-step implementation roadmap and methodologies."
    )
    resources_needed = models.TextField(
        help_text="List of equipment, technical skills, software, or funding required."
    )
    estimated_timeline = models.CharField(
        max_length=100,
        help_text="Expected duration (e.g., 6 weeks, 3 months)."
    )
    estimated_budget = models.CharField(
        max_length=100,
        blank=True,
        help_text="Expected costs, if any (or specify 'Zero budget / Volunteer')."
    )
    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.PROPOSED
    )
    upvotes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-upvotes_count', '-created_at']

    def __str__(self):
        return f"{self.title} (for {self.challenge.title})"

    def update_upvotes_count(self):
        self.upvotes_count = self.votes.count()
        self.save(update_fields=['upvotes_count'])

    def has_user_voted(self, user):
        if not user.is_authenticated:
            return False
        return self.votes.filter(user=user).exists()


class SolutionVote(models.Model):
    """
    Enforces strictly 1 vote per user per proposal.
    """
    proposal = models.ForeignKey(
        SolutionProposal,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solution_votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('proposal', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} voted on {self.proposal.title}"


class DiscussionComment(models.Model):
    """
    Discussion comment that can be attached to a Challenge or a Solution Proposal.
    """
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    proposal = models.ForeignKey(
        SolutionProposal,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        target = self.proposal.title if self.proposal else (self.challenge.title if self.challenge else "General")
        return f"Comment by {self.author.username} on {target}"
