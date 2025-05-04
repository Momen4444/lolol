from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from accounts.models import *

@login_required
def home(request):
    doctors = Doctor.objects.select_related('user').all()
    
    # Determine user type and get profile info
    context = {
        'doctors': doctors,
    }
    
    if hasattr(request.user, 'patient'):
        context['user_type'] = 'patient'
        context['patient'] = request.user.patient
    elif hasattr(request.user, 'doctor'):
        context['user_type'] = 'doctor'
        context['doctor'] = request.user.doctor
    
    return render(request, 'main/Homepage_copy.html', context)

def logout_view(request):
    logout(request)
    return redirect('/') 

@login_required
def profile_redirect_view(request):
    if hasattr(request.user, 'patient'):
        return redirect('accounts:accounts-patient_profile', request.user.patient.user.id)
    elif hasattr(request.user, 'doctor'):
        return redirect('accounts:accounts-doctor_profile', request.user.doctor.user.id)
    else:
        return redirect('homepage')