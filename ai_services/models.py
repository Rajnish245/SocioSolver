from django.db import models
from django.conf import settings
from challenges.models import Challenge


class AIServiceType(models.TextChoices):
    ANALYZE_CHALLENGE = 'analyze_challenge', 'AI Challenge Analyzer'
    GENERATE_SOLUTIONS = 'generate_solutions', 'AI Solution Generator'
    TEAM_MATCHING = 'team_matching', 'Smart Team Matching'
    FIND_SIMILAR = 'find_similar', 'Similar Challenge Search'


class AIAnalysisLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_requests'
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_logs'
    )
    service_type = models.CharField(
        max_length=30,
        choices=AIServiceType.choices
    )
    prompt_summary = models.CharField(max_length=255)
    response_json = models.JSONField(default=dict, blank=True)
    model_used = models.CharField(max_length=50, default='gpt-4o-mini')
    tokens_used = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_service_type_display()} by {self.user.username} at {self.created_at:%Y-%m-%d %H:%M}"
