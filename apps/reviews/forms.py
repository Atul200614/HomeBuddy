from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator

from .models import Review

RATING_CHOICES = [
    (5, '5 Stars — Outstanding service'),
    (4, '4 Stars — Very good'),
    (3, '3 Stars — Average'),
    (2, '2 Stars — Below expectations'),
    (1, '1 Star — Poor service'),
]


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
        label="Your rating",
    )

    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 1000,
                'placeholder': 'Punctuality, cleanliness, quality of work…',
            }),
        }
        labels = {'review_text': 'Your review'}

    def clean_review_text(self):
        text = (self.cleaned_data.get('review_text') or '').strip()
        if len(text) < 15:
            raise forms.ValidationError(
                "Please write at least 15 characters so the feedback is useful."
            )
        if len(text) > 1000:
            raise forms.ValidationError("Reviews are limited to 1000 characters.")
        return text

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating not in (1, 2, 3, 4, 5):
            raise forms.ValidationError("Choose a rating between 1 and 5 stars.")
        return rating
