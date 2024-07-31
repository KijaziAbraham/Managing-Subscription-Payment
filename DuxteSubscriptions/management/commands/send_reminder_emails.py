from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from DuxteSubscriptions.models import CompanyUser

class Command(BaseCommand):
    help = 'Send reminder emails to users whose subscriptions are about to end.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        two_months_from_now = today + timedelta(days=60)
        follow_up_customers = CompanyUser.objects.filter(
            end_of_subscription__gt=today, 
            end_of_subscription__lte=two_months_from_now
        )

        for customer in follow_up_customers:
            if customer.should_send_reminder():
                self.send_reminder_email(customer)
                customer.last_reminder_sent = today
                customer.reminder_count += 1
                customer.save()

        expired_customers = CompanyUser.objects.filter(end_of_subscription__lte=today)
        for customer in expired_customers:
            if customer.reminder_count == 0:  # Notify only once
                self.send_expired_notification_email(customer)
                customer.reminder_count += 1
                customer.save()

    def send_reminder_email(self, customer):
        subject = 'Your Subscription is Ending Soon'
        message = f"""
        <html>
            <body>
                <p>Dear {customer.customer_name},</p>
                <p>We hope you're enjoying our services. We wanted to remind you that your subscription will end on <strong>{customer.end_of_subscription}</strong>.</p>
                <p>To continue enjoying uninterrupted service, please renew your subscription before the expiration date.</p>
                <p>To renew your subscription, click <a href="your-renewal-link">here</a>.</p>
                <p>If you have any questions or need assistance, feel free to contact our support team.</p>
                <p>Best regards,</p>
                <p>Duxte Ltd</p>
                <hr>
                <p><small>If you have already renewed your subscription, please ignore this email.</small></p>
            </body>
        </html>
        """
        recipient_list = [customer.email1]
        send_mail(subject, '', 'abrahamkijazi01.com', recipient_list, html_message=message)

        self.stdout.write(self.style.SUCCESS(f'Successfully sent reminder email to {customer.email1}'))

    def send_expired_notification_email(self, customer):
        subject = 'Your Subscription Has Expired'
        message = f"""
        <html>
            <body>
                <p>Dear {customer.customer_name},</p>
                <p>We regret to inform you that your subscription expired on <strong>{customer.end_of_subscription}</strong>.</p>
                <p>To renew your subscription and continue enjoying our services, please contact us or click here</a>.</p>
                <p>If you have any questions or need assistance, our support team is here to help.</p>
                <p>Best regards,</p>
                <p>Duxte Ltd</p>
                <hr>
                <p><small>If you have already renewed your subscription, please ignore this email.</small></p>
            </body>
        </html>
        """
        recipient_list = [customer.email1]
        send_mail(subject, '', 'abrahamkijazi01.com', recipient_list, html_message=message)

        self.stdout.write(self.style.SUCCESS(f'Successfully sent expired notification email to {customer.email1}'))
