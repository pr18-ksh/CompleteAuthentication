from django.contrib import admin
from django.urls import path,include
from api.views import AuthView
from api.views import ResetPasswordView, ResetPasswordConfirmView 
from django.views.generic import TemplateView
from Emp.views import EmpListView




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('Emp.urls')),
    path('auth/', AuthView.as_view(), name='auth'),  
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-confirm/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('password-reset-complete/', TemplateView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
