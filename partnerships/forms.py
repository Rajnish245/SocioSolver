from django import forms
from .models import OrganizationProfile, PartnershipRequest, SponsoredChallenge


class OrganizationProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizationProfile
        fields = [
            'org_type', 'official_name', 'headquarters',
            'established_year', 'mission_statement',
            'focus_areas', 'resources_available', 'website'
        ]
        widgets = {
            'org_type': forms.Select(attrs={'class': 'form-select'}),
            'official_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full registered name'}),
            'headquarters': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cambridge, MA'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1995'}),
            'mission_statement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'focus_areas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Clean Water, Solar Microgrids, STEM'}),
            'resources_available': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List grants, lab equipment, mentors, or internship stipends'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://institution.org'}),
        }


class PartnershipRequestForm(forms.ModelForm):
    class Meta:
        model = PartnershipRequest
        fields = ['offered_support', 'message']
        widgets = {
            'offered_support': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $5,000 Seed Grant + 2 Faculty Mentors'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Outline your organization\'s collaboration objectives and expectations...'
            }),
        }


class SponsoredChallengeForm(forms.ModelForm):
    class Meta:
        model = SponsoredChallenge
        fields = ['grant_amount', 'currency', 'benefits', 'application_deadline']
        widgets = {
            'grant_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Prizes, mentoring, corporate recruitment'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
