from django.contrib import admin
from .models import Software, CompanyUser

@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'type')
    search_fields = ('name',)
    list_filter = ('category', 'type')

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'email1', 'date_of_registration', 'end_of_subscription', 'is_subscription_valid')
    search_fields = ('customer_name', 'email1')
    list_per_page = 25
