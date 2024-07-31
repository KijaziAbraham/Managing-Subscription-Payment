from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import BooleanField, Case, Value, When
from django.contrib.auth.forms import AuthenticationForm
from openpyxl.styles import Font, Alignment, PatternFill
from .forms import CompanyUserForm, SoftwareForm
from reportlab.lib.pagesizes import letter
from .models import CompanyUser, Software
from django.http import HttpResponse
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.utils import timezone
from reportlab.lib import colors
from django.urls import reverse
from datetime import timedelta
import openpyxl


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Check for existing company users and software
                if CompanyUser.objects.exists():
                    return redirect('company_user_list')
                elif Software.objects.exists():
                    return redirect('create_company_user')
                else:
                    return redirect('add_software')
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
    if not company_users.exists():
        return redirect('create_company_user')
    return render(request, 'DuxteSubscriptions/company_user_list.html', {'company_users': company_users})

def export_to_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="company_user_list.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,  
        spaceAfter=20
    )
    header_style = ParagraphStyle(
        'Heading4',
        parent=styles['Heading4'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        alignment=1,  
        spaceAfter=10
    )
    normal_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=12
    )

   
    title = Paragraph("Company User List", title_style)
    elements.append(title)

    
    headers = ["#", "Company", "Email", "Subscription Date", "Subscription End", "Status"]
    data = [headers]

    company_users = CompanyUser.objects.all()
    for index, company_user in enumerate(company_users, start=1):
        row = [
            str(index),
            company_user.customer_name,
            company_user.email1,
            company_user.date_of_subscription.strftime('%Y-%m-%d') if company_user.date_of_subscription else '',
            company_user.end_of_subscription.strftime('%Y-%m-%d') if company_user.end_of_subscription else '',
            'Valid' if company_user.is_subscription_valid else 'Expired'
        ]
        data.append(row)

   
    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    return response

def export_to_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="company_user_list.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Company Users'

    # Define header and data styles
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4CAF50', end_color='4CAF50', fill_type='solid')
    alignment = Alignment(horizontal='center', vertical='center')

    # Add headers
    headers = ["#", "Company", "Email", "Subscription Date", "Subscription End", "Status"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = alignment

    # Add data rows
    try:
        for index, company_user in enumerate(CompanyUser.objects.all(), start=1):
            row = [
                index,
                company_user.customer_name,
                company_user.email1,
                company_user.date_of_subscription.strftime('%Y-%m-%d') if company_user.date_of_subscription else '',
                company_user.end_of_subscription.strftime('%Y-%m-%d') if company_user.end_of_subscription else '',
                "Valid" if company_user.is_subscription_valid else "Expired"
            ]
            ws.append(row)

            for cell in ws[index + 1]:
                cell.alignment = alignment

        # Auto-adjust column width
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column name
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

    except Exception as e:
        ws.append(['Error:', str(e)])

    wb.save(response)
    return response

def add_software(request):
    if request.method == 'POST':
        form = SoftwareForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('software_list')  
    else:
        form = SoftwareForm()
    return render(request, 'DuxteSubscriptions/add_software.html', {'form': form})

def software_list(request):
    software_list = Software.objects.all()
    return render(request, 'DuxteSubscriptions/software_list.html', {'software_list': software_list})


def edit_software(request, pk):
    software = get_object_or_404(Software, pk=pk)
    
    if request.method == 'POST':
        form = SoftwareForm(request.POST, instance=software)
        if form.is_valid():
            form.save()
            return redirect('software_list')
    else:
        form = SoftwareForm(instance=software)
    
    return render(request, 'DuxteSubscriptions/edit_software.html', {'form': form})



def toggle_status(request, pk):
    company_user = get_object_or_404(CompanyUser, pk=pk)
    company_user.is_active = not company_user.is_active
    company_user.save()
    return redirect('company_user_list')

def company_user_detail(request, pk):
    company_user = get_object_or_404(CompanyUser, pk=pk)
    return render(request, 'DuxteSubscriptions/company_user_detail.html', {'company_user': company_user})



def update_company_user(request, pk):
    company_user = get_object_or_404(CompanyUser, pk=pk)
    if request.method == 'POST':
        form = CompanyUserForm(request.POST, instance=company_user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            today = timezone.now().date()
            if updated_user.end_of_subscription != company_user.end_of_subscription:
                updated_user.last_reminder_sent = None
                updated_user.reminder_count = 0
                updated_user.last_renewal_date = today
            updated_user.save()
            return redirect('company_user_detail', pk=updated_user.pk)
    else:
        form = CompanyUserForm(instance=company_user)
    return render(request, 'DuxteSubscriptions/update_company_user.html', {'form': form, 'company_user': company_user})



def dashboard(request):
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
    
    context = {
        'follow_up_count': follow_up_count,
        'follow_up_users': follow_up_users,
        'reminder_count': reminder_count,
        'reminders': reminders,
        'active_count': active_count,
        'valid_count': valid_count,
        'expired_count': expired_count,
    }
    return render(request, 'DuxteSubscriptions/dashboard.html', context)





def follow_up_customers(request):
    today = timezone.now().date()
    two_months_from_now = today + timedelta(days=60)
    customers = CompanyUser.objects.filter(end_of_subscription__gt=today, end_of_subscription__lte=two_months_from_now)
    return render(request, 'DuxteSubscriptions/company_user_list.html', {'company_users': customers})

def active_customers(request):
    customers = CompanyUser.objects.filter(is_active=True)
    return render(request, 'DuxteSubscriptions/company_user_list.html', {'company_users': customers})

def valid_customers(request):
    today = timezone.now().date()
    customers = CompanyUser.objects.filter(end_of_subscription__gt=today)
    return render(request, 'DuxteSubscriptions/company_user_list.html', {'company_users': customers})

def expired_customers(request):
    today = timezone.now().date()
    customers = CompanyUser.objects.filter(end_of_subscription__lte=today)
    return render(request, 'DuxteSubscriptions/company_user_list.html', {'company_users': customers})

