from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserRole

User = get_user_model()


class AuthenticationAndAccountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststudent',
            email='student@example.edu',
            password='Password123!',
            role=UserRole.STUDENT,
            organization_name='State College',
            skills='Python, Data Analysis',
            interests='Clean Water, Education'
        )

    def test_custom_user_roles_and_properties(self):
        self.assertTrue(self.user.is_student)
        self.assertFalse(self.user.is_university)
        self.assertFalse(self.user.is_company)
        self.assertFalse(self.user.is_administrator)
        self.assertEqual(self.user.get_skills_list(), ['Python', 'Data Analysis'])
        self.assertEqual(self.user.get_interests_list(), ['Clean Water', 'Education'])

    def test_user_registration_success(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newcitizen',
            'email': 'citizen@example.org',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'role': UserRole.CITIZEN,
            'organization_name': 'Austin Action',
            'location': 'Austin, TX',
            'skills': 'Community Organizing',
            'interests': 'Public Safety',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newcitizen').exists())
        new_user = User.objects.get(username='newcitizen')
        self.assertEqual(new_user.role, UserRole.CITIZEN)

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword456!',
            'role': UserRole.CITIZEN,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())

    def test_user_login_and_logout(self):
        login_res = self.client.post(reverse('accounts:login'), {
            'username': 'teststudent',
            'password': 'Password123!',
        })
        self.assertEqual(login_res.status_code, 302)

        logout_res = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_res.status_code, 302)

    def test_anonymous_access_restrictions(self):
        # Protected dashboard requires login
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

        # Protected profile edit requires login
        response_edit = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response_edit.status_code, 302)
        self.assertIn(reverse('accounts:login'), response_edit.url)
