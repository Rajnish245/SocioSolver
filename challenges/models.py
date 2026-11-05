from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class ChallengeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(
        max_length=50,
        default='bi-lightbulb',
        help_text="Bootstrap icon class name, e.g. bi-droplet, bi-tree, bi-heart-pulse"
    )

    class Meta:
        verbose_name_plural = 'Challenge Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ChallengeStatus(models.TextChoices):
    OPEN = 'open', 'Open for Solutions'
    IN_PROGRESS = 'in_progress', 'Team Working (In Progress)'
    RESOLVED = 'resolved', 'Resolved & Implemented'
    CLOSED = 'closed', 'Closed'


class ChallengePriority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class ModerationStatus(models.TextChoices):
    APPROVED = 'approved', 'Approved'
    UNDER_REVIEW = 'under_review', 'Under Review'
    REJECTED = 'rejected', 'Rejected'


class Challenge(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(
        help_text="Provide a clear, detailed description of the societal challenge."
    )
    category = models.ForeignKey(
        ChallengeCategory,
        on_delete=models.PROTECT,
        related_name='challenges'
    )
    location = models.CharField(
        max_length=255,
        help_text="City, campus, or geographic area impacted."
    )
    problem_image = models.ImageField(
        upload_to='challenges/',
        blank=True,
        null=True,
        help_text="Optional photo illustrating the issue (Max 5MB)."
    )
    affected_community = models.CharField(
        max_length=255,
        help_text="Who is impacted? E.g., Campus residents, rural farmers, local commuters."
    )
    status = models.CharField(
        max_length=20,
        choices=ChallengeStatus.choices,
        default=ChallengeStatus.OPEN
    )
    priority = models.CharField(
        max_length=20,
        choices=ChallengePriority.choices,
        default=ChallengePriority.MEDIUM,
        help_text="Current priority assessment (can be refined via AI analysis)."
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_challenges'
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)

    # Moderation
    is_flagged = models.BooleanField(default=False)
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.APPROVED
    )

    # AI Cache & Vector storage
    embedding = models.JSONField(
        blank=True,
        null=True,
        help_text="Vector embedding for semantic search comparisons."
    )
    ai_analysis_cache = models.JSONField(
        blank=True,
        null=True,
        help_text="Cached AI Analyzer structured evaluation."
    )
    ai_solutions_cache = models.JSONField(
        blank=True,
        null=True,
        help_text="Cached AI generated solutions."
    )

    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'challenge'
            unique_id = uuid.uuid4().hex[:8]
            self.slug = f"{base_slug[:60]}-{unique_id}"
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status == ChallengeStatus.OPEN

    @property
    def is_resolved(self):
        return self.status == ChallengeStatus.RESOLVED


class ChallengeReportReason(models.TextChoices):
    INAPPROPRIATE = 'inappropriate', 'Inappropriate or Offensive Content'
    MISLEADING = 'misleading', 'Misleading Information or False Claim'
    SPAM = 'spam', 'Spam or Commercial Promotion'
    DUPLICATE = 'duplicate', 'Duplicate Challenge'
    OTHER = 'other', 'Other Issue'


class ChallengeReport(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )
    reason = models.CharField(
        max_length=30,
        choices=ChallengeReportReason.choices,
        default=ChallengeReportReason.OTHER
    )
    details = models.TextField(
        help_text="Provide context on why this challenge needs moderation."
    )
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on '{self.challenge.title}' by {self.reported_by.username}"


class ChallengeBookmark(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarked_challenges'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('challenge', 'user')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.challenge.title}"
