from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from dateutil.relativedelta import relativedelta  
from django.core.exceptions import ValidationError
import re

def validate_phone_number(phone_number):
    # Strip all non-digit characters (including +, spaces, etc.)
    digits_only = re.sub(r'\D', '', phone_number)

    if not (10 <= len(digits_only) <= 16):
        raise ValidationError(f"Phone number must contain between 10 and 16 digits, after removing non-digit characters. Given: {digits_only} ({len(digits_only)} digits).")

    return digits_only

class SoftwareCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(SoftwareCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
    

class SoftwareEdition(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SoftwareVersion(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Addon(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Software(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(SoftwareCategory, on_delete=models.CASCADE)
    editions = models.ManyToManyField(SoftwareEdition)
    versions = models.ManyToManyField(SoftwareVersion)
    addons = models.ManyToManyField(Addon, related_name='softwares', blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    @property
    def edition_list(self):
        return [edition.name for edition in self.editions.all()]

    @property
    def version_list(self):
        return [version.name for version in self.versions.all()]

    @property
    def addon_list(self):
        return [addon.name.strip() for addon in self.addons.all()]
    

class CompanyUser(models.Model):
    customer_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    customer_account = models.CharField(null=True, blank=True, max_length=255)
    base_serial_number = models.CharField(null=True, blank=True, max_length=255)
    phone_number = models.CharField(
        max_length=16,  
        validators=[validate_phone_number]
    )
    email1 = models.EmailField()
    email2 = models.EmailField(blank=True, null=True)
    date_of_registration = models.DateField()
    date_of_subscription = models.DateField()
    end_of_subscription = models.DateField()
    subscription_duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], 
        help_text="Duration in months (1 to 12 months)."
    )
    is_active = models.BooleanField(default=True)
    software = models.ForeignKey(Software, on_delete=models.CASCADE, null=True, blank=True, related_name='company_users')
    software_edition = models.ForeignKey(
        SoftwareEdition, 
        on_delete=models.CASCADE, 
        null=True, blank=True, related_name='company_users'
    )
    software_version = models.ForeignKey(
        SoftwareVersion, 
        on_delete=models.CASCADE, 
        null=True, blank=True, related_name='company_users'
    )
    software_addons = models.ManyToManyField(Addon, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_reminder_sent = models.DateField(null=True, blank=True)
    last_renewal_date = models.DateField(null=True, blank=True)

    @property
    def subscription_valid(self):
        return timezone.now().date() < self.end_of_subscription

    def __str__(self):
        return f"{self.customer_name} - {self.contact}"



    def should_send_reminder(self):
        """Determine if a reminder should be sent based on the days left in the subscription."""
        today = timezone.now().date()
        days_left = (self.end_of_subscription - today).days
        
        if days_left in [0, 30, 60]:
            if not self.last_reminder_sent or (self.last_reminder_sent != today):
                return True
        return False

    
    def save(self, *args, **kwargs):
        if self.date_of_subscription and self.subscription_duration:
            self.end_of_subscription = self.date_of_subscription + relativedelta(months=self.subscription_duration)
        if self.date_of_subscription > self.end_of_subscription:
            raise ValidationError("End of subscription must be after date of subscription.")
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'),
        ('RESTORE', 'Restore'), ('IMPORT', 'Import'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_user = models.ForeignKey(CompanyUser, on_delete=models.SET_NULL, null=True, blank=True)
    software = models.ForeignKey(Software, on_delete=models.SET_NULL, null=True, blank=True)  # Added for software actions
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.action} by {self.user} on {self.timestamp}"



   