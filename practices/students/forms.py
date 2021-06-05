from django import forms
from internship.models import Internship


class InternshipEnrollForm(forms.Form):
    internship = forms.ModelChoiceField(queryset=Internship.objects.all(),
                                        widget=forms.HiddenInput)