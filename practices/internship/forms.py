from django import forms
from django.forms.models import inlineformset_factory
from .models import Internship, Module


ModuleFormSet = inlineformset_factory(Internship,
                                        Module,
                                        fields=['title', 'description'],
                                        extra=2,
                                        can_delete=True)