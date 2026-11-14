from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User

PASSWORD_HELP = (
    "At least 8 characters. Cannot be entirely numeric or a commonly used password."
)


def _shared_widgets():
    return {
        'first_name': forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'First Name', 'required': True,
            'autocomplete': 'given-name',
        }),
        'last_name': forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Last Name', 'required': True,
            'autocomplete': 'family-name',
        }),
        'email': forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': 'name@example.com',
            'required': True, 'autocomplete': 'email',
        }),
        'phone': forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': '10-digit mobile number',
            'required': True, 'autocomplete': 'tel', 'maxlength': 10,
        }),
    }


class PasswordValidatedMixin:
    """Runs Django's configured AUTH_PASSWORD_VALIDATORS on the password."""

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return password
        try:
            validate_password(password)
        except ValidationError as exc:
            raise forms.ValidationError(list(exc.messages))
        return password

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(digits) == 12 and digits.startswith('91'):
            digits = digits[2:]
        elif len(digits) == 11 and digits.startswith('0'):
            digits = digits[1:]
        if len(digits) != 10:
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number.")
        if User.objects.filter(phone=digits).exists():
            raise forms.ValidationError("An account with this mobile number already exists.")
        return digits

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        from django.db.models import Q
        if User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class CustomerRegistrationForm(PasswordValidatedMixin, forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Create a secure password',
            'autocomplete': 'new-password',
        }),
        label="Password",
        min_length=8,
        help_text=PASSWORD_HELP,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        }),
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']
        widgets = _shared_widgets()

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'CUSTOMER'
        email = self.cleaned_data['email'].strip().lower()
        user.email = email
        user.username = email
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ProviderRegistrationForm(PasswordValidatedMixin, forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Create password',
            'autocomplete': 'new-password',
        }),
        label="Password",
        min_length=8,
        help_text=PASSWORD_HELP,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        }),
        label="Confirm Password",
    )
    business_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Trading / business name (optional)',
        }),
    )
    experience_years = forms.IntegerField(
        initial=2, min_value=0, max_value=50,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    service_pincodes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'e.g. 411038, 411045, 411057',
        }),
        help_text="Comma-separated 6-digit postal codes you cover.",
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']
        widgets = _shared_widgets()

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")

        pincodes = (cleaned.get('service_pincodes') or '').strip()
        if pincodes:
            parts = [p.strip() for p in pincodes.replace(';', ',').split(',') if p.strip()]
            bad = [p for p in parts if not (p.isdigit() and len(p) == 6)]
            if bad:
                self.add_error(
                    'service_pincodes',
                    f"Invalid postal code(s): {', '.join(bad)}. Use 6 digits each.",
                )
            else:
                cleaned['service_pincodes'] = ', '.join(parts)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'PROVIDER'
        email = self.cleaned_data['email'].strip().lower()
        user.email = email
        user.username = email
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Email or username (e.g. admin or rahul.sharma@example.com)',
            'autofocus': True, 'autocomplete': 'username',
        }),
        label="Email or Username",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        }),
        label="Password",
    )


class UserPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current password'}),
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'}),
        label="New Password",
        min_length=8,
        help_text=PASSWORD_HELP
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        label="Confirm New Password"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Current password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "New passwords do not match.")

        if new_password:
            try:
                validate_password(new_password, self.user)
            except ValidationError as exc:
                self.add_error('new_password', list(exc.messages))

        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()
        return self.user

