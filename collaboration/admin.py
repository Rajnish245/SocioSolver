from django.contrib import admin
from .models import ProjectTeam, TeamMembership, ProjectTask, ProjectMilestone


@admin.register(ProjectTeam)
class ProjectTeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'challenge', 'created_by', 'is_active', 'created_at']
    search_fields = ['name', 'challenge__title', 'created_by__username']
    list_filter = ['is_active', 'created_at']


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'role', 'status', 'joined_at']
    list_filter = ['role', 'status', 'joined_at']
    search_fields = ['user__username', 'team__name']


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'team', 'assigned_to', 'status', 'priority', 'due_date']
    list_filter = ['status', 'priority', 'due_date']
    search_fields = ['title', 'team__name', 'assigned_to__username']


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'team', 'target_date', 'is_completed', 'completed_date']
    list_filter = ['is_completed', 'target_date']
    search_fields = ['title', 'team__name']
