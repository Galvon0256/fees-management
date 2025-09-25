from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from fees.views import CustomLoginView  # Import the custom login view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fees/', include('fees.urls')),
    
    # Override the default admin login with our custom login
    path('admin/login/', CustomLoginView.as_view(), name='login'),
    
    # Redirect root to fees dashboard
    path('', RedirectView.as_view(url='/fees/', permanent=False)),
]