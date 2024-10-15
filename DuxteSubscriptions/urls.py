from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view , name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_company_user', views.create_company_user, name='create_company_user'),
    path('company_user_list/', views.company_user_list, name='company_user_list'),
   ]
