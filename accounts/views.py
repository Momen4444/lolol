from datetime import date, datetime
import random
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from .models import User, Patient, Doctor, Admin
from .forms import *
import cloudinary
import cloudinary.uploader
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode

User = get_user_model()




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('main:homepage')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')




@transaction.atomic
def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        user_type = request.POST.get('user_type')
        photo = request.FILES.get('photo')

        try:
            with transaction.atomic():
                if user_form.is_valid():
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password1'])
                    user.save()

                    photo_url = ''
                    if photo:
                        try:
                            upload_result = cloudinary.uploader.upload(
                                photo,
                                folder=f"clinic/{user_type.lower()}s/",
                                public_id=f"{user.username}_profile",
                                overwrite=True,
                                resource_type="image",
                                width=300,
                                height=300,
                                crop="fill"
                            )
                            photo_url = upload_result.get('secure_url', '')
                        except Exception as upload_error:
                            messages.error(request, f"Error uploading photo: {str(upload_error)}")
                            return redirect('register')

                    if user_type == 'Patient':
                        patient = Patient.objects.create(
                            user=user,
                            date_of_birth=request.POST.get('date_of_birth'),
                            gender=request.POST.get('gender'),
                            address=request.POST.get('address'),
                            emergency_contact_name=request.POST.get('emergency_contact_name'),
                            emergency_contact_phone=request.POST.get('emergency_contact_phone'),
                            general_medical_history=request.POST.get('general_medical_history', ''),
                            insurance_provider=request.POST.get('insurance_provider', ''),
                            photo=photo_url
                        )
                        messages.success(request, 'Patient account created successfully!')

                    elif user_type == 'Doctor':
                        doctor = Doctor.objects.create(
                            user=user,
                            license_number=request.POST.get('license_number'),
                            specialization=request.POST.get('specialization', 'General'),
                            about=request.POST.get('about', ''),
                            rating=float(request.POST.get('rating', 0.0)),
                            first_visit=float(request.POST.get('fees', 0.0)),
                            follow_up=float(request.POST.get('follow_up_fees', 0.0)),
                            education=request.POST.get('education', ''),
                            experiences=request.POST.get('experiences', ''),
                            photo=photo_url
                        )
                        messages.success(request, 'Doctor account created successfully!')

                    elif user_type == 'Admin':
                        admin = Admin.objects.create(
                            user=user,
                            role=request.POST.get('role'),
                            photo=photo_url
                        )
                        messages.success(request, 'Admin account created successfully!')

                    return redirect('login')

                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")

        except Exception as e:
            messages.error(request, f"An error occurred during registration: {str(e)}")
            return redirect('register')

    else:
        user_form = UserForm()

    return render(request, 'accounts/register.html', {'user_form': user_form})



def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Email verified successfully! Your account is now active.")
        return redirect('home')
    else:
        messages.error(request, "Invalid verification link")
        return redirect('login')




@login_required
def patient_profile(request, patient_id):
    patient = get_object_or_404(Patient.objects.select_related('user'), user_id=patient_id)
    
    if request.user != patient.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this profile.")
        raise PermissionDenied

    if request.method == 'POST':
        patient_form = PatientForm(request.POST, request.FILES, instance=patient)
        user_form = UserUpdateForm(request.POST, instance=patient.user)   
        
        if patient_form.is_valid() and user_form.is_valid():
            user = user_form.save()
            patient_form.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:accounts-patient_profile', patient_id=patient.user.id)
        
        for form in [patient_form, user_form]:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        patient_form = PatientForm(instance=patient)
        user_form = UserUpdateForm(instance=patient.user)
    
    age = calculate_age(patient.date_of_birth) if patient.date_of_birth else None
    
    context = {
        'patient_form': patient_form,
        'user_form': user_form,
        'patient': patient,
        'age': age,
        'appointment_count': patient.appointment_set.count(),
        'prescription_count': patient.prescriptionglasses_set.count(),
    }
    
    return render(request, 'accounts/patient_profile2.html', context)




def calculate_age(birth_date):  
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))




@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect")
        elif new_password != confirm_password:
            messages.error(request, "Passwords don't match")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user) 
            messages.success(request, "Password updated successfully!")
            return redirect('accounts:accounts-patient_profile', patient_id=user.id)
    
    return render(request, 'accounts/change_password.html')





@login_required
def doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.select_related('user'), user_id=doctor_id)
    slots = [{'slot': i, 'start_time': 8 + i - 1, 'end_time': 8 + i} for i in range(1, 9)]
    editable = request.user == doctor.user  

    if request.method == 'POST' and editable:
        if 'photo' in request.FILES:
            try:
                result = cloudinary.uploader.upload(
                    request.FILES['photo'],
                    folder="doctor_photos",
                    public_id=f"doctor_{doctor.user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
                doctor.photo = result['secure_url']
                doctor.save()
                messages.success(request, 'Profile photo updated successfully!')
                return redirect('accounts:accounts-doctor_profile', doctor_id=doctor.user.id)
            except Exception as e:
                messages.error(request, f'Error uploading photo: {str(e)}')
        
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:accounts-doctor_profile', doctor_id=doctor.user.id)
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DoctorForm(instance=doctor)

    return render(request, 'accounts/doctor_profile2.html', {
        'form': form,
        'doctor': doctor,
        'slots': slots,
        'editable': editable
    })




@login_required
def admin_profile(request):
    user = request.user
    admin = get_object_or_404(Admin, user=user)

    if request.method == 'POST':
        form = AdminForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('admin_profile')
    else:
        form = AdminForm(instance=admin)

    return render(request, 'accounts/admin_profile.html', {
        'form': form,
        'admin': admin,
        'user': user
    })





def generate_code():
    return str(random.randint(100000, 999999))




def forgot_password_request(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            code = str(random.randint(100000, 999999))
            request.session['reset_code'] = code
            request.session['reset_email'] = email
            
            send_mail(
                'Password Reset Code',
                f'Your verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Verification code sent to your email.')
            return redirect('verify_code')
    else:
        form = EmailForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})




def verify_code(request):
    if request.method == 'POST':
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            user_code = form.cleaned_data['code']
            stored_code = request.session.get('reset_code')
            
            if user_code == stored_code:
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid verification code.')
    else:
        form = CodeVerificationForm()
    
    return render(request, 'accounts/verify_code.html', {'form': form})




def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = request.session.get('reset_email')
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    
                    request.session.pop('reset_code', None)
                    request.session.pop('reset_email', None)
                    
                    messages.success(request, 'Password has been reset. You can now log in.')
                    return redirect('login')
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
                    return redirect('forgot_password')
    else:
        form = PasswordResetForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})