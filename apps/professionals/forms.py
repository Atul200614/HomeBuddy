from django import forms
from .models import ProviderProfile, VerificationDocument, ProviderSkill
from apps.accounts.models import User

class ProviderUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ProviderProfileEditForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = ['business_name', 'bio', 'experience_years', 'hourly_rate', 'service_city', 'service_pincodes', 'is_available_today']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'service_city': forms.TextInput(attrs={'class': 'form-control'}),
            'service_pincodes': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available_today': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class VerificationDocumentForm(forms.ModelForm):
    class Meta:
        model = VerificationDocument
        fields = ['document_type', 'document_file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}),
        }

class ProviderSkillForm(forms.ModelForm):
    class Meta:
        model = ProviderSkill
        fields = ['skill_name', 'years_experience']
        widgets = {
            'skill_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Electrical Wiring, Bathroom Plumbing, Sofa Shampooing'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control'}),
        }
