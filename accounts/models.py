from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    CITIZEN = 'citizen', 'Citizen'
    STUDENT = 'student', 'Student'
    UNIVERSITY = 'university', 'University Representative'
    COMPANY = 'company', 'Company Representative'
    NGO = 'ngo', 'NGO Representative'
    ADMINISTRATOR = 'administrator', 'Administrator'


class User(AbstractUser):
    """
    Custom User model for SocioSolve supporting distinct societal roles,
    profile details, skills, and organizational affiliations.
    """
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CITIZEN,
        help_text="Role determining platform permissions and collaboration capabilities."
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Affiliated institution, university, NGO, or company."
    )
    bio = models.TextField(
        blank=True,
        help_text="Short professional summary or background."
    )
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated skills (e.g., Python, Water Purification, Project Management, Public Health)."
    )
    interests = models.TextField(
        blank=True,
        help_text="Comma-separated societal problem domains (e.g., Clean Water, Waste Recycling, Renewable Energy)."
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="City, region, or campus."
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Profile photo or organization logo."
    )
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True, help_text="Personal, portfolio, or organization website.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        full_name = self.get_full_name()
        display = full_name if full_name else self.username
        if self.organization_name:
            return f"{display} ({self.organization_name} - {self.get_role_display()})"
        return f"{display} ({self.get_role_display()})"

    @property
    def is_citizen(self):
        return self.role == UserRole.CITIZEN

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT

    @property
    def is_university(self):
        return self.role == UserRole.UNIVERSITY

    @property
    def is_company(self):
        return self.role == UserRole.COMPANY

    @property
    def is_ngo(self):
        return self.role == UserRole.NGO

    @property
    def is_administrator(self):
        return self.role == UserRole.ADMINISTRATOR or self.is_superuser or self.is_staff

    @property
    def is_organization(self):
        return self.role in [UserRole.UNIVERSITY, UserRole.COMPANY, UserRole.NGO]

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def get_interests_list(self):
        if not self.interests:
            return []
        return [i.strip() for i in self.interests.split(',') if i.strip()]
