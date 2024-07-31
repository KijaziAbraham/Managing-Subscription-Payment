# DuxteSubscriptions/context_processors.py

from datetime import timedelta
from django.utils import timezone
from .models import CompanyUser

def dashboard_context(request):
    today = timezone.now().date()
    two_months_from_now = today + timedelta(days=60)
    
    follow_up_users = CompanyUser.objects.filter(end_of_subscription__gt=today, end_of_subscription__lte=two_months_from_now)
    follow_up_count = follow_up_users.count()
    
    all_users = CompanyUser.objects.all()
    reminders = [user for user in all_users if user.should_send_reminder()]
    reminder_count = len(reminders)
    
    active_count = CompanyUser.objects.filter(is_active=True).count()
    valid_count = CompanyUser.objects.filter(end_of_subscription__gt=today).count()
    expired_count = CompanyUser.objects.filter(end_of_subscription__lte=today).count()
    
    return {
        'follow_up_count': follow_up_count,
        'follow_up_users': follow_up_users,
        'reminder_count': reminder_count,
        'reminders': reminders,
        'active_count': active_count,
        'valid_count': valid_count,
        'expired_count': expired_count,
    }
