from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.utils import timezone
from DuxteSubscriptions.models import CompanyUser

class Command(BaseCommand):
    help = 'Send reminder emails to users whose subscriptions are about to end.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        follow_up_customers = CompanyUser.objects.filter(
            end_of_subscription__gt=today,  
            is_subscription_valid=True
        )

        for customer in follow_up_customers:
            if customer.should_send_reminder():
                self.send_reminder_email(customer)
                customer.last_reminder_sent = today
                customer.save()

        expired_customers = CompanyUser.objects.filter(
            end_of_subscription__lte=today  
        )

        for customer in expired_customers:
            if customer.should_send_reminder():
                self.send_expired_notification_email(customer)
                customer.save()

    def send_reminder_email(self, customer):
        """Send an email reminder to customers whose subscriptions are about to expire."""
        subject = 'Your Subscription is Ending Soon'
        message = f"""
        <html>
            <body>
                <p>Dear {customer.customer_name},</p>
                <p>Your subscription will end on <strong>{customer.end_of_subscription}</strong>.</p>
                <p>Please renew your subscription to continue enjoying our services.</p>
                <p>Best regards,</p>
                <p>Duxte Ltd</p>
                <hr>
                <p><small>If you have already renewed your subscription, please ignore this email.</small></p>
            </body>
        </html>
        """

        recipient_list = [customer.email1]
        cc_list = [customer.email2] if customer.email2 else []

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email='abrahamkijazi01.com',
            to=recipient_list,
            cc=cc_list,
        )
        email.content_subtype = 'html' 
        email.send()

        self.stdout.write(self.style.SUCCESS(f'Successfully sent reminder email to {customer.email1}'))

    def send_expired_notification_email(self, customer):
        """Send an email to notify customers that their subscription has expired."""
        subject = 'Your Subscription Has Expired'
        message = f"""
        <html>
            <body>
                <p>Dear {customer.customer_name},</p>
                <p>Your subscription expired on <strong>{customer.end_of_subscription}</strong>.</p>
                <p>Please renew your subscription to continue using our services.</p>
                <p>Best regards,</p>
                <p>Duxte Ltd</p>
                <hr>
                <p><small>If you have already renewed your subscription, please ignore this email.</small></p>
            </body>
        </html>
        """

        recipient_list = [customer.email1]
        cc_list = [customer.email2] if customer.email2 else []

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email='abrahamkijazi01.com',
            to=recipient_list,
            cc=cc_list,
        )
        email.content_subtype = 'html'  
        email.send()

        self.stdout.write(self.style.SUCCESS(f'Successfully sent expired notification email to {customer.email1}'))



