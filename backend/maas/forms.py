from django import forms
from .models import *

class ContestForm(forms.Form):
    class Meta:
        model = Contest
        fields = ['name', 'description', 'url', 'is_online', 'config_file']