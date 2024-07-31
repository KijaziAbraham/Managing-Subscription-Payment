from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class Software(models.Model):
    CATEGORY_CHOICES = [
        ('Accounting Package', 'Accounting Package'),
        ('ERP', 'Enterprise Resource Planning (ERP)'),
        ('Payroll', 'Payroll'),
    ]
    
    TYPE_CHOICES = [
        ('Light', 'Light'),
        ('Heavy', 'Heavy'),
        ('Essential', 'Essential'),
        ('Plus', 'Plus'),
        ('Advance', 'Advance'),
        ('Premium', 'Premium'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

class CompanyUser(models.Model):
    last_reminder_sent = models.DateField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    customer_name = models.CharField(
        max_length=255,
        error_messages={
            'max_length': 'Customer name must be 255 characters or fewer.',
            'blank': 'Customer name cannot be blank.',
        }
    )
    contact = models.CharField(
        max_length=255,
        error_messages={
            'max_length': 'Contact must be 255 characters or fewer.',
            'blank': 'Contact cannot be blank.',
        }
    )
    phone_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be exactly 10 digits.',
            ),
        ],
        error_messages={
            'max_length': 'Phone number must be exactly 10 digits.',
            'blank': 'Phone number cannot be blank.',
        }
    )  
    email1 = models.EmailField(
        error_messages={
            'invalid': 'Enter a valid email address.',
            'blank': 'Email cannot be blank.',
        }
    )
    email2 = models.EmailField(
        blank=True, 
        null=True,
        error_messages={
            'invalid': 'Enter a valid email address.',
        }
    )
    date_of_registration = models.DateField(
        error_messages={
            'invalid': 'Enter a valid date.',
            'blank': 'Date of registration cannot be blank.',
        }
    )
    date_of_subscription = models.DateField(
        error_messages={
            'invalid': 'Enter a valid date.',
            'blank': 'Date of subscription cannot be blank.',
        }
    )
    end_of_subscription = models.DateField(
        error_messages={
            'invalid': 'Enter a valid date.',
            'blank': 'End of subscription cannot be blank.',
        }
    )
    is_subscription_valid = models.BooleanField(default=True)
    software = models.ForeignKey(
        Software, 
        on_delete=models.CASCADE, 
        related_name='company_users', 
        null=True, 
        blank=True,
        error_messages={
            'null': 'Software cannot be null.',
        }
    )
    is_active = models.BooleanField(default=True)
    

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
