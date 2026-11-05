from django import forms
from .models import ImpactReport


class ImpactReportForm(forms.ModelForm):
    class Meta:
        model = ImpactReport
        fields = [
            'title', 'summary', 'beneficiaries_reached',
            'environmental_impact', 'social_impact',
            'challenges_overcome', 'future_sustainability_plan'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Campus Greywater Recycling System Phase 1 Outcomes'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Summary of project deliverables and measurable outcomes achieved.'
            }),
            'beneficiaries_reached': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1200'
            }),
            'environmental_impact': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., 50,000 gallons of potable water conserved per academic semester.'
            }),
            'social_impact': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Raised student awareness, engaged 25 volunteers in workshops.'
            }),
            'challenges_overcome': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Key obstacles encountered during implementation and how they were resolved.'
            }),
            'future_sustainability_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ongoing maintenance plan, funding, or institutional handover.'
            }),
        }
