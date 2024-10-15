from django.contrib import admin
from .models import Software, CompanyUser, AuditLog, UserCategory, SoftwareCategory
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone


@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'category',)
    search_fields = ('name',)
    list_filter = ('category',)

   

class SubscriptionExpiredFilter(admin.SimpleListFilter):
    title = 'Subscription Status'
    parameter_name = 'is_subscription_expired'

    def lookups(self, request, model_admin):
        return (
            ('True', 'Valid'),  
            ('False', 'Expired'), 
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(end_of_subscription__gte=timezone.now().date())  
        if self.value() == 'False':
            return queryset.filter(end_of_subscription__lt=timezone.now().date())  
        return queryset

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'email1', 'date_of_registration', 'end_of_subscription', 'subscription_status_display')
    list_filter = (SubscriptionExpiredFilter,) 
    search_fields = ('customer_name', 'email1',)
    list_per_page = 20

    def subscription_status_display(self, obj):
        return "Valid" if obj.end_of_subscription >= timezone.now().date() else "Expired"
    subscription_status_display.short_description = "Subscription Status"


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'company_user', 'timestamp')
    list_filter = ('action', 'user', 'timestamp')
    search_fields = ('details',)
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'user', 'company_user')

admin.site.register(AuditLog, AuditLogAdmin)

admin.site.site_header = "Duxte Subscriptions Administration"
admin.site.site_title = "Duxte Subscriptions Admin Portal"
admin.site.index_title = "Welcome to the Duxte Subscriptions Management Dashboard"


class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'category']


class UserCategoryInline(admin.TabularInline):
    model = UserCategory
    extra = 1  

# Extend the existing User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserCategoryInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
