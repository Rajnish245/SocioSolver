from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeCategory, ChallengeStatus, ChallengeReport

User = get_user_model()


class ChallengeManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(
            username='alice', email='alice@example.com', password='Password123!'
        )
        self.other_user = User.objects.create_user(
            username='bob', email='bob@example.com', password='Password123!'
        )
        self.category = ChallengeCategory.objects.create(
            name='Water Conservation',
            slug='water-conservation',
            description='Water issues'
        )
        self.challenge = Challenge.objects.create(
            title='Campus Water Leakage',
            description='Severe pipe leakage in dormitories wasting hundreds of gallons daily.',
            category=self.category,
            location='Campus Dorm Quad',
            affected_community='500 Students',
            creator=self.creator,
            status=ChallengeStatus.OPEN
        )

    def test_anonymous_cannot_create_challenge(self):
        response = self.client.get(reverse('challenges:challenge_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_authenticated_user_can_create_challenge(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('challenges:challenge_create'), {
            'title': 'Plastic Waste in Local Lake',
            'category': self.category.id,
            'location': 'City Park Lake',
            'affected_community': 'Local Park Visitors',
            'priority': 'high',
            'description': 'Plastic bottles floating along shoreline need cleanup and trash can infrastructure.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Challenge.objects.filter(title='Plastic Waste in Local Lake').exists())

    def test_creator_can_edit_challenge(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('challenges:challenge_update', kwargs={'slug': self.challenge.slug}), {
            'title': 'Campus Water Leakage - Updated',
            'category': self.category.id,
            'location': 'Campus Dorm Quad B',
            'affected_community': '600 Students',
            'priority': 'critical',
            'description': 'Severe pipe leakage in dormitories wasting hundreds of gallons daily.',
        })
        self.assertEqual(response.status_code, 302)
        self.challenge.refresh_from_db()
        self.assertEqual(self.challenge.title, 'Campus Water Leakage - Updated')

    def test_unauthorized_user_cannot_edit_challenge(self):
        self.client.login(username='bob', password='Password123!')
        response = self.client.post(reverse('challenges:challenge_update', kwargs={'slug': self.challenge.slug}), {
            'title': 'Hacked Title',
            'category': self.category.id,
            'location': 'Hacked Location',
            'affected_community': 'Hacked Community',
            'priority': 'low',
            'description': 'Hacked description with enough characters.',
        })
        self.challenge.refresh_from_db()
        self.assertNotEqual(self.challenge.title, 'Hacked Title')

    def test_challenge_moderation_reporting(self):
        self.client.login(username='bob', password='Password123!')
        response = self.client.post(reverse('challenges:challenge_report', kwargs={'slug': self.challenge.slug}), {
            'reason': 'spam',
            'details': 'This challenge contains commercial spam links.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChallengeReport.objects.filter(challenge=self.challenge, reported_by=self.other_user).exists())
        self.challenge.refresh_from_db()
        self.assertTrue(self.challenge.is_flagged)
