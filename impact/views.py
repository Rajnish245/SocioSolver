import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeCategory, ChallengeStatus
from solutions.models import SolutionProposal
from collaboration.models import ProjectTeam, ProjectMilestone
from .models import ImpactReport
from .forms import ImpactReportForm

User = get_user_model()


def impact_dashboard_view(request):
    """
    Live database-backed societal impact dashboard.
    Calculates live statistics, distinguishes recorded vs estimated impact,
    and formats JSON payloads for Chart.js visualizations.
    """
    # High-level metrics
    total_challenges = Challenge.objects.filter(moderation_status='approved').count()
    open_challenges = Challenge.objects.filter(status=ChallengeStatus.OPEN).count()
    in_progress_challenges = Challenge.objects.filter(status=ChallengeStatus.IN_PROGRESS).count()
    resolved_challenges = Challenge.objects.filter(status=ChallengeStatus.RESOLVED).count()
    closed_challenges = Challenge.objects.filter(status=ChallengeStatus.CLOSED).count()

    active_projects = ProjectTeam.objects.filter(is_active=True).count()
    registered_collaborators = User.objects.filter(is_active=True).count()
    solutions_proposed = SolutionProposal.objects.count()

    total_milestones = ProjectMilestone.objects.count()
    completed_milestones = ProjectMilestone.objects.filter(is_completed=True).count()

    # Beneficiaries: distinct recorded verified vs self-reported/estimates
    verified_beneficiaries = ImpactReport.objects.filter(
        is_verified=True
    ).aggregate(total=Sum('beneficiaries_reached'))['total'] or 0

    estimated_beneficiaries = ImpactReport.objects.filter(
        is_verified=False
    ).aggregate(total=Sum('beneficiaries_reached'))['total'] or 0

    # Category Breakdown for Chart.js
    category_counts = ChallengeCategory.objects.annotate(
        approved_challenges=Count('challenges', filter=Q(challenges__moderation_status='approved'))
    ).values('name', 'approved_challenges')

    cat_labels = [c['name'] for c in category_counts if c['approved_challenges'] > 0]
    cat_data = [c['approved_challenges'] for c in category_counts if c['approved_challenges'] > 0]

    # If empty, add placeholder labels so chart gracefully displays empty state
    if not cat_labels:
        cat_labels = ['No Challenges Yet']
        cat_data = [0]

    # Status distribution for Doughnut Chart
    status_labels = ['Open', 'In Progress', 'Resolved', 'Closed']
    status_data = [open_challenges, in_progress_challenges, resolved_challenges, closed_challenges]

    # User Roles Distribution
    role_counts = User.objects.values('role').annotate(total=Count('id'))
    role_dict = {r['role']: r['total'] for r in role_counts}
    role_labels = ['Citizen', 'Student', 'University', 'Company', 'NGO', 'Admin']
    role_data = [
        role_dict.get('citizen', 0),
        role_dict.get('student', 0),
        role_dict.get('university', 0),
        role_dict.get('company', 0),
        role_dict.get('ngo', 0),
        role_dict.get('administrator', 0),
    ]

    # Recent verified and self-reported reports
    recent_reports = ImpactReport.objects.select_related('challenge', 'reported_by').order_by('-created_at')[:10]

    context = {
        'stats': {
            'total_challenges': total_challenges,
            'open_challenges': open_challenges,
            'in_progress_challenges': in_progress_challenges,
            'resolved_challenges': resolved_challenges,
            'closed_challenges': closed_challenges,
            'active_projects': active_projects,
            'registered_collaborators': registered_collaborators,
            'solutions_proposed': solutions_proposed,
            'total_milestones': total_milestones,
            'completed_milestones': completed_milestones,
            'milestone_completion_rate': round((completed_milestones / total_milestones * 100), 1) if total_milestones > 0 else 0,
            'verified_beneficiaries': verified_beneficiaries,
            'estimated_beneficiaries': estimated_beneficiaries,
            'total_beneficiaries': verified_beneficiaries + estimated_beneficiaries,
        },
        'cat_labels_json': json.dumps(cat_labels),
        'cat_data_json': json.dumps(cat_data),
        'status_labels_json': json.dumps(status_labels),
        'status_data_json': json.dumps(status_data),
        'role_labels_json': json.dumps(role_labels),
        'role_data_json': json.dumps(role_data),
        'recent_reports': recent_reports,
    }
    return render(request, 'impact/impact_dashboard.html', context)


@login_required
def impact_report_create_view(request, challenge_slug):
    """
    Submit an impact report for a challenge.
    Allowed for challenge creator, team lead, or administrator.
    """
    challenge = get_object_or_404(Challenge, slug=challenge_slug)

    # Permission check: Creator, Team lead, or Admin
    user_is_team_lead = ProjectTeam.objects.filter(challenge=challenge, memberships__user=request.user, memberships__role='lead').exists()
    if challenge.creator != request.user and not user_is_team_lead and not request.user.is_administrator:
        messages.error(request, "Only the challenge creator or project team lead can publish official impact reports.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    if request.method == 'POST':
        form = ImpactReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.challenge = challenge
            report.reported_by = request.user
            report.team = ProjectTeam.objects.filter(challenge=challenge).first()
            # If administrator submitted, mark verified, else self-reported
            report.is_verified = request.user.is_administrator
            report.save()

            # Mark challenge as resolved if user requests or if verified
            mark_resolved = request.POST.get('mark_resolved') == '1'
            if mark_resolved:
                challenge.status = ChallengeStatus.RESOLVED
                challenge.save(update_fields=['status'])

            status_note = "Officially Verified" if report.is_verified else "Self-Reported"
            messages.success(request, f"Impact Report '{report.title}' published successfully ({status_note})!")
            return redirect('impact:report_detail', pk=report.pk)
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = ImpactReportForm()

    return render(request, 'impact/impact_report_form.html', {
        'form': form,
        'challenge': challenge
    })


def impact_report_detail_view(request, pk):
    """
    View full details of an individual impact report.
    """
    report = get_object_or_404(
        ImpactReport.objects.select_related('challenge', 'team', 'reported_by'),
        pk=pk
    )
    return render(request, 'impact/impact_report_detail.html', {'report': report})
