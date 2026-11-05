from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeCategory, ChallengeStatus
from solutions.models import SolutionProposal
from collaboration.models import ProjectTeam, ProjectMilestone
from impact.models import ImpactReport

User = get_user_model()


class ImpactDashboardAndReportsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='Password123!'
        )
        self.user = User.objects.create_user(
            username='impactlead', email='lead@example.com', password='Password123!'
        )
        self.category = ChallengeCategory.objects.create(name='Water Tech', slug='water-tech')
        self.challenge = Challenge.objects.create(
            title='Clean Drinking Water Well',
            description='Constructing sand biofilters for clean well water.',
            category=self.category,
            location='Village East',
            affected_community='800 Villagers',
            creator=self.user,
            status=ChallengeStatus.RESOLVED
        )

    def test_database_backed_dashboard_metrics(self):
        # Create a verified report and a self-reported report
        ImpactReport.objects.create(
            challenge=self.challenge,
            reported_by=self.admin,
            title='Verified Water Quality Audit',
            summary='Water turbidity decreased by 98%.',
            beneficiaries_reached=500,
            is_verified=True
        )
        ImpactReport.objects.create(
            challenge=self.challenge,
            reported_by=self.user,
            title='Community Estimate',
            summary='Preliminary household feedback.',
            beneficiaries_reached=300,
            is_verified=False
        )

        response = self.client.get(reverse('impact:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stats']['total_challenges'], 1)
        self.assertEqual(response.context['stats']['resolved_challenges'], 1)
        self.assertEqual(response.context['stats']['verified_beneficiaries'], 500)
        self.assertEqual(response.context['stats']['estimated_beneficiaries'], 300)
        self.assertEqual(response.context['stats']['total_beneficiaries'], 800)

    def test_impact_report_creation_and_resolution(self):
        self.client.login(username='impactlead', password='Password123!')
        url = reverse('impact:report_create', kwargs={'challenge_slug': self.challenge.slug})
        response = self.client.post(url, {
            'title': 'Well Filter Project Completion',
            'summary': 'All biofilters successfully deployed and tested.',
            'beneficiaries_reached': 800,
            'environmental_impact': 'Eliminated boiling firewood emissions.',
            'social_impact': 'Decreased waterborne illness incidents.',
            'mark_resolved': '1',
        })
        self.assertEqual(response.status_code, 302)
        report = ImpactReport.objects.get(title='Well Filter Project Completion')
        self.assertEqual(report.beneficiaries_reached, 800)
        # Non-admin users submit self-reported entries until audited
        self.assertFalse(report.is_verified)
