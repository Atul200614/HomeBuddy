from django import forms
from .models import Service, Category

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'category', 'name', 'pricing_type', 'base_price',
            'estimated_duration_minutes', 'is_emergency_eligible',
            'emergency_surcharge', 'short_description', 'detailed_description',
            'is_active'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sofa Foam Cleaning'}),
            'pricing_type': forms.Select(attrs={'class': 'form-select'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_emergency_eligible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'emergency_surcharge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short summary for cards'}),
            'detailed_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon_name', 'description', 'display_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bi-wrench'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
