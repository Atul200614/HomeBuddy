from django import forms

from .models import Complaint

MAX_MB = 5


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'description', 'evidence_file']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'maxlength': 2000,
                'placeholder': 'What went wrong? Include times, names and anything the support team should know.',
            }),
            'evidence_file': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*,application/pdf',
            }),
        }
        labels = {'evidence_file': 'Photo or document evidence (optional)'}

    def clean_description(self):
        text = (self.cleaned_data.get('description') or '').strip()
        if len(text) < 20:
            raise forms.ValidationError(
                "Please describe the issue in at least 20 characters."
            )
        return text

    def clean_evidence_file(self):
        file = self.cleaned_data.get('evidence_file')
        if not file:
            return file
        if hasattr(file, 'size') and file.size > MAX_MB * 1024 * 1024:
            raise forms.ValidationError(f"Evidence files must be smaller than {MAX_MB} MB.")
        allowed = ('image/jpeg', 'image/png', 'image/webp', 'application/pdf')
        content_type = getattr(file, 'content_type', '')
        if content_type and content_type not in allowed:
            raise forms.ValidationError("Upload a JPG, PNG, WebP image or a PDF.")
        return file
