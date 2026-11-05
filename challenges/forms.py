from django import forms
from django.core.exceptions import ValidationError
from .models import Challenge, ChallengeReport, ChallengeCategory
from django.conf import settings
import os


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = [
            'title', 'category', 'location', 'affected_community',
            'priority', 'description', 'problem_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Severe Water Leakage and Wastage at North Campus Hostel'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., North Campus, Building B or Ward 4, Austin TX'
            }),
            'affected_community': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1,200 On-campus Resident Students & Staff'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the societal issue in detail. What is happening? When did it start? What are the consequences?'
            }),
            'problem_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 20:
            raise ValidationError("Please provide a more descriptive challenge summary (at least 20 characters).")
        if len(desc) > 5000:
            raise ValidationError("Challenge description exceeds the maximum length of 5000 characters.")
        return desc

    def clean_problem_image(self):
        image = self.cleaned_data.get('problem_image')
        if image:
            # Validate size (max 5MB)
            max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)
            if image.size > max_size:
                raise ValidationError("The image file size exceeds the 5MB limit.")
            
            # Validate extension
            ext = os.path.splitext(image.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            if ext not in allowed_extensions:
                raise ValidationError("Unsupported file format. Please upload JPG, PNG, WEBP, or GIF.")
        return image


class ChallengeReportForm(forms.ModelForm):
    class Meta:
        model = ChallengeReport
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please describe specifically what is inaccurate or inappropriate about this challenge.'
            }),
        }

    def clean_details(self):
        details = self.cleaned_data.get('details', '').strip()
        if len(details) < 10:
            raise ValidationError("Please provide at least 10 characters explaining the issue.")
        return details
