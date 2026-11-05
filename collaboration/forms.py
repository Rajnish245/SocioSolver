from django import forms
from .models import ProjectTeam, TeamMembership, ProjectTask, ProjectMilestone, TeamRole, TaskStatus, TaskPriority
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectTeamForm(forms.ModelForm):
    class Meta:
        model = ProjectTeam
        fields = ['name', 'description', 'proposal']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Campus EcoFlow Water Initiative'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your team mission, goals, and who you are looking to recruit.'
            }),
            'proposal': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        challenge = kwargs.pop('challenge', None)
        super().__init__(*args, **kwargs)
        if challenge:
            self.fields['proposal'].queryset = challenge.proposals.all()
            self.fields['proposal'].required = False
            self.fields['proposal'].empty_label = "None (Independent Implementation)"


class TeamJoinRequestForm(forms.ModelForm):
    class Meta:
        model = TeamMembership
        fields = ['role', 'join_message']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'join_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explain your relevant skills, availability, and what you hope to contribute to this team...'
            }),
        }


class ProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Task requirements and instructions'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            # Only allow assigning to accepted team members
            member_user_ids = team.memberships.filter(status='accepted').values_list('user_id', flat=True)
            self.fields['assigned_to'].queryset = User.objects.filter(id__in=member_user_ids)
            self.fields['assigned_to'].empty_label = "Unassigned"


class ProjectMilestoneForm(forms.ModelForm):
    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'target_date', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Milestone title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deliverables required to achieve this milestone'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
