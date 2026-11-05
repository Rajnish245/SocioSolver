from django.contrib import admin
from .models import AIAnalysisLog


@admin.register(AIAnalysisLog)
class AIAnalysisLogAdmin(admin.ModelAdmin):
    list_display = ['service_type', 'user', 'challenge', 'model_used', 'tokens_used', 'success', 'created_at']
    list_filter = ['service_type', 'success', 'model_used', 'created_at']
    search_fields = ['prompt_summary', 'user__username', 'challenge__title', 'error_message']
    readonly_fields = ['created_at']
