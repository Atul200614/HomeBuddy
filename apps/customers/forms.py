from django import forms
from .models import CustomerProfile, Address
from apps.accounts.models import User

class CustomerUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['emergency_contact_name', 'emergency_contact_phone', 'notes']
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g. Ring bell twice, gate passcode 1234'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['title', 'address_line1', 'address_line2', 'landmark', 'city', 'state', 'pincode', 'is_default']
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Flat/House No., Wing, Building Name'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Area / Locality (e.g. Kothrud, Baner, Wakad)'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Near City Hospital or Metro Station'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '411038'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
