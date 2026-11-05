from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from challenges.models import Challenge
from .models import SolutionProposal, SolutionVote, DiscussionComment
from .forms import SolutionProposalForm, DiscussionCommentForm


@login_required
def proposal_create_view(request, challenge_slug):
    """
    Submit a new solution proposal for a specific challenge.
    """
    challenge = get_object_or_404(Challenge, slug=challenge_slug)

    if request.method == 'POST':
        form = SolutionProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.challenge = challenge
            proposal.author = request.user
            proposal.save()
            messages.success(request, f"Your proposal '{proposal.title}' has been submitted for community review!")
            return redirect('solutions:proposal_detail', pk=proposal.pk)
        else:
            messages.error(request, "Please correct the errors in your solution proposal.")
    else:
        form = SolutionProposalForm()

    return render(request, 'solutions/proposal_form.html', {
        'form': form,
        'challenge': challenge,
        'action': 'Submit'
    })


def proposal_detail_view(request, pk):
    """
    Detailed view of a single solution proposal.
    """
    proposal = get_object_or_404(
        SolutionProposal.objects.select_related('challenge', 'author'),
        pk=pk
    )
    comments = proposal.comments.select_related('author').order_by('created_at')
    comment_form = DiscussionCommentForm()
    
    user_has_voted = False
    if request.user.is_authenticated:
        user_has_voted = proposal.votes.filter(user=request.user).exists()

    context = {
        'proposal': proposal,
        'challenge': proposal.challenge,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_voted': user_has_voted,
    }
    return render(request, 'solutions/proposal_detail.html', context)


@login_required
def proposal_update_view(request, pk):
    """
    Edit a solution proposal. Author or Administrator only.
    """
    proposal = get_object_or_404(SolutionProposal, pk=pk)

    if proposal.author != request.user and not request.user.is_administrator:
        messages.error(request, "You do not have permission to edit this proposal.")
        return redirect('solutions:proposal_detail', pk=proposal.pk)

    if request.method == 'POST':
        form = SolutionProposalForm(request.POST, instance=proposal)
        if form.is_valid():
            form.save()
            messages.success(request, "Proposal updated successfully.")
            return redirect('solutions:proposal_detail', pk=proposal.pk)
    else:
        form = SolutionProposalForm(instance=proposal)

    return render(request, 'solutions/proposal_form.html', {
        'form': form,
        'challenge': proposal.challenge,
        'proposal': proposal,
        'action': 'Edit'
    })


@login_required
def proposal_delete_view(request, pk):
    """
    Delete a solution proposal. Author or Administrator only.
    """
    proposal = get_object_or_404(SolutionProposal, pk=pk)

    if proposal.author != request.user and not request.user.is_administrator:
        messages.error(request, "You do not have permission to delete this proposal.")
        return redirect('solutions:proposal_detail', pk=proposal.pk)

    challenge_slug = proposal.challenge.slug
    if request.method == 'POST':
        proposal.delete()
        messages.success(request, "Proposal has been removed.")
        return redirect('challenges:challenge_detail', slug=challenge_slug)

    return render(request, 'solutions/proposal_confirm_delete.html', {
        'proposal': proposal,
        'challenge': proposal.challenge
    })


@login_required
def toggle_vote_view(request, pk):
    """
    Cast or revoke an upvote on a solution proposal.
    Strictly 1 vote per user per proposal enforced atomically.
    """
    proposal = get_object_or_404(SolutionProposal, pk=pk)
    user = request.user

    with transaction.atomic():
        existing_vote = SolutionVote.objects.filter(proposal=proposal, user=user)
        if existing_vote.exists():
            existing_vote.delete()
            voted = False
        else:
            SolutionVote.objects.create(proposal=proposal, user=user)
            voted = True

        proposal.update_upvotes_count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'voted': voted,
            'upvotes_count': proposal.upvotes_count
        })

    if voted:
        messages.success(request, f"Upvoted '{proposal.title}'!")
    else:
        messages.info(request, f"Removed upvote from '{proposal.title}'.")

    # Redirect back to where the request came from
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('solutions:proposal_detail', pk=proposal.pk)


@login_required
def add_comment_view(request):
    """
    Submit a comment either on a challenge or on a specific solution proposal.
    """
    if request.method == 'POST':
        form = DiscussionCommentForm(request.POST)
        challenge_id = request.POST.get('challenge_id')
        proposal_id = request.POST.get('proposal_id')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user

            if proposal_id:
                proposal = get_object_or_404(SolutionProposal, pk=proposal_id)
                comment.proposal = proposal
                comment.save()
                messages.success(request, "Comment posted successfully.")
                return redirect('solutions:proposal_detail', pk=proposal.pk)
            elif challenge_id:
                challenge = get_object_or_404(Challenge, pk=challenge_id)
                comment.challenge = challenge
                comment.save()
                messages.success(request, "Discussion comment added.")
                return redirect('challenges:challenge_detail', slug=challenge.slug)
        else:
            messages.error(request, "Cannot submit an empty comment.")

    return redirect('challenges:challenge_list')
