from django.db import models
from django.conf import settings
from challenges.models import Challenge
from collaboration.models import ProjectTeam


class ImpactReport(models.Model):
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='impact_reports'
    )
    team = models.ForeignKey(
        ProjectTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='impact_reports'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_impact_reports'
    )
    title = models.CharField(max_length=255)
    summary = models.TextField(
        help_text="Executive summary of the project outcome and societal difference made."
    )
    beneficiaries_reached = models.PositiveIntegerField(
        default=0,
        help_text="Direct count of citizens, students, or community members served."
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="True = Officially verified by institution/admin audit; False = Self-reported / estimated."
    )
    metrics_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured metrics (e.g., {'gallons_water_recycled': 50000, 'cost_reduction_percent': 35})."
    )
    environmental_impact = models.TextField(blank=True)
    social_impact = models.TextField(blank=True)
    challenges_overcome = models.TextField(blank=True)
    future_sustainability_plan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "Verified" if self.is_verified else "Self-Reported"
        return f"{self.title} ({status} - {self.challenge.title})"
