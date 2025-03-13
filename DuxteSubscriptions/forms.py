from .models import CompanyUser, Software, SoftwareCategory, SoftwareEdition, SoftwareVersion, Addon,UserCategory
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
 
class CustomUserCreationForm(UserCreationForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=SoftwareCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'categories']

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)  # Add a flag to check if it's an edit form
        super().__init__(*args, **kwargs)

        # If it's an edit form, make username and password fields optional
        if self.is_edit:
            self.fields['username'].required = False
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # If it's an edit form and username is left blank, return the existing username
        if self.is_edit and not username:
            return self.instance.username

        # Check for duplicate usernames, excluding the current user during editing
        if self.is_edit:
            existing_user = User.objects.filter(username=username).exclude(pk=self.instance.pk).first()
        else:
            existing_user = User.objects.filter(username=username).first()

        if existing_user:
            raise forms.ValidationError("A user with that username already exists.")

        return username

    def clean_password2(self):
        # Ensure password fields are filled during editing
        if self.is_edit and not self.cleaned_data.get('password1') and not self.cleaned_data.get('password2'):
            raise forms.ValidationError("Password fields are required during editing.")
        return super().clean_password2()

    def save(self, commit=True):
        user = super().save(commit=False)

        # Only update password if it's provided
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

            # Clear existing categories and assign new ones
            UserCategory.objects.filter(user=user).delete()  # Clear existing categories
            categories = self.cleaned_data['categories']
            for category in categories:
                UserCategory.objects.create(user=user, category=category)  # Assign new categories

        return user
    
class CompanyUserForm(forms.ModelForm):

    software_addons = forms.ModelMultipleChoiceField(
        queryset=Addon.objects.none(),
        widget=forms.CheckboxSelectMultiple,  
        required=False
    )

    class Meta:
        model = CompanyUser
        fields = [
            'customer_name', 'contact', 'customer_account', 'base_serial_number', 
            'phone_number', 'email1', 'email2', 'date_of_registration', 
            'date_of_subscription', 'subscription_duration', 
            'software', 'software_edition', 'software_version', 'software_addons','last_reminder_sent'
            ,'last_renewal_date',
        ]
        widgets = {
            'date_of_registration': forms.DateInput(attrs={'type': 'date'}),
            'date_of_subscription': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['software_edition'].queryset = SoftwareEdition.objects.none()
        self.fields['software_version'].queryset = SoftwareVersion.objects.none()
        self.fields['software_addons'].queryset = Addon.objects.none()

        if 'software' in self.data:
            try:
                software_id = int(self.data.get('software'))
                software_instance = Software.objects.get(id=software_id)

                self.fields['software_edition'].queryset = software_instance.editions.all()
                self.fields['software_version'].queryset = software_instance.versions.all()
                self.fields['software_addons'].queryset = software_instance.addons.all()
            except (ValueError, TypeError, Software.DoesNotExist):
                pass
        elif self.instance.pk:
            software_instance = self.instance.software
            self.fields['software_edition'].queryset = software_instance.editions.all()
            self.fields['software_version'].queryset = software_instance.versions.all()
            self.fields['software_addons'].queryset = software_instance.addons.all()



class SoftwareForm(forms.ModelForm):
    editions = forms.ModelMultipleChoiceField(
        queryset=SoftwareEdition.objects.all(),
        widget=forms.CheckboxSelectMultiple,  
        required=False 
    )
    versions = forms.ModelMultipleChoiceField(
        queryset=SoftwareVersion.objects.all(),
        widget=forms.CheckboxSelectMultiple,  
        required=False  
    )
    addons = forms.ModelMultipleChoiceField(
        queryset=Addon.objects.all(),
        widget=forms.CheckboxSelectMultiple,  
        required=False  
    )

    class Meta:
        model = Software
        fields = ['name', 'category', 'editions', 'versions', 'addons']

    def clean(self):
        cleaned_data = super().clean()
        editions = cleaned_data.get('editions')
        versions = cleaned_data.get('versions')
        addons = cleaned_data.get('addons')

        if not editions:
            self.add_error('editions', 'At least one edition must be selected.')
        if not versions:
            self.add_error('versions', 'At least one version must be selected.')
        if not addons:
            self.add_error('addons', 'At least one addon must be selected.')

        return cleaned_data




class SoftwareCategoryForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        help_text="Enter categories separated by commas.",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter categories separated by commas'}),
    )

    class Meta:
        model = SoftwareCategory
        fields = ['name']

    def clean_name(self):
        categories = self.cleaned_data.get("name", "").strip()
        categories_list = [category.strip() for category in categories.split(',') if category.strip()]
        return ','.join(categories_list) if categories_list else ''


class SoftwareEditionForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        help_text="Enter editions separated by commas.",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter editions separated by commas'}),
    )

    class Meta:
        model = SoftwareEdition
        fields = ['name']

    def clean_name(self):
        editions = self.cleaned_data.get("name", "").strip()
        editions_list = [edition.strip() for edition in editions.split(',') if edition.strip()]
        return ','.join(editions_list) if editions_list else ''


class SoftwareVersionForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        help_text="Enter versions separated by commas.",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter versions separated by commas'}),
    )

    class Meta:
        model = SoftwareVersion
        fields = ['name']

    def clean_name(self):
        versions = self.cleaned_data.get("name", "").strip()
        versions_list = [version.strip() for version in versions.split(',') if version.strip()]
        return ','.join(versions_list) if versions_list else ''

class AddonForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        help_text="Enter addons separated by commas.",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter addons separated by commas'}),
    )

    class Meta:
        model = Addon
        fields = ['name']

    def clean_name(self):
        addons = self.cleaned_data.get("name", "").strip()
        addons_list = [addon.strip() for addon in addons.split(',') if addon.strip()]
        return ','.join(addons_list) if addons_list else ''
    


    
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Your password must be at least 8 characters long and contain letters and numbers.",
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class ImportForm(forms.Form):
    file = forms.FileField(label='Select an Excel file')

class SoftwareImportForm(forms.Form):
    file = forms.FileField(label='Select an Excel file')


class UserCategoryForm(forms.ModelForm):
    class Meta:
        model = UserCategory
        fields = ['category']
    
    def __init__(self, *args, **kwargs):
        # Restrict form usage to staff or superusers
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if not user.is_staff:
            self.fields.pop('category')


