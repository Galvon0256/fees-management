from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/payment/', views.mark_payment, name='mark_payment'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('logout/', views.custom_logout, name='logout'),
]