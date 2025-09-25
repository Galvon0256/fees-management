from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class StudentClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} (₹{self.fee_amount})"

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100,blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def current_month_status(self):
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Create month string in YYYY-MM format
        month_str = f"{current_year}-{current_month:02d}"
        
        try:
            month_obj = Month.objects.get(month=month_str)
            payment = Payment.objects.filter(student=self, month=month_obj).first()
            return "paid" if payment and payment.paid else "unpaid"
        except (Month.DoesNotExist, Payment.DoesNotExist):
            return "unpaid"
    
    def fee_amount(self):
        return self.student_class.fee_amount

class Month(models.Model):
    month = models.CharField(max_length=7, unique=True)  # Format: YYYY-MM
    
    def __str__(self):
        year, month = self.month.split('-')
        month_name = date(1900, int(month), 1).strftime('%B')
        return f"{month_name} {year}"
    
    class Meta:
        ordering = ['-month']

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'month']
    
    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"{self.student} - {self.month} - {status}"
    
    def save(self, *args, **kwargs):
        if self.paid and not self.payment_date:
            self.payment_date = timezone.now()
        elif not self.paid:
            self.payment_date = None
        super().save(*args, **kwargs)