from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from challenges.models import Challenge
from .models import (
    ProjectTeam, TeamMembership, ProjectTask,
    ProjectMilestone, TeamRole, MembershipStatus, TaskStatus
)
from .forms import (
    ProjectTeamForm, TeamJoinRequestForm,
    ProjectTaskForm, ProjectMilestoneForm
)


@login_required
def team_create_view(request, challenge_slug):
    """
    Form a new collaborative team to tackle a challenge.
    """
    challenge = get_object_or_404(Challenge, slug=challenge_slug)

    if request.method == 'POST':
        form = ProjectTeamForm(request.POST, challenge=challenge)
        if form.is_valid():
            team = form.save(commit=False)
            team.challenge = challenge
            team.created_by = request.user
            team.save()

            # Auto-enroll creator as Team Lead
            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role=TeamRole.LEAD,
                status=MembershipStatus.ACCEPTED,
                join_message="Project founder"
            )

            # Update challenge status to in_progress if currently open
            if challenge.status == 'open':
                challenge.status = 'in_progress'
                challenge.save(update_fields=['status'])

            messages.success(request, f"Team '{team.name}' created! You are the Team Lead.")
            return redirect('collaboration:team_detail', pk=team.pk)
    else:
        form = ProjectTeamForm(challenge=challenge)

    return render(request, 'collaboration/team_form.html', {
        'form': form,
        'challenge': challenge,
        'action': 'Create'
    })


def team_detail_view(request, pk):
    """
    Full team workspace with members, tasks, kanban statuses, and milestones.
    """
    team = get_object_or_404(
        ProjectTeam.objects.select_related('challenge', 'created_by', 'proposal'),
        pk=pk
    )

    # Active members
    accepted_members = team.memberships.filter(
        status=MembershipStatus.ACCEPTED
    ).select_related('user')

    # Pending requests (for Team Lead review)
    pending_requests = []
    is_lead = False
    is_member = False
    my_membership = None

    if request.user.is_authenticated:
        is_lead = team.is_lead(request.user)
        is_member = team.is_member(request.user)
        my_membership = team.memberships.filter(user=request.user).first()
        if is_lead:
            pending_requests = team.memberships.filter(
                status=MembershipStatus.PENDING
            ).select_related('user')

    # Tasks grouped by status
    tasks = team.tasks.select_related('assigned_to', 'created_by').order_by('due_date', 'priority')
    todo_tasks = [t for t in tasks if t.status == TaskStatus.TODO]
    in_progress_tasks = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
    in_review_tasks = [t for t in tasks if t.status == TaskStatus.IN_REVIEW]
    done_tasks = [t for t in tasks if t.status == TaskStatus.DONE]

    # Milestones
    milestones = team.milestones.select_related('created_by').order_by('target_date')

    join_form = TeamJoinRequestForm()
    task_form = ProjectTaskForm(team=team)
    milestone_form = ProjectMilestoneForm()

    context = {
        'team': team,
        'challenge': team.challenge,
        'accepted_members': accepted_members,
        'pending_requests': pending_requests,
        'is_lead': is_lead,
        'is_member': is_member,
        'my_membership': my_membership,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'in_review_tasks': in_review_tasks,
        'done_tasks': done_tasks,
        'milestones': milestones,
        'join_form': join_form,
        'task_form': task_form,
        'milestone_form': milestone_form,
        'total_tasks_count': len(tasks),
        'completed_tasks_count': len(done_tasks),
    }
    return render(request, 'collaboration/team_detail.html', context)


@login_required
def team_join_request_view(request, pk):
    """
    Submit a request to join a project team.
    """
    team = get_object_or_404(ProjectTeam, pk=pk)

    if team.memberships.filter(user=request.user).exists():
        messages.warning(request, "You have already applied or are already a member of this team.")
        return redirect('collaboration:team_detail', pk=team.pk)

    if request.method == 'POST':
        form = TeamJoinRequestForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.team = team
            membership.user = request.user
            membership.status = MembershipStatus.PENDING
            membership.save()
            messages.success(request, "Your application to join the team has been submitted to the Team Lead!")
        else:
            messages.error(request, "Please check your join request submission.")

    return redirect('collaboration:team_detail', pk=team.pk)


@login_required
def team_membership_action_view(request, pk, membership_id, action):
    """
    Team Lead approval or rejection of member applications.
    """
    team = get_object_or_404(ProjectTeam, pk=pk)

    if not team.is_lead(request.user) and not request.user.is_administrator:
        messages.error(request, "Only the Team Lead can manage membership requests.")
        return redirect('collaboration:team_detail', pk=team.pk)

    membership = get_object_or_404(TeamMembership, pk=membership_id, team=team)

    if action == 'accept':
        membership.status = MembershipStatus.ACCEPTED
        membership.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Accepted {membership.user.username} into the team!")
    elif action == 'reject':
        membership.status = MembershipStatus.REJECTED
        membership.save(update_fields=['status', 'updated_at'])
        messages.info(request, f"Declined application from {membership.user.username}.")

    return redirect('collaboration:team_detail', pk=team.pk)


@login_required
def task_create_view(request, pk):
    """
    Add a task to the project workspace.
    """
    team = get_object_or_404(ProjectTeam, pk=pk)

    if not team.is_member(request.user) and not request.user.is_administrator:
        messages.error(request, "Only accepted team members can create project tasks.")
        return redirect('collaboration:team_detail', pk=team.pk)

    if request.method == 'POST':
        form = ProjectTaskForm(request.POST, team=team)
        if form.is_valid():
            task = form.save(commit=False)
            task.team = team
            task.created_by = request.user
            task.save()
            messages.success(request, f"Task '{task.title}' created.")
        else:
            messages.error(request, "Could not create task. Check form errors.")

    return redirect('collaboration:team_detail', pk=team.pk)


@login_required
def task_update_status_view(request, pk, task_id):
    """
    Update task status (e.g. from Todo to In Progress or Done).
    """
    team = get_object_or_404(ProjectTeam, pk=pk)
    task = get_object_or_404(ProjectTask, pk=task_id, team=team)

    if not team.is_member(request.user) and not request.user.is_administrator:
        messages.error(request, "Only accepted team members can update task status.")
        return redirect('collaboration:team_detail', pk=team.pk)

    new_status = request.POST.get('status')
    if new_status in [s[0] for s in TaskStatus.choices]:
        task.status = new_status
        task.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Task status updated to {task.get_status_display()}.")

    return redirect('collaboration:team_detail', pk=team.pk)


@login_required
def task_delete_view(request, pk, task_id):
    """
    Delete a task.
    """
    team = get_object_or_404(ProjectTeam, pk=pk)
    task = get_object_or_404(ProjectTask, pk=task_id, team=team)

    if not team.is_lead(request.user) and task.created_by != request.user and not request.user.is_administrator:
        messages.error(request, "You are not authorized to delete this task.")
        return redirect('collaboration:team_detail', pk=team.pk)

    task.delete()
    messages.success(request, "Task deleted.")
    return redirect('collaboration:team_detail', pk=team.pk)


@login_required
def milestone_create_view(request, pk):
    """
    Add a project milestone.
    """
    team = get_object_or_404(ProjectTeam, pk=pk)

    if not team.is_member(request.user) and not request.user.is_administrator:
        messages.error(request, "Only team members can create milestones.")
        return redirect('collaboration:team_detail', pk=team.pk)

    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.team = team
            milestone.created_by = request.user
            if milestone.is_completed:
                milestone.completed_date = timezone.now().date()
            milestone.save()
            messages.success(request, f"Milestone '{milestone.title}' added.")
        else:
            messages.error(request, "Check milestone form inputs.")

    return redirect('collaboration:team_detail', pk=team.pk)


@login_required
def milestone_toggle_view(request, pk, milestone_id):
    """
    Toggle milestone completion state.
    """
    team = get_object_or_404(ProjectTeam, pk=pk)
    milestone = get_object_or_404(ProjectMilestone, pk=milestone_id, team=team)

    if not team.is_member(request.user) and not request.user.is_administrator:
        messages.error(request, "Only team members can update milestones.")
        return redirect('collaboration:team_detail', pk=team.pk)

    milestone.is_completed = not milestone.is_completed
    if milestone.is_completed:
        milestone.completed_date = timezone.now().date()
    else:
        milestone.completed_date = None
    milestone.save(update_fields=['is_completed', 'completed_date', 'updated_at'])

    status_str = "completed" if milestone.is_completed else "marked as pending"
    messages.success(request, f"Milestone '{milestone.title}' is now {status_str}.")
    return redirect('collaboration:team_detail', pk=team.pk)
