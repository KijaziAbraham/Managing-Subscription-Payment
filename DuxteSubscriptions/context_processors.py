from datetime import timedelta
from django.utils import timezone
from .models import CompanyUser, UserCategory
import datetime



def current_year(request):
    return {
        'current_year': datetime.datetime.now().year
    }

def dashboard_data(request):
    today = timezone.now().date()
    two_months_from_now = today + timedelta(days=60)

    if not request.user.is_authenticated:
        return {}  

    if request.user.is_superuser:
        all_users = CompanyUser.objects.filter(deleted_at__isnull=True)
    else:
        user_categories = UserCategory.objects.filter(user=request.user).values_list('category', flat=True)

        all_users = CompanyUser.objects.filter(
            deleted_at__isnull=True,
            software__category__in=user_categories
        )

    follow_up_users = all_users.filter(
        end_of_subscription__gt=today,
        end_of_subscription__lte=two_months_from_now
    )
    follow_up_count = follow_up_users.count()

    reminders = [user for user in all_users if user.should_send_reminder()]
    reminder_count = len(reminders)

    active_count = all_users.filter(is_active=True).count()

    valid_count = all_users.filter(end_of_subscription__gt=today).count()

    expired_count = all_users.filter(end_of_subscription__lte=today).count()

    suspended_count = all_users.filter(is_active=False).count()

    return {
        'follow_up_count': follow_up_count,
        'follow_up_users': follow_up_users,
        'reminder_count': reminder_count,
        'reminders': reminders,
        'active_count': active_count,
        'valid_count': valid_count,
        'expired_count': expired_count,
        'suspended_count': suspended_count,
    }

