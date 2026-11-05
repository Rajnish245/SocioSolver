import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeCategory
from ai_services.models import AIAnalysisLog
from ai_services.services import (
    AIChallengeAnalyzer, AISolutionGenerator,
    AISimilarChallengeFinder, AISmartTeamMatcher,
    AIServiceUnavailableError, AIRateLimitExceededError,
    AIValidationError, check_user_rate_limit
)

User = get_user_model()


class AIServicesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='aitester',
            email='aitester@example.com',
            password='Password123!',
            skills='Python, IoT, Water Engineering',
            interests='Water Conservation'
        )
        self.category = ChallengeCategory.objects.create(name='Water Tech', slug='water-tech')
        self.challenge = Challenge.objects.create(
            title='Dormitory Water Leakage',
            description='Mechanical float valves frequently fail causing thousands of liters to overflow every morning.',
            category=self.category,
            location='North Campus Quad',
            affected_community='1200 Students',
            creator=self.user
        )

    def test_input_validation_rejects_too_short(self):
        with self.assertRaises(AIValidationError):
            AIChallengeAnalyzer.analyze("Short", "Too short", self.user)

    @override_settings(MISTRAL_API_KEY='')
    def test_missing_api_key_raises_service_unavailable(self):
        with self.assertRaises(AIServiceUnavailableError):
            AIChallengeAnalyzer.analyze(self.challenge.title, self.challenge.description, self.user)

    @override_settings(AI_RATE_LIMIT_PER_USER_PER_HOUR=2)
    def test_rate_limiting_enforcement(self):
        # Create 2 logs within the hour
        AIAnalysisLog.objects.create(user=self.user, service_type='analyze_challenge', prompt_summary='test1')
        AIAnalysisLog.objects.create(user=self.user, service_type='analyze_challenge', prompt_summary='test2')

        with self.assertRaises(AIRateLimitExceededError):
            check_user_rate_limit(self.user)

    @override_settings(MISTRAL_API_KEY='mstrl-mock-valid-key-for-testing')
    @patch('ai_services.services.get_mistral_client')
    def test_ai_challenge_analyzer_mocked_success(self, mock_client_factory):
        # Setup mock Mistral client
        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client

        mock_payload = {
            "suggested_category": "Water Conservation",
            "potential_root_causes": ["Faulty float valve", "Excessive water pressure"],
            "affected_stakeholders": ["Dormitory students", "Maintenance staff"],
            "suggested_priority": "high",
            "priority_explanation": "Continuous potable water loss and infrastructure risk.",
            "missing_information": ["Inlet pipe diameter"],
            "disclaimer": "AI-generated recommendation; human review required."
        }

        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(mock_payload)
        mock_completion.choices = [mock_choice]
        mock_completion.usage.total_tokens = 350
        mock_client.chat.complete.return_value = mock_completion

        result = AIChallengeAnalyzer.analyze(
            self.challenge.title, self.challenge.description, self.user, challenge=self.challenge
        )

        self.assertIn('data', result)
        self.assertEqual(result['data']['suggested_category'], "Water Conservation")
        self.assertEqual(result['data']['suggested_priority'], "high")
        self.assertEqual(len(result['data']['potential_root_causes']), 2)

        # Verify cached on model
        self.challenge.refresh_from_db()
        self.assertIsNotNone(self.challenge.ai_analysis_cache)

        # Verify logged in database
        self.assertTrue(AIAnalysisLog.objects.filter(user=self.user, challenge=self.challenge).exists())

    @override_settings(MISTRAL_API_KEY='mstrl-mock-valid-key-for-testing')
    @patch('ai_services.services.get_mistral_client')
    def test_ai_solution_generator_mocked_success(self, mock_client_factory):
        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client

        mock_solutions = {
            "solutions": [
                {
                    "id": i,
                    "title": f"Practical Solution {i}",
                    "summary": f"Summary for solution {i}",
                    "implementation_steps": ["Step 1", "Step 2"],
                    "required_skills_and_resources": ["Plumbing", "IoT"],
                    "potential_risks_and_limitations": ["Initial cost"],
                    "possible_collaborators": ["Engineering students"],
                    "suggested_impact_metrics": ["Gallons saved"]
                }
                for i in range(1, 6)
            ],
            "disclaimer": "Verify with local engineers."
        }

        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(mock_solutions)
        mock_completion.choices = [mock_choice]
        mock_completion.usage.total_tokens = 850
        mock_client.chat.complete.return_value = mock_completion

        result = AISolutionGenerator.generate(
            self.challenge.title, self.challenge.description, self.category.name, self.user, challenge=self.challenge
        )

        self.assertEqual(len(result['data']['solutions']), 5)
        self.challenge.refresh_from_db()
        self.assertIsNotNone(self.challenge.ai_solutions_cache)

    @override_settings(MISTRAL_API_KEY='')
    def test_similar_challenge_finder_keyword_fallback(self):
        # Create a second challenge
        c2 = Challenge.objects.create(
            title='River Water Pollution',
            description='Agricultural runoff contaminating drinking water supply.',
            category=self.category,
            location='River Valley',
            affected_community='Local farmers',
            creator=self.user
        )

        result = AISimilarChallengeFinder.find_similar(self.challenge)
        self.assertEqual(result['method'], 'Database Keyword Fallback')
        self.assertTrue(len(result['results']) >= 1)

    def test_smart_team_matching_collaborators(self):
        # Create prospective collaborator
        collaborator = User.objects.create_user(
            username='sensor_expert',
            email='sensor@example.edu',
            password='Password123!',
            skills='IoT Sensors, Water Engineering, Python',
            interests='Clean Water, Microgrids'
        )

        match_result = AISmartTeamMatcher.match_collaborators(self.challenge, self.user)
        self.assertTrue(len(match_result['recommendations']) >= 1)
        top_rec = match_result['recommendations'][0]
        self.assertEqual(top_rec['user'], collaborator)
        self.assertTrue(top_rec['score'] >= 50)
        self.assertIn("water", top_rec['reason'].lower())
