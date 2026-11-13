import datetime

from django import forms
from django.utils import timezone

from apps.customers.models import Address
from apps.professionals.models import ProviderProfile
from .models import Booking


class BookingCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user)
            self.fields['address'].empty_label = "Select a service address"
            default_addr = Address.objects.filter(user=user, is_default=True).first()
            if default_addr and not self.instance.pk:
                self.fields['address'].initial = default_addr

        if service:
            self.fields['provider'].queryset = ProviderProfile.objects.filter(
                is_verified=True, is_available_today=True
            ).select_related('user')
            self.fields['provider'].empty_label = (
                "Auto-assign the best certified technician for my area"
            )

        self.fields['scheduled_date'].widget.attrs.update({
            'min': timezone.localdate().isoformat(),
        })

    class Meta:
        model = Booking
        fields = [
            'address', 'provider', 'scheduled_date', 'time_slot',
            'is_emergency', 'special_instructions',
        ]
        widgets = {
            'address': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'provider': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'is_emergency': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 1000,
                'placeholder': 'Access instructions, specific issues, gate codes…',
            }),
        }

    def clean_scheduled_date(self):
        scheduled = self.cleaned_data.get('scheduled_date')
        if scheduled and scheduled < timezone.localdate():
            raise forms.ValidationError("Scheduled date cannot be in the past.")
        if scheduled and scheduled > timezone.localdate() + datetime.timedelta(days=90):
            raise forms.ValidationError("Bookings can be made up to 90 days ahead.")
        return scheduled

    def clean_special_instructions(self):
        notes = (self.cleaned_data.get('special_instructions') or '').strip()
        if len(notes) > 1000:
            raise forms.ValidationError("Please keep instructions under 1000 characters.")
        return notes
