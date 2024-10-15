from django.shortcuts import render, redirect
from .forms import CompanyUserForm
from .models import CompanyUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponse


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Use `auth_login` to avoid naming conflict
                return redirect('company_user_list')
    else:
        form = AuthenticationForm()
    return render(request, 'DuxteSubscriptions/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def create_company_user(request):
    if request.method == 'POST':
        form = CompanyUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_user_list')
    else:
        form = CompanyUserForm()
    return render(request, 'DuxteSubscriptions/create_company.html', {'form': form})

def company_user_list(request):
    company_users = CompanyUser.objects.all()
    return render(request, 'DuxteSubscriptions/company_user_list.html', {'company_users': company_users})

