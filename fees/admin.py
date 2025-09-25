from django.contrib import admin
from .models import StudentClass, Student, Month, Payment

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'fee_amount']
    search_fields = ['name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'father_name', 'mother_name', 'student_class', 'current_month_status']
    search_fields = ['first_name', 'last_name', 'father_name', 'mother_name']
    list_filter = ['student_class', 'created_at']
    
    def current_month_status(self, obj):
        return obj.current_month_status()
    current_month_status.short_description = 'Current Status'

@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ['month', '__str__']
    search_fields = ['month']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'month', 'amount', 'paid', 'payment_date']
    list_filter = ['month', 'paid', 'payment_date', 'student__student_class']
    search_fields = ['student__first_name', 'student__last_name', 'student__father_name', 'student__mother_name']