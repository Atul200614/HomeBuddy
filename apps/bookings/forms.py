import datetime

from django import forms
from django.utils import timezone

from apps.customers.models import Address
from apps.professionals.models import ProviderProfile
from .models import Booking


class BookingCreationForm(forms.ModelForm):
    # Customer Details (Inline on Step 2)
    customer_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Customer Full Name',
            'autocomplete': 'name',
        }),
        label="Customer Name",
    )
    customer_phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit mobile number',
            'autocomplete': 'tel',
            'maxlength': '10',
        }),
        label="Mobile Number",
    )

    # Inline Delivery Address Fields (Step 2)
    address_title = forms.ChoiceField(
        choices=[('Home', 'Home'), ('Office', 'Office'), ('Other', 'Other')],
        initial='Home',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Address Type",
    )
    house_flat_no = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Flat/House No., Wing, Building Name',
        }),
        label="House / Flat / Building",
    )
    street = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street, Wing, or Landmark (e.g. Near Metro Station)',
        }),
        label="Street / Landmark",
    )
    area = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Area / Locality (e.g. Kothrud, Baner, Wakad, Viman Nagar)',
        }),
        label="Area / Locality",
    )
    city = forms.CharField(
        max_length=100,
        initial='Pune',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pune',
        }),
        label="City",
    )
    state = forms.CharField(
        max_length=100,
        initial='Maharashtra',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maharashtra',
        }),
        label="State",
    )
    pincode = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '6-digit PIN code (e.g. 411038)',
            'maxlength': '6',
        }),
        label="PIN Code",
    )
    save_as_default = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Save as primary address for future bookings",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields['address'].queryset = Address.objects.filter(user=user)
            self.fields['address'].empty_label = "Select a saved address (or enter new address below)"
            default_addr = Address.objects.filter(user=user, is_default=True).first()
            if default_addr and not self.instance.pk:
                self.fields['address'].initial = default_addr

            full_name = user.get_full_name() or user.username
            if full_name and not self.initial.get('customer_name'):
                self.initial['customer_name'] = full_name
            if user.phone and not self.initial.get('customer_phone'):
                self.initial['customer_phone'] = user.phone
        else:
            self.fields['address'].queryset = Address.objects.none()
            self.fields['address'].empty_label = "Enter new delivery address below"

        # Address is optional in the model form because customer can supply inline address
        self.fields['address'].required = False

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
            'address': forms.Select(attrs={'class': 'form-select'}),
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

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')

        # If a saved address is not selected, validate the inline new address fields
        if not address:
            house = (cleaned_data.get('house_flat_no') or '').strip()
            area = (cleaned_data.get('area') or '').strip()
            city = (cleaned_data.get('city') or '').strip()
            pincode = (cleaned_data.get('pincode') or '').strip()
            phone = (cleaned_data.get('customer_phone') or '').strip()

            pin_digits = ''.join(ch for ch in pincode if ch.isdigit())
            phone_digits = ''.join(ch for ch in phone if ch.isdigit())

            if not house:
                self.add_error('house_flat_no', "Please enter house/flat/building number.")
            if not area:
                self.add_error('area', "Please enter area or locality in Pune.")
            if not city:
                self.add_error('city', "Please enter city.")
            if not pincode or len(pin_digits) != 6:
                self.add_error('pincode', "Please enter a valid 6-digit postal PIN code.")
            if not phone:
                self.add_error('customer_phone', "Please enter a 10-digit mobile number for appointment updates.")
            elif len(phone_digits) != 10:
                self.add_error('customer_phone', "Please enter a valid 10-digit Indian mobile number.")

        return cleaned_data
