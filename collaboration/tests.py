from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeCategory
from collaboration.models import ProjectTeam, TeamMembership, TeamRole, MembershipStatus, ProjectTask, ProjectMilestone

User = get_user_model()


class CollaborationAndTeamTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.lead = User.objects.create_user(username='teamlead', email='lead@example.com', password='Password123!')
        self.applicant = User.objects.create_user(username='applicant', email='app@example.com', password='Password123!')
        self.outsider = User.objects.create_user(username='outsider', email='out@example.com', password='Password123!')

        self.category = ChallengeCategory.objects.create(name='Education', slug='education')
        self.challenge = Challenge.objects.create(
            title='Rural School Computer Lab',
            description='Refurbishing obsolete computer hardware for rural middle schoolers.',
            category=self.category,
            location='Greenfield Valley',
            affected_community='300 Students',
            creator=self.lead
        )
        self.team = ProjectTeam.objects.create(
            challenge=self.challenge,
            name='Lab Innovators',
            description='Deploying open-source Linux on donated workstations.',
            created_by=self.lead
        )
        # Lead membership
        TeamMembership.objects.create(
            team=self.team,
            user=self.lead,
            role=TeamRole.LEAD,
            status=MembershipStatus.ACCEPTED
        )

    def test_team_creation_assigns_lead(self):
        self.assertTrue(self.team.is_lead(self.lead))
        self.assertTrue(self.team.is_member(self.lead))
        self.assertFalse(self.team.is_member(self.applicant))

    def test_team_membership_application_and_approval(self):
        # 1. Applicant requests to join
        self.client.login(username='applicant', password='Password123!')
        join_url = reverse('collaboration:team_join', kwargs={'pk': self.team.pk})
        res1 = self.client.post(join_url, {
            'role': TeamRole.CONTRIBUTOR,
            'join_message': 'I have experience installing Linux distributions.'
        })
        self.assertEqual(res1.status_code, 302)

        membership = TeamMembership.objects.get(team=self.team, user=self.applicant)
        self.assertEqual(membership.status, MembershipStatus.PENDING)
        self.assertFalse(self.team.is_member(self.applicant))

        # 2. Lead accepts applicant
        self.client.login(username='teamlead', password='Password123!')
        accept_url = reverse('collaboration:membership_action', kwargs={
            'pk': self.team.pk,
            'membership_id': membership.pk,
            'action': 'accept'
        })
        res2 = self.client.get(accept_url)
        self.assertEqual(res2.status_code, 302)

        membership.refresh_from_db()
        self.assertEqual(membership.status, MembershipStatus.ACCEPTED)
        self.assertTrue(self.team.is_member(self.applicant))

    def test_non_member_cannot_create_task(self):
        self.client.login(username='outsider', password='Password123!')
        task_url = reverse('collaboration:task_create', kwargs={'pk': self.team.pk})
        res = self.client.post(task_url, {
            'title': 'Unauthorized Task',
            'status': 'todo',
            'priority': 'low'
        })
        self.assertEqual(res.status_code, 302)
        self.assertFalse(ProjectTask.objects.filter(title='Unauthorized Task').exists())

    def test_accepted_member_can_create_task(self):
        self.client.login(username='teamlead', password='Password123!')
        task_url = reverse('collaboration:task_create', kwargs={'pk': self.team.pk})
        res = self.client.post(task_url, {
            'title': 'Order RAM Modules',
            'description': 'Procure DDR3 RAM sticks.',
            'status': 'todo',
            'priority': 'high'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(ProjectTask.objects.filter(title='Order RAM Modules').exists())

    def test_milestone_creation_and_toggle(self):
        self.client.login(username='teamlead', password='Password123!')
        milestone = ProjectMilestone.objects.create(
            team=self.team,
            title='First 10 PCs Assembled',
            target_date=timezone.now().date(),
            created_by=self.lead
        )
        self.assertFalse(milestone.is_completed)

        toggle_url = reverse('collaboration:milestone_toggle', kwargs={
            'pk': self.team.pk,
            'milestone_id': milestone.pk
        })
        res = self.client.post(toggle_url)
        self.assertEqual(res.status_code, 302)
        milestone.refresh_from_db()
        self.assertTrue(milestone.is_completed)
        self.assertIsNotNone(milestone.completed_date)
