from django import forms
from .models import Software, CompanyUser

class CompanyUserForm(forms.ModelForm):
    software = forms.ModelChoiceField(
        queryset=Software.objects.all(),
        widget=forms.Select(attrs={'placeholder': 'Select Software'}),
        required=False,
    )
    class Meta:
        model = CompanyUser
        fields = ['customer_name', 'contact', 'phone_number', 'email1', 'email2','date_of_registration', 'date_of_subscription', 'end_of_subscription', 'software']


class SoftwareForm(forms.ModelForm):
    class Meta:
        model = Software
        fields = ['name', 'category', 'type']
