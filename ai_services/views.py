from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from challenges.models import Challenge
from .services import (
    AIChallengeAnalyzer, AISolutionGenerator,
    AISimilarChallengeFinder, AISmartTeamMatcher,
    AIServiceUnavailableError, AIRateLimitExceededError,
    AIValidationError, AIServiceError
)


@login_required
def analyze_challenge_view(request, challenge_id):
    """
    Trigger AI Challenge Analysis.
    Returns JSON for asynchronous modal display or redirects back with message.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    force_refresh = request.GET.get('refresh') == '1' or request.POST.get('refresh') == '1'

    try:
        result = AIChallengeAnalyzer.analyze(
            title=challenge.title,
            description=challenge.description,
            user=request.user,
            challenge=challenge,
            force_refresh=force_refresh
        )
        
        # If AJAX request, return JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({
                'success': True,
                'data': result['data'],
                'cached': result['cached'],
                'model': result['model_used']
            })

        messages.success(request, "AI Analysis completed! Review the strategic insights below.")
        return redirect('challenges:challenge_detail', slug=challenge.slug)

    except (AIServiceUnavailableError, AIRateLimitExceededError, AIValidationError, AIServiceError) as exc:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({'success': False, 'error': str(exc)}, status=400)
        messages.warning(request, str(exc))
        return redirect('challenges:challenge_detail', slug=challenge.slug)


@login_required
def generate_solutions_view(request, challenge_id):
    """
    Generate or display 5 AI structured solution roadmaps for a challenge.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    force_refresh = request.GET.get('refresh') == '1' or request.POST.get('refresh') == '1'
    error_message = None
    solutions_data = None
    is_cached = False

    try:
        result = AISolutionGenerator.generate(
            title=challenge.title,
            description=challenge.description,
            category_name=challenge.category.name,
            user=request.user,
            challenge=challenge,
            force_refresh=force_refresh
        )
        solutions_data = result['data']
        is_cached = result['cached']
    except (AIServiceUnavailableError, AIRateLimitExceededError, AIValidationError, AIServiceError) as exc:
        error_message = str(exc)

    context = {
        'challenge': challenge,
        'solutions_data': solutions_data,
        'is_cached': is_cached,
        'error_message': error_message,
    }
    return render(request, 'ai_services/solutions_view.html', context)


def similar_challenges_view(request, challenge_id):
    """
    Finds and displays similar societal challenges with explicit search mode.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    similarity_result = AISimilarChallengeFinder.find_similar(challenge)

    context = {
        'challenge': challenge,
        'similar_challenges': similarity_result['results'],
        'search_method': similarity_result['method'],
        'search_explanation': similarity_result['explanation'],
    }
    return render(request, 'ai_services/similar_challenges.html', context)


@login_required
def smart_team_matching_view(request, challenge_id):
    """
    Recommends prospective team collaborators for a challenge based on
    skills, interests, and profile roles.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    match_result = AISmartTeamMatcher.match_collaborators(challenge, request.user)

    context = {
        'challenge': challenge,
        'recommendations': match_result['recommendations'],
        'method': match_result['method'],
        'explanation': match_result['explanation'],
    }
    return render(request, 'ai_services/team_matching.html', context)
