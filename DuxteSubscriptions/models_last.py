from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver


class SoftwareCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SoftwareEdition(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SoftwareVersion(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Software(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(SoftwareCategory, on_delete=models.CASCADE)
    editions = models.ManyToManyField(SoftwareEdition)
    versions = models.ManyToManyField(SoftwareVersion)
    addons = models.TextField(blank=True, null=True, help_text="Comma-separated addons.")

    def __str__(self):
        return self.name
    @property
    def edition_list(self):
        return [edition.strip() for edition in (self.editions or '').split(',') if edition.strip()]

    @property
    def version_list(self):
        return [version.strip() for version in (self.versions or '').split(',') if version.strip()]

    @property
    def addon_list(self):
        return [addon.strip() for addon in (self.addons or '').split(',') if addon.strip()]


class CompanyUser(models.Model):
    customer_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    customer_account = models.CharField(max_length=255)
    base_serial_number = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=10, validators=[RegexValidator(regex=r'^\d{10}$', message='Phone number must be 10 digits.')]
    )
    email1 = models.EmailField()
    email2 = models.EmailField(blank=True, null=True)
    date_of_registration = models.DateField()
    date_of_subscription = models.DateField()
    end_of_subscription = models.DateField()
    last_date_of_subscription = models.DateField(null=True, blank=True) 
    is_subscription_valid = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    software = models.ForeignKey(Software, on_delete=models.CASCADE, null=True, blank=True, related_name='company_users')
    software_edition = models.ForeignKey(SoftwareEdition, on_delete=models.CASCADE, null=True, blank=True, related_name='company_users' )
    software_version = models.ForeignKey(SoftwareVersion, on_delete=models.CASCADE, null=True, blank=True, related_name='company_users' )
    software_addon = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of add-ons.")
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_reminder_sent = models.DateField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
   
    @property
    def total_subscription_time(self):
        return (self.end_of_subscription - self.date_of_subscription).days

    @property
    def is_subscription_valid(self):
        return timezone.now().date() < self.end_of_subscription

    def __str__(self):
        return f"{self.customer_name} - {self.contact}"

    def should_send_reminder(self):
        today = timezone.now().date()
        if self.end_of_subscription <= today:
            return self.reminder_count == 0
        if self.last_reminder_sent:
            days_since_last_reminder = (today - self.last_reminder_sent).days
            return days_since_last_reminder >= 5
        return True
    
    def update_subscription_date(self):
            """Update the subscription date if the end date is reached."""
            today = timezone.now().date()
            if self.end_of_subscription == today:
                self.date_of_subscription = self.end_of_subscription
                self.save()

@receiver(post_save, sender=CompanyUser)
def check_subscription_update(sender, instance, **kwargs):
    """Signal to check and update the subscription date after saving."""
    if kwargs.get('created', False): 
        return

    today = timezone.now().date()
    if instance.end_of_subscription == today and instance.date_of_subscription != instance.end_of_subscription:
        CompanyUser.objects.filter(pk=instance.pk).update(date_of_subscription=instance.end_of_subscription)


@receiver(pre_save, sender=CompanyUser)
def update_subscription_dates(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CompanyUser.objects.get(pk=instance.pk)
            if old_instance.end_of_subscription and old_instance.end_of_subscription != instance.end_of_subscription:
                instance.last_date_of_subscription = old_instance.date_of_subscription
                instance.date_of_subscription = old_instance.end_of_subscription
        except CompanyUser.DoesNotExist:
            pass

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'),
        ('RESTORE', 'Restore'), ('IMPORT', 'Import'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_user = models.ForeignKey(CompanyUser, on_delete=models.SET_NULL, null=True, blank=True)
    software = models.ForeignKey(Software, on_delete=models.SET_NULL, null=True, blank=True) 
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.action} by {self.user} on {self.timestamp}"

