from django.db import models
from django.conf import settings
from challenges.models import Challenge
from solutions.models import SolutionProposal


class TeamRole(models.TextChoices):
    LEAD = 'lead', 'Team Lead'
    CONTRIBUTOR = 'contributor', 'Core Contributor'
    ADVISOR = 'advisor', 'Technical Advisor / Mentor'
    VOLUNTEER = 'volunteer', 'Volunteer'
    OBSERVER = 'observer', 'Observer'


class MembershipStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Review'
    ACCEPTED = 'accepted', 'Accepted Member'
    REJECTED = 'rejected', 'Declined'


class ProjectTeam(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    proposal = models.ForeignKey(
        SolutionProposal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams',
        help_text="Optional solution proposal guiding this project."
    )
    name = models.CharField(max_length=255)
    description = models.TextField(
        help_text="Team charter, objectives, and collaboration guidelines."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='founded_teams'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.challenge.title})"

    def is_lead(self, user):
        if not user.is_authenticated:
            return False
        if user == self.created_by or user.is_superuser:
            return True
        return self.memberships.filter(
            user=user,
            role=TeamRole.LEAD,
            status=MembershipStatus.ACCEPTED
        ).exists()

    def is_member(self, user):
        if not user.is_authenticated:
            return False
        if user == self.created_by or user.is_superuser:
            return True
        return self.memberships.filter(
            user=user,
            status=MembershipStatus.ACCEPTED
        ).exists()

    def can_manage(self, user):
        return self.is_lead(user)


class TeamMembership(models.Model):
    team = models.ForeignKey(
        ProjectTeam,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=TeamRole.choices,
        default=TeamRole.CONTRIBUTOR
    )
    status = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.PENDING
    )
    join_message = models.TextField(
        blank=True,
        help_text="Explain your skills, background, and how you want to contribute."
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.status})"


class TaskStatus(models.TextChoices):
    TODO = 'todo', 'To Do'
    IN_PROGRESS = 'in_progress', 'In Progress'
    IN_REVIEW = 'in_review', 'In Review'
    DONE = 'done', 'Completed'


class TaskPriority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class ProjectTask(models.Model):
    team = models.ForeignKey(
        ProjectTeam,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


class ProjectMilestone(models.Model):
    team = models.ForeignKey(
        ProjectTeam,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        help_text="Key deliverable or goal for this milestone."
    )
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_milestones'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date', 'created_at']

    def __str__(self):
        status = "Done" if self.is_completed else "Pending"
        return f"{self.title} ({status} - Due {self.target_date})"
