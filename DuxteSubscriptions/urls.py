from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_company_user/', views.create_company_user, name='create_company_user'),
    path('company_user_list/', views.company_user_list, name='company_user_list'),
    path('add_software/', views.add_software, name='add_software'),
    path('software_list/', views.software_list, name='software_list'),
    path('export/pdf/', views.export_to_pdf, name='export_to_pdf'),
    path('export/excel/', views.export_to_excel, name='export_to_excel'),
    path('toggle-status/<int:pk>/', views.toggle_status, name='toggle_status'),
    path('company_users/<int:pk>/', views.company_user_detail, name='company_user_detail'),  
    path('company_users/<int:pk>/edit/', views.update_company_user, name='update_company_user'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('follow-up-customers/', views.follow_up_customers, name='follow_up_customers'),
    path('active-customers/', views.active_customers, name='active_customers'),
    path('valid-customers/', views.valid_customers, name='valid_customers'),
    path('expired-customers/', views.expired_customers, name='expired_customers'),
    path('software/edit/<int:pk>/', views.edit_software, name='edit_software'),  



]


