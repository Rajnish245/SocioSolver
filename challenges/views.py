from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import (
    Challenge, ChallengeCategory, ChallengeStatus,
    ChallengePriority, ChallengeReport, ChallengeBookmark
)
from .forms import ChallengeForm, ChallengeReportForm
from solutions.models import SolutionProposal, DiscussionComment
from solutions.forms import SolutionProposalForm, DiscussionCommentForm
from collaboration.models import ProjectTeam
from impact.models import ImpactReport


def landing_page_view(request):
    """
    Public landing page introducing SocioSolve, key impact metrics,
    featured challenges, and call to action.
    """
    categories = ChallengeCategory.objects.annotate(
        challenge_count=Count('challenges', filter=Q(challenges__moderation_status='approved'))
    )
    featured_challenges = Challenge.objects.filter(
        moderation_status='approved'
    ).select_related('category', 'creator').order_by('-views_count', '-creation_date')[:6]

    # Live statistics
    total_challenges = Challenge.objects.filter(moderation_status='approved').count()
    resolved_challenges = Challenge.objects.filter(status=ChallengeStatus.RESOLVED).count()
    total_proposals = SolutionProposal.objects.count()
    active_teams = ProjectTeam.objects.filter(is_active=True).count()

    context = {
        'categories': categories,
        'featured_challenges': featured_challenges,
        'stats': {
            'total_challenges': total_challenges,
            'resolved_challenges': resolved_challenges,
            'total_proposals': total_proposals,
            'active_teams': active_teams,
        }
    }
    return render(request, 'landing.html', context)


def challenge_list_view(request):
    """
    Search, filter, sort, and paginate societal challenges.
    """
    queryset = Challenge.objects.filter(
        moderation_status='approved'
    ).select_related('category', 'creator').annotate(
        proposals_total=Count('proposals', distinct=True),
        comments_total=Count('comments', distinct=True)
    )

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q) |
            Q(affected_community__icontains=q)
        )

    # Category filter
    category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(ChallengeCategory, slug=category_slug)
        queryset = queryset.filter(category=selected_category)

    # Status filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter in [c[0] for c in ChallengeStatus.choices]:
        queryset = queryset.filter(status=status_filter)

    # Priority filter
    priority_filter = request.GET.get('priority', '').strip()
    if priority_filter in [p[0] for p in ChallengePriority.choices]:
        queryset = queryset.filter(priority=priority_filter)

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        queryset = queryset.order_by('-views_count', '-creation_date')
    elif sort_by == 'most_solutions':
        queryset = queryset.order_by('-proposals_total', '-creation_date')
    elif sort_by == 'most_discussed':
        queryset = queryset.order_by('-comments_total', '-creation_date')
    elif sort_by == 'priority':
        queryset = queryset.order_by('priority', '-creation_date')
    else:  # 'newest'
        queryset = queryset.order_by('-creation_date')

    # Pagination: 9 per page
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = ChallengeCategory.objects.annotate(
        c_count=Count('challenges', filter=Q(challenges__moderation_status='approved'))
    )

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'q': q,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by,
        'statuses': ChallengeStatus.choices,
        'priorities': ChallengePriority.choices,
    }
    return render(request, 'challenges/challenge_list.html', context)


def challenge_detail_view(request, slug):
    """
    Challenge detail page displaying descriptions, proposal submissions,
    voting, community comments, active teams, and AI analysis.
    """
    challenge = get_object_or_404(
        Challenge.objects.select_related('category', 'creator'),
        slug=slug
    )

    # Increment view count
    Challenge.objects.filter(pk=challenge.pk).update(views_count=challenge.views_count + 1)
    challenge.views_count += 1

    # Proposals for this challenge
    proposals = challenge.proposals.select_related('author').prefetch_related('votes').order_by('-upvotes_count', '-created_at')

    # Comments for this challenge
    comments = challenge.comments.filter(proposal__isnull=True).select_related('author').order_by('created_at')

    # Teams working on this challenge
    teams = challenge.teams.filter(is_active=True).select_related('created_by')

    # Impact reports
    impact_reports = challenge.impact_reports.all()

    # Is bookmarked by user
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = challenge.bookmarks.filter(user=request.user).exists()

    proposal_form = SolutionProposalForm()
    comment_form = DiscussionCommentForm()
    report_form = ChallengeReportForm()

    context = {
        'challenge': challenge,
        'proposals': proposals,
        'comments': comments,
        'teams': teams,
        'impact_reports': impact_reports,
        'is_bookmarked': is_bookmarked,
        'proposal_form': proposal_form,
        'comment_form': comment_form,
        'report_form': report_form,
    }
    return render(request, 'challenges/challenge_detail.html', context)


@login_required
def challenge_create_view(request):
    """
    Create a new societal challenge.
    """
    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.creator = request.user
            challenge.save()
            messages.success(request, f"Challenge '{challenge.title}' posted successfully! You can now analyze it with AI or invite collaborators.")
            return redirect('challenges:challenge_detail', slug=challenge.slug)
        else:
            messages.error(request, "Please correct the errors in the challenge submission form.")
    else:
        form = ChallengeForm()

    return render(request, 'challenges/challenge_form.html', {'form': form, 'action': 'Create'})


@login_required
def challenge_update_view(request, slug):
    """
    Update an existing challenge. Only creator or administrator.
    """
    challenge = get_object_or_404(Challenge, slug=slug)

    if challenge.creator != request.user and not request.user.is_administrator:
        messages.error(request, "You are not authorized to edit this challenge.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES, instance=challenge)
        if form.is_valid():
            form.save()
            messages.success(request, "Challenge details updated successfully.")
            return redirect('challenges:challenge_detail', slug=challenge.slug)
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = ChallengeForm(instance=challenge)

    return render(request, 'challenges/challenge_form.html', {
        'form': form,
        'challenge': challenge,
        'action': 'Edit'
    })


@login_required
def challenge_delete_view(request, slug):
    """
    Delete a challenge. Only creator or administrator.
    """
    challenge = get_object_or_404(Challenge, slug=slug)

    if challenge.creator != request.user and not request.user.is_administrator:
        messages.error(request, "You are not authorized to delete this challenge.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    if request.method == 'POST':
        title = challenge.title
        challenge.delete()
        messages.success(request, f"Challenge '{title}' has been deleted.")
        return redirect('challenges:challenge_list')

    return render(request, 'challenges/challenge_confirm_delete.html', {'challenge': challenge})


@login_required
def challenge_report_view(request, slug):
    """
    Submit a moderation report for a challenge.
    """
    challenge = get_object_or_404(Challenge, slug=slug)

    if request.method == 'POST':
        form = ChallengeReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.challenge = challenge
            report.reported_by = request.user
            report.save()

            challenge.is_flagged = True
            challenge.save(update_fields=['is_flagged'])

            messages.success(request, "Thank you for helping keep SocioSolve safe. Your report has been submitted to moderators.")
            return redirect('challenges:challenge_detail', slug=challenge.slug)
        else:
            messages.error(request, "Please provide complete details in the report.")

    return redirect('challenges:challenge_detail', slug=challenge.slug)


@login_required
def toggle_bookmark_view(request, slug):
    """
    Bookmark or remove bookmark for a challenge.
    """
    challenge = get_object_or_404(Challenge, slug=slug)
    bookmark = ChallengeBookmark.objects.filter(challenge=challenge, user=request.user)

    if bookmark.exists():
        bookmark.delete()
        bookmarked = False
        messages.info(request, "Removed from your saved bookmarks.")
    else:
        ChallengeBookmark.objects.create(challenge=challenge, user=request.user)
        bookmarked = True
        messages.success(request, "Challenge added to your bookmarks!")

    # Support AJAX or standard redirect
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'bookmarked': bookmarked})

    return redirect('challenges:challenge_detail', slug=challenge.slug)
