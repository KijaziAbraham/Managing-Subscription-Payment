# yourapp/management/commands/send_subscription_reminders.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from DuxteSubscriptions.models import CompanyUser

class Command(BaseCommand):
    help = 'Send subscription reminder emails to companies'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        reminder_dates = [today + timedelta(days=60), today + timedelta(days=55), today + timedelta(days=50)]
        
        users_to_notify = CompanyUser.objects.filter(end_of_subscription__in=reminder_dates)
        
        for user in users_to_notify:
            context = {
                'customer_name': user.customer_name,
                'end_of_subscription': user.end_of_subscription,
            }
            message = render_to_string('emails/subscription_reminder.html', context)
            send_mail(
                'Subscription Reminder',
                message,
                'your_email@example.com',
                [user.email1],
                fail_silently=False,
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully sent reminder emails'))
