from django import forms
from .models import CompanyUser

class CompanyUserForm(forms.ModelForm):
    class Meta:
        model = CompanyUser
        fields = [
            'customer_name', 'contact', 'phone_number', 
            'email1', 'email2', 'date_of_registration', 
            'end_of_subscription'
        ]
