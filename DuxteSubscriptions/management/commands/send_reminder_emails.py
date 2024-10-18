from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
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
            end_of_subscription__lte=two_months_from_now,
        )

        for customer in follow_up_customers:
            if customer.should_send_reminder():
                self.send_reminder_email(customer)
                customer.last_reminder_sent = today  
                customer.save()
            else:
                
                if not customer.last_reminder_sent:
                    self.send_follow_up_notification_email(customer)
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
        """Send a 60-day reminder email to customers whose subscriptions are about to expire."""
        subject = 'Reminder: Your Subscription is Expiring Soon!'
        message = f"""
        <html>
            <body>
                <p>Greetings from Duxte Limited,</p>
                <p>We hope you’re enjoying your experience with {customer.software}. We wanted to remind you that your subscription will be expiring on <strong>{customer.end_of_subscription}</strong>.</p>
                <p>To continue enjoying uninterrupted service, please consider renewing your subscription before this date. Our sales team will reach out with a quote and payment details.</p>
                <p>If you have any questions or need assistance, feel free to reach out!</p>
                <p>Thank you for being a valued client!</p>
                <p>Kind Regards,</p>
                <p>Duxte Limited</p>
                <p>+255 745 000 555</p>
                <p>biz@duxte.com</p>
                <hr>
                <p><small>If you have already renewed your subscription, please ignore this email.</small></p>
            </body>
        </html>
        """

        self.send_email(customer, subject, message)
        self.stdout.write(self.style.SUCCESS(f'Successfully sent reminder email to {customer.email1}'))

    def send_follow_up_notification_email(self, customer):
        """Send a follow-up notification email to customers who have not received a reminder yet."""
        subject = 'Follow-Up: Your Subscription Status'
        message = f"""
       <html>
            <body>
                <p>Dear {customer.customer_name},</p>
                <p>We hope you’re enjoying your experience with {customer.software}. We wanted to remind you that your subscription will be expiring on <strong>{customer.end_of_subscription}</strong>.</p>
                <p>To continue enjoying uninterrupted service, please consider renewing your subscription before this date. Our sales team will reach out with a quote and payment details.</p>
                <p>If you have any questions or need assistance, feel free to reach out!</p>
                <p>Thank you for being a valued client!</p>
                <p>Kind Regards</p>
                <p>Duxte Limited</p>
                <p>+255 745 000 555</p>
                <p>biz@duxte.com</p>
                <hr>
                <p><small>If you have already renewed your subscription, please ignore this email.</small></p>
            </body>
        </html>
        """

        self.send_email(customer, subject, message)
        self.stdout.write(self.style.SUCCESS(f'Successfully sent follow-up email to {customer.email1}'))

    def send_expired_notification_email(self, customer):
        """Send a final reminder email to notify customers that their subscription is about to cancel."""
        subject = 'Final Reminder: Your Subscription is About to Cancel'
        message = f"""
        <html>
            <body>
                <p>Greetings from Duxte Limited,</p>
                <p>This is a final reminder that your subscription with {customer.software} will be canceled on <strong>{customer.end_of_subscription}</strong> if it’s not renewed. We value your membership and want to ensure you continue to enjoy our services.</p>
                <p>If you’d like to keep your subscription active, please renew it by making payments against the shared quotation.</p>
                <p>If you have any questions or need assistance, don’t hesitate to reach out. We’re here to help!</p>
                <p>Thank you for being a part of our community.</p>
                <p>Kind Regards,</p>
                <p>Duxte Limited</p>
                <p>+255 745 000 555</p>
                <p>biz@duxte.com</p>
                <hr>
                <p><small>If you have already renewed your subscription, please ignore this email.</small></p>
            </body>
        </html>
        """

        self.send_email(customer, subject, message)
        self.stdout.write(self.style.SUCCESS(f'Successfully sent expired notification email to {customer.email1}'))

    def send_email(self, customer, subject, message):
        """Utility method to send an email."""
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

