from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeCategory
from solutions.models import SolutionProposal, SolutionVote, DiscussionComment

User = get_user_model()


class SolutionProposalsAndVotingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username='author1', email='author1@example.com', password='Password123!')
        self.voter = User.objects.create_user(username='voter1', email='voter1@example.com', password='Password123!')
        
        self.category = ChallengeCategory.objects.create(name='Environment', slug='environment')
        self.challenge = Challenge.objects.create(
            title='Park Litter Issue',
            description='Excessive litter in the central community park needs clean bins.',
            category=self.category,
            location='Central Park',
            affected_community='Park Visitors',
            creator=self.author
        )
        self.proposal = SolutionProposal.objects.create(
            challenge=self.challenge,
            author=self.author,
            title='Smart Solar Compacting Bins',
            summary='Install solar powered waste compactors.',
            detailed_plan='Phase 1: Procurement. Phase 2: Installation across park.',
            resources_needed='5 solar bins, waste service agreement.',
            estimated_timeline='4 weeks'
        )

    def test_authenticated_user_can_propose_solution(self):
        self.client.login(username='voter1', password='Password123!')
        response = self.client.post(reverse('solutions:proposal_create', kwargs={'challenge_slug': self.challenge.slug}), {
            'title': 'Volunteer Clean Up Saturdays',
            'summary': 'Weekly community student cleanups.',
            'detailed_plan': 'Organize volunteer groups every Saturday with grabbers and gloves.',
            'resources_needed': 'Gloves, trash bags, refreshments.',
            'estimated_timeline': 'Ongoing',
            'estimated_budget': '$50/week'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SolutionProposal.objects.filter(title='Volunteer Clean Up Saturdays').exists())

    def test_single_upvote_enforcement_and_toggle(self):
        self.client.login(username='voter1', password='Password123!')
        vote_url = reverse('solutions:toggle_vote', kwargs={'pk': self.proposal.pk})

        # 1. First vote -> Upvoted
        res1 = self.client.post(vote_url)
        self.assertEqual(res1.status_code, 302)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.upvotes_count, 1)
        self.assertEqual(SolutionVote.objects.filter(proposal=self.proposal, user=self.voter).count(), 1)

        # 2. Second vote by same user -> Toggles off (No duplicate vote!)
        res2 = self.client.post(vote_url)
        self.assertEqual(res2.status_code, 302)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.upvotes_count, 0)
        self.assertEqual(SolutionVote.objects.filter(proposal=self.proposal, user=self.voter).count(), 0)

    def test_comment_submission(self):
        self.client.login(username='voter1', password='Password123!')
        response = self.client.post(reverse('solutions:add_comment'), {
            'proposal_id': self.proposal.pk,
            'content': 'Great initiative! We can donate the first 2 compactors.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DiscussionComment.objects.filter(proposal=self.proposal, author=self.voter).exists())
