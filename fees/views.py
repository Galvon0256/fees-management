from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from .models import Student, Payment, Month, StudentClass

class CustomLoginView(LoginView):
    template_name = 'admin/login.html'
    
    def get_success_url(self):
        # Check if there's a 'next' parameter, otherwise go to dashboard
        next_url = self.request.GET.get('next', '/fees/')
        return next_url

def admin_required(user):
    return user.is_superuser

def check_auth(view_func):
    """Decorator to check authentication and redirect to login if not authenticated"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Redirect to login with next parameter pointing to the intended page
            next_url = request.get_full_path()
            return redirect_to_login(next_url, login_url='/admin/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

def custom_logout(request):
    """Custom logout view that clears session and redirects to login"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    # Redirect to login with next parameter pointing to dashboard
    return redirect('/admin/login/?next=/fees/')

@check_auth
@user_passes_test(admin_required)
def dashboard(request):
    # If user accesses /fees/ but is not authenticated, they'll be redirected to login
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Get current month object
    month_str = f"{current_year}-{current_month:02d}"
    month_obj, created = Month.objects.get_or_create(month=month_str)
    
    # Count paid and unpaid students for current month
    paid_count = Payment.objects.filter(month=month_obj, paid=True).count()
    unpaid_count = Student.objects.count() - paid_count
    
    # Calculate total collected amount
    total_collected = Payment.objects.filter(month=month_obj, paid=True).aggregate(
        Sum('amount')
    )['amount__sum'] or 0
    
    # Get recent payments
    recent_payments = Payment.objects.filter(paid=True).select_related('student', 'month').order_by('-payment_date')[:5]
    
    context = {
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'total_collected': total_collected,
        'current_month': month_obj,
        'recent_payments': recent_payments,
    }
    return render(request, 'fees/dashboard.html', context)

@check_auth
@user_passes_test(admin_required)
def student_list(request):
    students = Student.objects.all().select_related('student_class')
    
    # Get current month
    current_month = timezone.now().month
    current_year = timezone.now().year
    month_str = f"{current_year}-{current_month:02d}"
    
    # Add current month status to each student
    for student in students:
        student.status = student.current_month_status()
    
    context = {
        'students': students,
        'current_month': month_str,
    }
    return render(request, 'fees/student_list.html', context)

@check_auth
@user_passes_test(admin_required)
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    payments = Payment.objects.filter(student=student).select_related('month').order_by('-month__month')
    
    context = {
        'student': student,
        'payments': payments,
    }
    return render(request, 'fees/student_detail.html', context)

@check_auth
@user_passes_test(admin_required)
def mark_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Get or create current month object
    month_str = f"{current_year}-{current_month:02d}"
    month_obj, created = Month.objects.get_or_create(month=month_str)
    
    # Get or create payment record
    payment, created = Payment.objects.get_or_create(
        student=student,
        month=month_obj,
        defaults={'amount': student.fee_amount(), 'created_by': request.user}
    )
    
    if request.method == 'POST':
        # Process form data manually
        amount = request.POST.get('amount')
        paid = request.POST.get('paid') == 'on'
        
        payment.amount = amount
        payment.paid = paid
        payment.created_by = request.user
        
        if paid and not payment.payment_date:
            payment.payment_date = timezone.now()
        elif not paid:
            payment.payment_date = None
            
        payment.save()
        messages.success(request, f'Payment status updated for {student.first_name} {student.last_name}')
        return redirect('fees:student_list')
    
    context = {
        'student': student,
        'payment': payment,
    }
    return render(request, 'fees/payment_form.html', context)

@check_auth
@user_passes_test(admin_required)
def payment_history(request):
    # Get filter parameters
    month_filter = request.GET.get('month')
    status_filter = request.GET.get('status')
    class_filter = request.GET.get('class')
    
    payments = Payment.objects.all().select_related('student', 'month', 'student__student_class')
    
    # Apply filters
    if month_filter:
        payments = payments.filter(month__month=month_filter)
    if status_filter:
        if status_filter == 'paid':
            payments = payments.filter(paid=True)
        elif status_filter == 'unpaid':
            payments = payments.filter(paid=False)
    if class_filter:
        payments = payments.filter(student__student_class_id=class_filter)
    
    # Get all months and classes for filter dropdowns
    months = Month.objects.all().order_by('-month')
    classes = StudentClass.objects.all()
    
    context = {
        'payments': payments,
        'months': months,
        'classes': classes,
        'current_filters': {
            'month': month_filter,
            'status': status_filter,
            'class': class_filter,
        }
    }
    return render(request, 'fees/payment_history.html', context)