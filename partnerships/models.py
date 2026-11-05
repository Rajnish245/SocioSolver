from django.db import models
from django.conf import settings
from challenges.models import Challenge
from collaboration.models import ProjectTeam


class OrganizationType(models.TextChoices):
    UNIVERSITY = 'university', 'University / Academic Institution'
    COMPANY = 'company', 'Private Enterprise / Corporation'
    NGO = 'ngo', 'Non-Governmental Organization (NGO)'
    RESEARCH = 'research', 'Research Institute'
    GOVERNMENT = 'government', 'Public Sector / Municipality'


class OrganizationProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_profile'
    )
    org_type = models.CharField(
        max_length=20,
        choices=OrganizationType.choices,
        default=OrganizationType.NGO
    )
    official_name = models.CharField(max_length=255)
    headquarters = models.CharField(max_length=255, blank=True)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    mission_statement = models.TextField(blank=True)
    focus_areas = models.TextField(
        help_text="Comma-separated focus domains (e.g., Sustainability, Water Tech, Youth Literacy)."
    )
    resources_available = models.TextField(
        help_text="Support offered: Funding, Mentorship, Cloud Credits, Lab Facilities, Student Internships."
    )
    website = models.URLField(blank=True)
    verified = models.BooleanField(
        default=False,
        help_text="Whether this institution has been verified by platform administrators."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.official_name} ({self.get_org_type_display()})"


class PartnershipStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Approval'
    APPROVED = 'approved', 'Approved & Active'
    DECLINED = 'declined', 'Declined'
    COMPLETED = 'completed', 'Completed'


class PartnershipRequest(models.Model):
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_partnerships'
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='partnership_requests'
    )
    team = models.ForeignKey(
        ProjectTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partnerships'
    )
    offered_support = models.CharField(
        max_length=255,
        help_text="E.g., $5,000 Micro-Grant, Technical Mentorship, Lab Equipment, 10 Student Volunteers."
    )
    message = models.TextField(
        help_text="Describe how your organization wants to collaborate on this challenge."
    )
    status = models.CharField(
        max_length=20,
        choices=PartnershipStatus.choices,
        default=PartnershipStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Partnership: {self.organization.organization_name or self.organization.username} -> {self.challenge.title}"


class SponsoredChallenge(models.Model):
    challenge = models.OneToOneField(
        Challenge,
        on_delete=models.CASCADE,
        related_name='sponsorship'
    )
    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sponsored_challenges'
    )
    grant_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Direct funding or grant awarded to implementers."
    )
    currency = models.CharField(max_length=10, default='USD')
    benefits = models.TextField(
        help_text="Perks, corporate mentorship, recruitment opportunities, or prizes."
    )
    application_deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sponsorship by {self.sponsor.username} for {self.challenge.title} ({self.currency} {self.grant_amount})"
