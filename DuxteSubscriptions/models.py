# subscriptions/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class CompanyUser(models.Model):
    customer_name = models.CharField(max_length=255)  
    contact = models.CharField(max_length=255)  
    phone_number = models.CharField(max_length=15)
    email1 = models.EmailField()
    email2 = models.EmailField(blank=True, null=True)
    date_of_registration = models.DateField()
    end_of_subscription = models.DateField()

    @property
    def total_subscription_time(self):
        return (self.end_of_subscription - self.date_of_registration).days

    @property
    def is_subscription_valid(self):
        return timezone.now().date() <= self.end_of_subscription

    def __str__(self):
        return f"{self.customer_name} - {self.contact}"
