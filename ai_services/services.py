import json
import logging
from datetime import timedelta
import numpy as np
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import AIAnalysisLog, AIServiceType

logger = logging.getLogger(__name__)
User = get_user_model()


class AIServiceError(Exception):
    """Base exception for SocioSolve AI service errors."""
    pass


class AIServiceUnavailableError(AIServiceError):
    """Raised when the Mistral API key is missing or the external API cannot be reached."""
    pass


class AIRateLimitExceededError(AIServiceError):
    """Raised when a user exceeds the hourly AI request quota."""
    pass


class AIValidationError(AIServiceError):
    """Raised when inputs do not meet length or format requirements."""
    pass


def get_mistral_client():
    """
    Initializes and returns the Mistral client using environment variables.
    Raises AIServiceUnavailableError if the key is not set.
    """
    api_key = getattr(settings, 'MISTRAL_API_KEY', '').strip()
    if not api_key:
        raise AIServiceUnavailableError(
            "The Mistral API key is not configured. Please set MISTRAL_API_KEY in your .env file to activate AI features."
        )

    try:
        from mistralai.client import Mistral
        return Mistral(api_key=api_key)
    except Exception as exc:
        logger.error(f"Failed to initialize Mistral client: {exc}")
        raise AIServiceUnavailableError(f"Could not connect to Mistral service: {str(exc)}")


def check_user_rate_limit(user):
    """
    Enforces per-user hourly quota to prevent abuse and excessive API spending.
    """
    if user.is_superuser:
        return True

    hourly_limit = getattr(settings, 'AI_RATE_LIMIT_PER_USER_PER_HOUR', 15)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_requests_count = AIAnalysisLog.objects.filter(
        user=user,
        created_at__gte=one_hour_ago
    ).count()

    if recent_requests_count >= hourly_limit:
        raise AIRateLimitExceededError(
            f"You have reached the limit of {hourly_limit} AI requests per hour. Please wait a few minutes before trying again."
        )
    return True


def validate_challenge_input(title, description):
    """
    Validates input length and rejects empty submissions.
    """
    combined = f"{title.strip()} {description.strip()}".strip()
    if len(combined) < 20:
        raise AIValidationError("Input is too short. Please provide at least 20 characters describing the problem.")
    if len(combined) > 6000:
        raise AIValidationError("Input exceeds maximum allowed length of 6,000 characters.")


class AIChallengeAnalyzer:
    """
    Feature A: Evaluates societal challenges and returns structured analysis:
    suggested category, root causes, stakeholders, priority with rationale, and missing details.
    """
    @staticmethod
    def analyze(title, description, user, challenge=None, force_refresh=False):
        # 1. Check existing cache to reduce repeated API calls
        if challenge and challenge.ai_analysis_cache and not force_refresh:
            return {
                'data': challenge.ai_analysis_cache,
                'cached': True,
                'model_used': 'cached'
            }

        # 2. Authentication and rate limit check
        check_user_rate_limit(user)
        validate_challenge_input(title, description)

        # 3. Call Mistral API
        client = get_mistral_client()
        model_name = getattr(settings, 'MISTRAL_MODEL', 'mistral-small-latest')

        system_prompt = (
            "You are an expert societal problem analyst for SocioSolve. "
            "Analyze the submitted community challenge objectively. "
            "IMPORTANT: Priority is a recommendation, not a verified fact. "
            "Do not invent statistics or claim unconfirmed facts. "
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "suggested_category": "string (e.g., Water Conservation, Healthcare, Environment)",\n'
            '  "potential_root_causes": ["list of 3-5 plausible root causes"],\n'
            '  "affected_stakeholders": ["list of 3-5 distinct groups affected"],\n'
            '  "suggested_priority": "low" | "medium" | "high" | "critical",\n'
            '  "priority_explanation": "objective rationale explaining why this priority level was suggested",\n'
            '  "missing_information": ["list of specific questions or data points that would clarify the challenge"],\n'
            '  "disclaimer": "AI-generated recommendation. Requires local human review and verification."\n'
            "}"
        )

        user_content = f"Title: {title}\nDescription: {description}"

        try:
            from mistralai.client.models import ResponseFormat

            response = client.chat.complete(
                model=model_name,
                response_format=ResponseFormat(type='json_object'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            raw_text = response.choices[0].message.content
            parsed_data = json.loads(raw_text)
            tokens_used = response.usage.total_tokens if response.usage else 0

            # 4. Cache in challenge model if attached
            if challenge:
                challenge.ai_analysis_cache = parsed_data
                challenge.save(update_fields=['ai_analysis_cache'])

            # 5. Log request
            AIAnalysisLog.objects.create(
                user=user,
                challenge=challenge,
                service_type=AIServiceType.ANALYZE_CHALLENGE,
                prompt_summary=f"Analysis of: {title[:80]}",
                response_json=parsed_data,
                model_used=model_name,
                tokens_used=tokens_used,
                success=True
            )

            return {
                'data': parsed_data,
                'cached': False,
                'model_used': model_name
            }

        except Exception as exc:
            logger.error(f"Mistral Analysis error: {exc}")
            AIAnalysisLog.objects.create(
                user=user,
                challenge=challenge,
                service_type=AIServiceType.ANALYZE_CHALLENGE,
                prompt_summary=f"Failed analysis of: {title[:80]}",
                success=False,
                error_message=str(exc)
            )
            raise AIServiceError(f"AI Analysis could not be completed: {str(exc)}")


class AISolutionGenerator:
    """
    Feature B: Generates 5 practical, structured solution ideas with implementation steps,
    required resources, potential risks, collaborators, and impact metrics.
    """
    @staticmethod
    def generate(title, description, category_name, user, challenge=None, force_refresh=False):
        if challenge and challenge.ai_solutions_cache and not force_refresh:
            return {
                'data': challenge.ai_solutions_cache,
                'cached': True,
                'model_used': 'cached'
            }

        check_user_rate_limit(user)
        validate_challenge_input(title, description)

        client = get_mistral_client()
        model_name = getattr(settings, 'MISTRAL_MODEL', 'mistral-small-latest')

        system_prompt = (
            "You are a collaborative social innovation consultant for SocioSolve. "
            "Generate exactly 5 diverse, highly practical, community-actionable solution ideas "
            "for the presented societal problem. "
            "Do not make exaggerated claims. "
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "solutions": [\n'
            "    {\n"
            '      "id": 1,\n'
            '      "title": "Concise solution name",\n'
            '      "summary": "Brief 2-3 sentence overview",\n'
            '      "implementation_steps": ["Step 1...", "Step 2...", "Step 3...", "Step 4..."],\n'
            '      "required_skills_and_resources": ["Key skill 1", "Equipment 2", "Resource 3"],\n'
            '      "potential_risks_and_limitations": ["Risk 1", "Limitation 2"],\n'
            '      "possible_collaborators": ["e.g. Engineering students", "Local municipality", "Environmental NGO"],\n'
            '      "suggested_impact_metrics": ["Metric 1 (e.g. Gallons saved)", "Metric 2 (e.g. Participants engaged)"]\n'
            "    }\n"
            "  ],\n"
            '  "disclaimer": "AI-generated ideas provide initial brainstorming. Feasibility must be verified by local project teams."\n'
            "}"
        )

        user_content = f"Category: {category_name}\nChallenge Title: {title}\nDescription: {description}"

        try:
            from mistralai.client.models import ResponseFormat

            response = client.chat.complete(
                model=model_name,
                response_format=ResponseFormat(type='json_object'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.5,
                max_tokens=2200
            )

            raw_text = response.choices[0].message.content
            parsed_data = json.loads(raw_text)
            tokens_used = response.usage.total_tokens if response.usage else 0

            if challenge:
                challenge.ai_solutions_cache = parsed_data
                challenge.save(update_fields=['ai_solutions_cache'])

            AIAnalysisLog.objects.create(
                user=user,
                challenge=challenge,
                service_type=AIServiceType.GENERATE_SOLUTIONS,
                prompt_summary=f"Solutions for: {title[:80]}",
                response_json=parsed_data,
                model_used=model_name,
                tokens_used=tokens_used,
                success=True
            )

            return {
                'data': parsed_data,
                'cached': False,
                'model_used': model_name
            }

        except Exception as exc:
            logger.error(f"Mistral Solution Generation error: {exc}")
            AIAnalysisLog.objects.create(
                user=user,
                challenge=challenge,
                service_type=AIServiceType.GENERATE_SOLUTIONS,
                prompt_summary=f"Failed solution gen: {title[:80]}",
                success=False,
                error_message=str(exc)
            )
            raise AIServiceError(f"AI Solution generation failed: {str(exc)}")


class AISimilarChallengeFinder:
    """
    Feature C: Finds related challenges.
    Uses Mistral vector embeddings with cosine similarity when API key is active.
    Gracefully falls back to database text matching when Mistral is not configured.
    Explicitly reports the method used.
    """
    @staticmethod
    def get_embedding(text, client=None):
        if not client:
            client = get_mistral_client()
        embed_model = getattr(settings, 'MISTRAL_EMBEDDING_MODEL', 'mistral-embed')
        response = client.embeddings.create(
            model=embed_model,
            inputs=[text[:2000]]
        )
        return response.data[0].embedding

    @classmethod
    def find_similar(cls, challenge, limit=4):
        from challenges.models import Challenge

        other_challenges = Challenge.objects.filter(
            moderation_status='approved'
        ).exclude(pk=challenge.pk).select_related('category')

        if not other_challenges.exists():
            return {
                'results': [],
                'method': 'none',
                'explanation': 'No other challenges currently exist in the database to compare against.'
            }

        # Try semantic search if API key is present
        api_key = getattr(settings, 'MISTRAL_API_KEY', '').strip()
        if api_key:
            try:
                client = get_mistral_client()
                # Compute or retrieve target embedding
                target_vector = challenge.embedding
                if not target_vector:
                    target_text = f"{challenge.title}. {challenge.description[:500]}"
                    target_vector = cls.get_embedding(target_text, client)
                    challenge.embedding = target_vector
                    challenge.save(update_fields=['embedding'])

                target_arr = np.array(target_vector, dtype=np.float32)
                target_norm = np.linalg.norm(target_arr)

                scored_challenges = []
                for other in other_challenges:
                    other_vector = other.embedding
                    if not other_vector:
                        other_text = f"{other.title}. {other.description[:500]}"
                        try:
                            other_vector = cls.get_embedding(other_text, client)
                            other.embedding = other_vector
                            other.save(update_fields=['embedding'])
                        except Exception:
                            continue

                    other_arr = np.array(other_vector, dtype=np.float32)
                    other_norm = np.linalg.norm(other_arr)

                    if target_norm > 0 and other_norm > 0:
                        sim = float(np.dot(target_arr, other_arr) / (target_norm * other_norm))
                        similarity_percent = max(0, min(100, int(sim * 100)))
                        scored_challenges.append((other, similarity_percent))

                scored_challenges.sort(key=lambda x: x[1], reverse=True)
                top_results = [
                    {'challenge': item[0], 'similarity_percent': item[1]}
                    for item in scored_challenges[:limit]
                ]

                return {
                    'results': top_results,
                    'method': 'AI Semantic Embeddings',
                    'explanation': 'Calculated via high-dimensional cosine similarity using Mistral mistral-embed.'
                }

            except Exception as exc:
                logger.warning(f"Semantic search encountered an error, falling back to keyword search: {exc}")

        # Fallback to Database Keyword Matching
        keywords = [word.lower() for word in challenge.title.split() if len(word) > 3]
        query = Q(category=challenge.category)

        for kw in keywords[:4]:
            query |= Q(title__icontains=kw) | Q(description__icontains=kw)

        fallback_qs = other_challenges.filter(query).distinct()[:limit]
        results = [
            {'challenge': item, 'similarity_percent': 65 if item.category == challenge.category else 45}
            for item in fallback_qs
        ]

        return {
            'results': results,
            'method': 'Database Keyword Fallback',
            'explanation': 'Mistral semantic search is currently unavailable or unconfigured. Showing matches based on category and keyword relevance.'
        }


class AISmartTeamMatcher:
    """
    Feature D: Recommends potential collaborators based on profile skills,
    interests, and challenge requirements. Explains why each person is recommended.
    Does NOT automatically enroll anyone.
    """
    @staticmethod
    def match_collaborators(challenge, user, limit=5):
        # 1. Fetch active candidates excluding the challenge creator
        candidates = User.objects.filter(is_active=True).exclude(pk=challenge.creator.pk)
        if not candidates.exists():
            return {
                'recommendations': [],
                'method': 'none',
                'explanation': 'No other registered collaborators found on the platform yet.'
            }

        # 2. Extract challenge terms
        challenge_text = f"{challenge.title} {challenge.category.name} {challenge.description}".lower()

        candidate_scores = []
        for cand in candidates:
            # Avoid sending private info: only name, role, organization, skills, interests
            cand_skills = [s.strip().lower() for s in cand.get_skills_list()]
            cand_interests = [i.strip().lower() for i in cand.get_interests_list()]

            score = 20  # Base score for platform engagement
            reasons = []

            # Check skills match
            matched_skills = [s for s in cand_skills if s and (s in challenge_text or any(w in challenge_text for w in s.split()))]
            if matched_skills:
                score += min(45, len(matched_skills) * 15)
                reasons.append(f"Relevant skills in {', '.join(matched_skills)}")

            # Check interests match
            matched_interests = [
                i for i in cand_interests
                if i and (
                    i in challenge_text
                    or any(len(w) >= 4 and w in challenge_text for w in i.split())
                    or any(len(w) >= 4 and w in i for w in challenge.category.name.lower().split())
                )
            ]
            if matched_interests:
                score += min(25, len(matched_interests) * 15)
                reasons.append(f"Shared domain interest in {', '.join(matched_interests)}")

            # Role contextual bonus
            if cand.is_university and 'research' in challenge_text:
                score += 10
                reasons.append("Academic institution capable of research and lab support")
            elif cand.is_company:
                score += 10
                reasons.append("Corporate partner potential for resources and funding")
            elif cand.is_student:
                score += 10
                reasons.append("Motivated student eager to apply hands-on project skills")

            if not reasons:
                reasons.append("Active community contributor in societal problem solving")

            score = min(98, max(30, score))
            candidate_scores.append({
                'user': cand,
                'score': score,
                'reason': "; ".join(reasons),
                'role_suggestion': 'Technical Contributor' if cand_skills else 'Collaborator / Advisor'
            })

        candidate_scores.sort(key=lambda x: x['score'], reverse=True)
        return {
            'recommendations': candidate_scores[:limit],
            'method': 'Skills & Domain Affinity Matcher',
            'explanation': 'Recommendations are based on profile skills, declared interests, and organizational roles. Users must be invited and accept manually.'
        }
