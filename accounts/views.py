from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserProfileUpdateForm, CustomLoginForm
from challenges.models import Challenge
from solutions.models import SolutionProposal
from collaboration.models import ProjectTeam, ProjectTask, TeamMembership
from partnerships.models import PartnershipRequest

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to SocioSolve, {user.first_name or user.username}! Your account has been created.")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Please correct the errors in the registration form below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'accounts:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('challenges:landing')


@login_required
def dashboard_view(request):
    user = request.user
    
    # User's challenges
    my_challenges = Challenge.objects.filter(creator=user).select_related('category')
    
    # User's solution proposals
    my_proposals = SolutionProposal.objects.filter(author=user).select_related('challenge')
    
    # User's teams (founded or member)
    my_team_memberships = TeamMembership.objects.filter(user=user, status='accepted').select_related('team', 'team__challenge')
    
    # User's tasks
    my_tasks = ProjectTask.objects.filter(assigned_to=user).select_related('team').order_by('due_date', 'status')
    
    # User's bookmarks
    bookmarked_challenges = Challenge.objects.filter(bookmarks__user=user).select_related('category')
    
    # Organization specific data
    org_partnership_requests = []
    if user.is_organization:
        org_partnership_requests = PartnershipRequest.objects.filter(organization=user).select_related('challenge')

    context = {
        'my_challenges': my_challenges,
        'my_proposals': my_proposals,
        'my_team_memberships': my_team_memberships,
        'my_tasks': my_tasks,
        'bookmarked_challenges': bookmarked_challenges,
        'org_partnership_requests': org_partnership_requests,
        'stats': {
            'challenges_count': my_challenges.count(),
            'proposals_count': my_proposals.count(),
            'teams_count': my_team_memberships.count(),
            'tasks_count': my_tasks.count(),
            'pending_tasks_count': my_tasks.exclude(status='done').count(),
        }
    }
    return render(request, 'accounts/dashboard.html', context)


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_challenges = Challenge.objects.filter(creator=profile_user, moderation_status='approved').select_related('category')
    user_proposals = SolutionProposal.objects.filter(author=profile_user).select_related('challenge')
    user_teams = TeamMembership.objects.filter(user=profile_user, status='accepted').select_related('team')
    
    context = {
        'profile_user': profile_user,
        'user_challenges': user_challenges,
        'user_proposals': user_proposals,
        'user_teams': user_teams,
        'is_own_profile': request.user.is_authenticated and request.user == profile_user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been successfully updated!")
            return redirect('accounts:profile', username=request.user.username)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})
