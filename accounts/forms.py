from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserRole

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a secure password'}),
        min_length=8,
        help_text="Minimum 8 characters."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        help_text="Re-enter the password to confirm."
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'organization_name', 'skills', 'interests', 'location'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.org'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institution / University / Company / NGO'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, Water Purification, Data Analysis'}),
            'interests': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Clean Water, Solar Power, Education Access'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Boston, MA or Nairobi, Kenya'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'role', 'organization_name', 'bio',
            'skills', 'interests', 'location',
            'phone', 'website', 'avatar'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated skills'}),
            'interests': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated societal domains'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
