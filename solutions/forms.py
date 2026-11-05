from django import forms
from .models import SolutionProposal, DiscussionComment


class SolutionProposalForm(forms.ModelForm):
    class Meta:
        model = SolutionProposal
        fields = [
            'title', 'summary', 'detailed_plan',
            'resources_needed', 'estimated_timeline', 'estimated_budget'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Campus Greywater Filtration & Subsurface Drip Irrigation'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Provide a concise overview of how this proposal solves the problem.'
            }),
            'detailed_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Phase 1: Survey campus piping. Phase 2: Install sand-carbon filter. Phase 3: Route to gardens.'
            }),
            'resources_needed': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Plumbing equipment, PVC pipes, sand/activated charcoal, 4 student volunteers.'
            }),
            'estimated_timeline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 4 weeks'
            }),
            'estimated_budget': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $350 or Volunteer-run'
            }),
        }

    def clean_detailed_plan(self):
        plan = self.cleaned_data.get('detailed_plan', '').strip()
        if len(plan) < 20:
            raise forms.ValidationError("Please provide more details on the implementation plan (at least 20 characters).")
        return plan


class DiscussionCommentForm(forms.ModelForm):
    class Meta:
        model = DiscussionComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your constructive insights, questions, or suggestions...'
            })
        }
