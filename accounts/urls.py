# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='accounts-register'),
    path('profile/patient/<int:patient_id>/', views.patient_profile, name='accounts-patient_profile'),
    path('profile/doctor/<int:doctor_id>/', views.doctor_profile, name='accounts-doctor_profile'),
    path('profile/admin/', views.admin_profile, name='accounts-admin_profile'),
    path('forgot-password/', views.forgot_password_request, name='accounts-forgot_password'),
    path('verify-code/', views.verify_code, name='accounts-verify_code'),
    path('reset-password/', views.reset_password, name='accounts-reset_password'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify-email'),
]