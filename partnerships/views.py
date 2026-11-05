from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from challenges.models import Challenge
from .models import (
    OrganizationProfile, PartnershipRequest,
    SponsoredChallenge, PartnershipStatus, OrganizationType
)
from .forms import OrganizationProfileForm, PartnershipRequestForm, SponsoredChallengeForm


def org_list_view(request):
    """
    Public directory of universities, companies, and NGOs supporting SocioSolve.
    """
    org_type_filter = request.GET.get('type', '')
    profiles = OrganizationProfile.objects.select_related('user')
    
    if org_type_filter in [t[0] for t in OrganizationType.choices]:
        profiles = profiles.filter(org_type=org_type_filter)

    context = {
        'profiles': profiles,
        'types': OrganizationType.choices,
        'selected_type': org_type_filter,
    }
    return render(request, 'partnerships/org_list.html', context)


def org_detail_view(request, pk):
    """
    Detailed profile page for an organization.
    """
    profile = get_object_or_404(
        OrganizationProfile.objects.select_related('user'),
        pk=pk
    )
    sponsored_challenges = SponsoredChallenge.objects.filter(
        sponsor=profile.user,
        is_active=True
    ).select_related('challenge')

    active_partnerships = PartnershipRequest.objects.filter(
        organization=profile.user,
        status=PartnershipStatus.APPROVED
    ).select_related('challenge')

    context = {
        'profile': profile,
        'sponsored_challenges': sponsored_challenges,
        'active_partnerships': active_partnerships,
        'is_owner': request.user.is_authenticated and request.user == profile.user,
    }
    return render(request, 'partnerships/org_detail.html', context)


@login_required
def org_profile_manage_view(request):
    """
    Create or edit institutional profile.
    Available to University, Company, NGO, and Admin roles.
    """
    if not request.user.is_organization and not request.user.is_administrator:
        messages.error(request, "Only university, corporate, or NGO representatives can create an organization profile.")
        return redirect('accounts:dashboard')

    profile, created = OrganizationProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'official_name': request.user.organization_name or request.user.get_full_name() or request.user.username,
            'org_type': request.user.role if request.user.role in [t[0] for t in OrganizationType.choices] else OrganizationType.NGO,
        }
    )

    if request.method == 'POST':
        form = OrganizationProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Organization profile updated successfully!")
            return redirect('partnerships:org_detail', pk=profile.pk)
        else:
            messages.error(request, "Please check form entries.")
    else:
        form = OrganizationProfileForm(instance=profile)

    return render(request, 'partnerships/org_form.html', {'form': form, 'profile': profile})


@login_required
def partnership_request_create_view(request, challenge_slug):
    """
    An organization requests to officially partner with a challenge.
    """
    challenge = get_object_or_404(Challenge, slug=challenge_slug)

    if not request.user.is_organization and not request.user.is_administrator:
        messages.error(request, "Only registered organizations (Universities, Companies, NGOs) can initiate institutional partnerships.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    # Check for existing request
    existing = PartnershipRequest.objects.filter(challenge=challenge, organization=request.user).first()
    if existing:
        messages.info(request, f"You already have a {existing.get_status_display()} partnership request for this challenge.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    if request.method == 'POST':
        form = PartnershipRequestForm(request.POST)
        if form.is_valid():
            partnership = form.save(commit=False)
            partnership.challenge = challenge
            partnership.organization = request.user
            partnership.save()
            messages.success(request, f"Partnership proposal submitted to the creators of '{challenge.title}'!")
            return redirect('challenges:challenge_detail', slug=challenge.slug)
    else:
        form = PartnershipRequestForm()

    return render(request, 'partnerships/partnership_request_form.html', {
        'form': form,
        'challenge': challenge
    })


@login_required
def partnership_action_view(request, pk, action):
    """
    Challenge creator or admin approves or declines an incoming partnership request.
    """
    partnership = get_object_or_404(
        PartnershipRequest.objects.select_related('challenge', 'organization'),
        pk=pk
    )

    if partnership.challenge.creator != request.user and not request.user.is_administrator:
        messages.error(request, "Only the challenge creator can approve partnership proposals.")
        return redirect('challenges:challenge_detail', slug=partnership.challenge.slug)

    if action == 'approve':
        partnership.status = PartnershipStatus.APPROVED
        partnership.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Partnership with {partnership.organization.organization_name or partnership.organization.username} approved!")
    elif action == 'decline':
        partnership.status = PartnershipStatus.DECLINED
        partnership.save(update_fields=['status', 'updated_at'])
        messages.info(request, "Partnership request declined.")

    return redirect('challenges:challenge_detail', slug=partnership.challenge.slug)


@login_required
def sponsored_challenge_create_view(request, challenge_slug):
    """
    Sponsor a challenge with grant funds or prizes.
    """
    challenge = get_object_or_404(Challenge, slug=challenge_slug)

    if not request.user.is_organization and not request.user.is_administrator:
        messages.error(request, "Only organizations or sponsors can sponsor a challenge.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    if hasattr(challenge, 'sponsorship'):
        messages.info(request, "This challenge already has active sponsorship.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    if request.method == 'POST':
        form = SponsoredChallengeForm(request.POST)
        if form.is_valid():
            sponsorship = form.save(commit=False)
            sponsorship.challenge = challenge
            sponsorship.sponsor = request.user
            sponsorship.save()
            messages.success(request, f"Thank you! You are now the official sponsor of '{challenge.title}'.")
            return redirect('challenges:challenge_detail', slug=challenge.slug)
    else:
        form = SponsoredChallengeForm()

    return render(request, 'partnerships/sponsored_challenge_form.html', {
        'form': form,
        'challenge': challenge
    })
